"""Tests for ayoai_lambda_common.validators — path traversal protection patterns."""

from ayoai_lambda_common.validators import (
    SAFE_KEY_PATTERN,
    SAFE_API_KEY_PATTERN,
    SAFE_VERSION_PATTERN,
    SAFE_EFS_ID_PATTERN,
)


class TestSafeKeyPattern:
    def test_valid_alphanumeric(self):
        assert SAFE_KEY_PATTERN.match("abc123")

    def test_valid_with_hyphens(self):
        assert SAFE_KEY_PATTERN.match("my-server-key")

    def test_valid_with_underscores(self):
        assert SAFE_KEY_PATTERN.match("my_server_key")

    def test_rejects_dots(self):
        assert not SAFE_KEY_PATTERN.match("file.json")

    def test_rejects_dot_dot(self):
        assert not SAFE_KEY_PATTERN.match("..")

    def test_rejects_slashes(self):
        assert not SAFE_KEY_PATTERN.match("path/traversal")

    def test_rejects_backslashes(self):
        assert not SAFE_KEY_PATTERN.match("path\\traversal")

    def test_rejects_spaces(self):
        assert not SAFE_KEY_PATTERN.match("has space")

    def test_rejects_empty(self):
        assert not SAFE_KEY_PATTERN.match("")


class TestSafeApiKeyPattern:
    def test_valid_key(self):
        assert SAFE_API_KEY_PATTERN.match("ayo" + "a" * 32)

    def test_valid_hex_key(self):
        assert SAFE_API_KEY_PATTERN.match("ayo1234567890abcdef1234567890abcdef")

    def test_rejects_wrong_prefix(self):
        assert not SAFE_API_KEY_PATTERN.match("xyz" + "a" * 32)

    def test_rejects_short_key(self):
        assert not SAFE_API_KEY_PATTERN.match("ayo" + "a" * 31)

    def test_rejects_long_key(self):
        assert not SAFE_API_KEY_PATTERN.match("ayo" + "a" * 33)

    def test_rejects_uppercase_hex(self):
        assert not SAFE_API_KEY_PATTERN.match("ayo" + "A" * 32)


class TestSafeVersionPattern:
    def test_semver(self):
        assert SAFE_VERSION_PATTERN.match("1.2.3")

    def test_with_pre_release(self):
        assert SAFE_VERSION_PATTERN.match("1.0.0-beta.1")

    def test_rejects_spaces(self):
        assert not SAFE_VERSION_PATTERN.match("1.0 beta")


class TestSafeEfsIdPattern:
    def test_valid_efs_id(self):
        assert SAFE_EFS_ID_PATTERN.match("fs-0123456789abcdef")

    def test_rejects_without_prefix(self):
        assert not SAFE_EFS_ID_PATTERN.match("0123456789abcdef")
