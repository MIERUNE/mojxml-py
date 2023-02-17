"""Tests for process.py"""

from pathlib import Path

from mojxml.process import process_file, ProcessOptions


def test_process():
    """とりあえずの雑なテスト"""
    src_path = Path("testdata") / "15222-1107-1553.xml"
    dst_path = src_path.with_suffix(".geojson")

    options = ProcessOptions()
    process_file([src_path], dst_path, options=options)
