"""Convert .xml/.zip files to OGR format."""

import logging
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

try:
    import fiona
except ImportError:  # pragma: no cover
    fiona = None  # pragma: no cover

from ..parse import Feature
from ..reader import iter_content_xmls
from ..schema import OGR_SCHEMA
from .executor import BaseExecutor

_logger = logging.getLogger(__name__)


def _write_by_fiona(
    features_iter: Iterable[List[Feature]],
    dst_path: Path,
    driver: Optional[str] = None,
) -> Iterable[Tuple[int, int]]:  # (num_files, num_features)
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
    src_paths: List[Path],
    dst_path: Path,
    executor: BaseExecutor,
    driver: Optional[str] = None,
) -> None:
    """Generate OGR file from given XML/ZIP files."""
    features_iter = executor.iter_process(iter_content_xmls(src_paths))

    num_files = 0
    num_features = 0
    for num_files, num_features in _write_by_fiona(
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
    src_paths: List[Path], executor: BaseExecutor
) -> Iterable[Feature]:
    """Iterate features from given XML/ZIP files."""
    features_iter = executor.iter_process(iter_content_xmls(src_paths))
    for features in features_iter:
        yield from features
