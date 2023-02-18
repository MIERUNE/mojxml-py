"""Tests for process.py"""

from pathlib import Path

from mojxml.process import files_to_ogr_file
from mojxml.process.executor import ProcessPoolExecutor
from mojxml.parse import ParseOptions


def test_process():
    """とりあえずの雑なテスト"""
    src_path = Path("testdata") / "15222-1107-1553.xml"
    dst_path = src_path.with_suffix(".geojson")

    options = ParseOptions()
    executor = ProcessPoolExecutor(options)
    files_to_ogr_file([src_path], dst_path, executor)
