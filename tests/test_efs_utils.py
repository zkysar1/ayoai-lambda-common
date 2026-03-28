"""Tests for ayoai_lambda_common.efs_utils — NFS cache invalidation."""

import os
import tempfile

from ayoai_lambda_common.efs_utils import efs_exists


class TestEfsExists:
    def test_existing_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        assert efs_exists(str(f)) is True

    def test_nonexistent_file(self, tmp_path):
        assert efs_exists(str(tmp_path / "nope.txt")) is False

    def test_existing_directory(self, tmp_path):
        d = tmp_path / "subdir"
        d.mkdir()
        assert efs_exists(str(d)) is True

    def test_nonexistent_directory(self, tmp_path):
        assert efs_exists(str(tmp_path / "nodir")) is False

    def test_empty_file(self, tmp_path):
        f = tmp_path / "empty.txt"
        f.write_text("")
        assert efs_exists(str(f)) is True
