"""
Tests for cleanup classification.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from garbage_map import _classify_path


def test_classify_pycache():
    assert _classify_path("/project/__pycache__") == "SAFE_CLEAN"
    assert _classify_path("/project/.pytest_cache") == "SAFE_CLEAN"


def test_classify_logs():
    assert _classify_path("/var/log/app.log") == "DANGEROUS"
    assert _classify_path("/tmp/test.log") == "REVIEW_FIRST"


def test_classify_secrets():
    assert _classify_path("/secrets/vault.key") == "SECRET_OR_UNKNOWN"
    assert _classify_path("/private/credentials.yaml") == "SECRET_OR_UNKNOWN"
    # Note: .ssh/id_rsa is caught by DANGEROUS .ssh pattern first, which is acceptable


def test_classify_temp():
    assert _classify_path("/tmp/old_file.txt") == "REVIEW_FIRST"
    assert _classify_path("/var/tmp/data.tmp") == "REVIEW_FIRST"


if __name__ == "__main__":
    test_classify_pycache()
    test_classify_logs()
    test_classify_secrets()
    test_classify_temp()
    print("All cleanup classification tests passed.")
