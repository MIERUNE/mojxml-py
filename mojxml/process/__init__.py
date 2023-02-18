"""Convert .xml/.zip files to OGR format."""

import logging
from pathlib import Path
from typing import Iterable, Optional

try:
    import fiona
except:
    fiona = None

from ..reader import iter_content_xmls
from ..schema import OGR_SCHEMA
from .executor import BaseExecutor
from ..parse import Feature

_logger = logging.getLogger(__name__)


def _write_by_fiona(
    features_iter: Iterable[list[Feature]],
    dst_path: Path,
    driver: Optional[str] = None,
) -> Iterable[tuple[int, int]]:  # (num_files, num_features)
    """WIP"""
    assert fiona, "fiona is not installed"

    with fiona.open(
        dst_path,
        "w",
        driver=driver,
        schema=OGR_SCHEMA,
        crs="EPSG:4326",
    ) as f:
        num_files = 0
        num_features = 0
        for features in features_iter:
            f.writerecords(features)
            num_files += 1
            num_features += len(features)
            yield (num_files, num_features)


def files_to_ogr_file(
    src_paths: list[Path],
    dst_path: Path,
    executor: BaseExecutor,
    driver: Optional[str] = None,
) -> None:
    """WIP"""
    features_iter = executor.iter_process(iter_content_xmls(src_paths))

    num_files = 0
    num_features = 0
    for (num_files, num_features) in _write_by_fiona(
        features_iter,
        dst_path,
        driver=driver,
    ):
        if num_files > 0 and num_files % 10 == 0:
            _logger.info(
                f"{num_files} XML files processed, {num_features} features written"
            )
    _logger.info(f"{num_files} XML files processed, {num_features} features written")


def files_to_feature_iter(
    src_paths: list[Path], executor: BaseExecutor
) -> Iterable[Feature]:
    """WIP"""
    features_iter = executor.iter_process(iter_content_xmls(src_paths))
    for features in features_iter:
        for feature in features:
            yield feature
