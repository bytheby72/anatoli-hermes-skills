"""
Tests for redaction engine.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from redaction import (
    is_secret_filename,
    is_confidential_path,
    redact_env_line,
    safe_read_text,
)


def test_secret_filenames():
    assert is_secret_filename(".env") is True
    assert is_secret_filename("config.yaml") is False
    assert is_secret_filename("token.json") is True
    assert is_secret_filename("my_script.py") is False
    assert is_secret_filename("google_credentials.pem") is True


def test_confidential_paths():
    assert is_confidential_path("/home/user/.env") is True
    assert is_confidential_path("/home/user/projects/app.py") is False
    assert is_confidential_path("/secrets/vault.key") is True
    assert is_confidential_path("/tmp/test.txt") is False


def test_redact_env_line():
    assert redact_env_line("API_KEY=abc123") == "API_KEY=<REDACTED>"
    assert redact_env_line("DEBUG=true") == "DEBUG=true"
    assert redact_env_line("MY_TOKEN=secret") == "MY_TOKEN=<REDACTED>"
    assert redact_env_line("# comment") == "# comment"
    assert redact_env_line("") == ""


def test_safe_read_text_skips_secrets():
    # This test assumes no real secret file exists
    result = safe_read_text("/nonexistent/.env")
    assert result is None


if __name__ == "__main__":
    test_secret_filenames()
    test_confidential_paths()
    test_redact_env_line()
    test_safe_read_text_skips_secrets()
    print("All redaction tests passed.")
