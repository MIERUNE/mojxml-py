"""Tests for reader.py"""

from pathlib import Path

import pytest

from mojxml.reader import iter_content_xmls


def test_reader():
    """Test content reader"""
    with pytest.raises(ValueError):
        src_path = Path("testdata") / "foobar.png"  # invalid extension
        for _ in iter_content_xmls([src_path]):
            pass
