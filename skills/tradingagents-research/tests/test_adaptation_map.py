#!/usr/bin/env python3
"""Tests for adaptation_map.py logic."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from adaptation_map import ROLE_MAP, load_scan_data, load_debate_data


def test_role_map_completeness():
    assert "Fundamental Analyst" in ROLE_MAP
    assert "Sentiment Analyst" in ROLE_MAP
    assert "Technical Analyst" in ROLE_MAP
    assert "Risk Manager" in ROLE_MAP
    assert "Moderator" in ROLE_MAP
    assert "Execution" in ROLE_MAP


def test_role_map_has_generic_name():
    for src, mapped in ROLE_MAP.items():
        assert "generic_name" in mapped
        assert len(mapped["generic_name"]) > 0
        assert "function" in mapped
        assert "tools" in mapped
        assert "outputs" in mapped


def test_load_scan_data_missing():
    result = load_scan_data("/nonexistent")
    assert "error" in result


def test_load_debate_data_missing():
    result = load_debate_data()
    assert result == {}


def test_no_real_identifiers_in_roles():
    forbidden = ["IEK", "Tera", "Detector", "Piakhouski", "AVS", "ankron"]
    for src, mapped in ROLE_MAP.items():
        combined = str(mapped)
        for word in forbidden:
            assert word not in combined, f"Forbidden word '{word}' found in role mapping"


if __name__ == "__main__":
    test_role_map_completeness()
    test_role_map_has_generic_name()
    test_load_scan_data_missing()
    test_load_debate_data_missing()
    test_no_real_identifiers_in_roles()
    print("All adaptation_map tests passed.")
