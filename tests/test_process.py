"""Tests for process.py"""

from pathlib import Path

from mojxml.parse import ParseOptions
from mojxml.process import files_to_feature_iter, files_to_ogr_file
from mojxml.process.executor import (
    ProcessPoolExecutor,
    SingleThreadExecutor,
    ThreadPoolExecutor,
)

_FILENAMES = {
    "12103-0400.zip": {
        "count": 3371,
    },
    "15222-1107-1553.xml": {
        "count": 1051,
    },
    "12103-0400-76.zip": {
        "count": 1,
    },
}


def test_process():
    """Run process"""
    for filename in _FILENAMES:
        src_path = Path("testdata") / filename
        dst_path = src_path.with_suffix(".geojson")
        options = ParseOptions()
        executor = ProcessPoolExecutor(options)
        files_to_ogr_file([src_path], dst_path, executor)


def test_executors():
    """Test several executors"""
    for executor_cls in [ThreadPoolExecutor, SingleThreadExecutor]:
        src_path = Path("testdata") / "15222-1107-1553.xml"
        dst_path = src_path.with_suffix(".geojson")
        options = ParseOptions()
        executor = executor_cls(options)
        files_to_ogr_file([src_path], dst_path, executor)


def test_iter_features():
    """Test iter_features"""
    for filename, props in _FILENAMES.items():
        src_path = Path("testdata") / filename

        options = ParseOptions()
        executor = ProcessPoolExecutor(options)
        count = 0
        for _ in files_to_feature_iter([src_path], executor):
            count += 1
        assert count == props["count"]


def test_iter_features_arbitrary():
    """Test iter_features with the arbitrary option"""
    filename = "12103-0400.zip"
    src_path = Path("testdata") / filename

    options = ParseOptions(include_arbitrary_crs=True)
    executor = ProcessPoolExecutor(options)
    count = 0
    for _ in files_to_feature_iter([src_path], executor):
        count += 1
    assert count == 71073


def test_iter_features_chikugai():
    """Test iter_features with the chikugai option"""
    filename = "12103-0400.zip"
    src_path = Path("testdata") / filename

    options = ParseOptions(include_chikugai=True, include_arbitrary_crs=True)
    executor = ProcessPoolExecutor(options)
    count = 0
    found_chikugai = False
    for feature in files_to_feature_iter([src_path], executor):
        count += 1
        chiban = str(feature["properties"]["地番"])
        if "地区外" in chiban or "別図" in chiban:
            found_chikugai = True
    assert count == 71103
    assert found_chikugai
