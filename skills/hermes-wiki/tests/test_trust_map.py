"""
Tests for trust map.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from trust_map import TrustEntry, _classify_risk


def test_classify_risk():
    # Secret/unknown
    e = TrustEntry(file="test.py", can_handle_secrets=True, can_call_network=True)
    assert _classify_risk(e) == "CRITICAL"

    # High: file read + network
    e = TrustEntry(file="test.py", can_read_files=True, can_call_network=True)
    assert _classify_risk(e) == "HIGH"

    # High: google access
    e = TrustEntry(file="test.py", can_call_google=True)
    assert _classify_risk(e) == "HIGH"

    # Medium: write only
    e = TrustEntry(file="test.py", can_write_files=True)
    assert _classify_risk(e) == "MEDIUM"

    # Low: read only
    e = TrustEntry(file="test.py", can_read_files=True)
    assert _classify_risk(e) == "LOW"

    # Low: nothing
    e = TrustEntry(file="test.py")
    assert _classify_risk(e) == "LOW"


if __name__ == "__main__":
    test_classify_risk()
    print("All trust map tests passed.")
