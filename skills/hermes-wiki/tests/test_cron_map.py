"""
Tests for cron map.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from cron_map import _extract_script_path, _check_script_exists, _assign_risk


def test_extract_script_path():
    assert _extract_script_path("python3 /home/user/script.py") == "/home/user/script.py"
    assert _extract_script_path("bash /opt/app/run.sh") == "/opt/app/run.sh"
    assert _extract_script_path("echo hello") is None


def test_assign_risk():
    assert _assign_risk("echo hello") == "LOW"
    assert _assign_risk("python3 app.py") == "MEDIUM"
    assert _assign_risk("curl https://example.com") == "MEDIUM"
    assert _assign_risk("sudo rm -rf /") == "DANGEROUS"
    assert _assign_risk("systemctl restart service") == "LOW"


if __name__ == "__main__":
    test_extract_script_path()
    test_assign_risk()
    print("All cron map tests passed.")
