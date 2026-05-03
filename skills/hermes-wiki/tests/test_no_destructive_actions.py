"""
Tests verifying no destructive actions in any script.
"""

import ast
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


FORBIDDEN_CALLS = [
    "os.remove",
    "os.rmdir",
    "os.unlink",
    "shutil.rmtree",
    "shutil.rmdir",
    "subprocess.run",
    "subprocess.call",
    "subprocess.Popen",
]


def _scan_for_destructive(filepath: Path) -> list[str]:
    """Scan Python file for destructive function calls."""
    issues = []
    try:
        tree = ast.parse(filepath.read_text(encoding="utf-8"))
    except SyntaxError:
        return issues

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for os.remove, shutil.rmtree, etc.
            if isinstance(node.func, ast.Attribute):
                full = ""
                if isinstance(node.func.value, ast.Name):
                    full = f"{node.func.value.id}.{node.func.attr}"
                elif isinstance(node.func.value, ast.Attribute):
                    # Handle module.submodule.func
                    parts = []
                    n = node.func.value
                    while isinstance(n, ast.Attribute):
                        parts.append(n.attr)
                        n = n.value
                    if isinstance(n, ast.Name):
                        parts.append(n.id)
                    full = ".".join(reversed(parts)) + "." + node.func.attr

                if full in ("os.remove", "os.rmdir", "os.unlink", "shutil.rmtree"):
                    issues.append(f"{full} at line {node.lineno}")

            # Check for subprocess with rm, docker prune, etc.
            if isinstance(node.func, ast.Attribute) and node.func.attr in ("run", "call", "Popen", "check_output"):
                # Check if first arg contains dangerous commands
                if node.args:
                    first_arg = node.args[0]
                    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                        cmd = first_arg.value.lower()
                        if any(d in cmd for d in ["rm -", "docker prune", "journalctl --vacuum", "mkfs"]):
                            issues.append(f"dangerous subprocess '{first_arg.value}' at line {node.lineno}")

    return issues


def test_no_destructive_in_scripts():
    issues = []
    for pyfile in SCRIPTS_DIR.glob("*.py"):
        found = _scan_for_destructive(pyfile)
        if found:
            issues.extend([f"{pyfile.name}: {f}" for f in found])

    if issues:
        print("DESTRUCTIVE ACTIONS FOUND:")
        for i in issues:
            print(f"  - {i}")
        raise AssertionError("Destructive actions detected in scripts!")

    print("No destructive actions found in any script.")


if __name__ == "__main__":
    test_no_destructive_in_scripts()
    print("All no-destructive-action tests passed.")
