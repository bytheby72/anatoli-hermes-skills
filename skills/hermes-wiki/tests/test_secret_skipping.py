"""
Tests for secret file skipping.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from redaction import is_secret_filename, safe_read_text


def test_skips_env_files():
    assert is_secret_filename(".env") is True
    assert is_secret_filename(".env.local") is True
    assert is_secret_filename("production.env") is True


def test_skips_token_files():
    assert is_secret_filename("token.json") is True
    assert is_secret_filename("refresh_token.txt") is True
    assert is_secret_filename("api_token.py") is True


def test_skips_key_files():
    assert is_secret_filename("id_rsa") is True
    assert is_secret_filename("id_ed25519") is True
    assert is_secret_filename("server.pem") is True
    assert is_secret_filename("client.p12") is True


def test_allows_normal_files():
    assert is_secret_filename("scanner.py") is False
    assert is_secret_filename("README.md") is False
    assert is_secret_filename("config.yaml") is False
    assert is_secret_filename("test_utils.py") is False


if __name__ == "__main__":
    test_skips_env_files()
    test_skips_token_files()
    test_skips_key_files()
    test_allows_normal_files()
    print("All secret skipping tests passed.")
