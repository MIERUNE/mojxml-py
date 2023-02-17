"""Convert .xml/.zip files to OGR format."""

import logging
from pathlib import Path
from typing import Iterable, Optional
from dataclasses import dataclass

import fiona

from ..mojzip import MojXMLZipFile
from ..schema import OGR_SCHEMA
from .executor import (
    BaseExecutor,
    ProcessPoolExecutor,
)

_logger = logging.getLogger(__name__)


@dataclass
class ProcessOptions:
    """Options for processing files"""

    driver: Optional[str] = None
    executor: Optional[BaseExecutor] = None
    include_arbitrary_crs: bool = False
    include_chikugai: bool = False


def process_raw(
    src_iter: Iterable[bytes],
    dst_path: Path,
    driver: Optional[str] = None,
    executor: Optional[BaseExecutor] = None,
    include_arbitrary_crs: bool = False,
    include_chikugai: bool = False,
) -> Iterable[tuple[int, int]]:  # (num_files, num_features)
    """WIP"""
    with fiona.open(
        dst_path,
        "w",
        driver=driver,
        schema=OGR_SCHEMA,
        crs="EPSG:4326",
    ) as f:
        # Use default executor if not specified
        if executor is None:
            executor = ProcessPoolExecutor()

        num_files = 0
        num_features = 0
        for features in executor.process(
            src_iter,
            include_arbitrary_crs=include_arbitrary_crs,
            include_chikugai=include_chikugai,
        ):
            f.writerecords(features)
            num_files += 1
            num_features += len(features)
            yield (num_files, num_features)


def _iter_content_xml(src_paths: list[Path]) -> Iterable[bytes]:
    """WIP"""
    for src_path in src_paths:
        src_path = Path(src_path)
        if src_path.suffix == ".xml":
            with open(src_path, "rb") as f:
                yield f.read()
        elif src_path.suffix == ".zip":
            with MojXMLZipFile(src_path) as mzf:
                yield from mzf.iter_xml_contents()
        else:
            raise ValueError(f"Unsupported file type: {src_path.suffix}")


def process_file(
    src_paths: list[Path], dst_path: Path, options: ProcessOptions
) -> None:
    """WIP"""
    num_files = 0
    num_features = 0

    for (num_files, num_features) in process_raw(
        _iter_content_xml(src_paths),
        dst_path,
        driver=options.driver,
        executor=options.executor,
        include_arbitrary_crs=options.include_arbitrary_crs,
        include_chikugai=options.include_chikugai,
    ):
        if num_files > 0 and num_files % 10 == 0:
            _logger.info(
                f"{num_files} files processed, {num_features} features written"
            )
    _logger.info(f"{num_files} files processed, {num_features} features written")
