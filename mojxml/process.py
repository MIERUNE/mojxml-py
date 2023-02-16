"""ひとまず雑に実装"""

import logging
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable

import fiona

from .mojzip import MojXMLZipFile
from .parse import parse_raw
from .schema import OGR_SCHEMA

_logger = logging.getLogger(__name__)


def process_raw(
    src_iter: Iterable[bytes], dst_path: Path, driver: str | None = None
) -> None:
    """WIP"""
    with fiona.open(
        dst_path,
        "w",
        driver=driver,
        schema=OGR_SCHEMA,
        crs="EPSG:4326",
    ) as f:
        with ProcessPoolExecutor() as executor:
            count = 0
            for features in executor.map(parse_raw, src_iter):
                if count > 0 and count % 10 == 0:
                    _logger.info(f"{count} files processed")
                for feature in features:
                    f.write(feature)  # type: ignore
                count += 1
            _logger.info(f"{count} files processed")


def _iter_content_xml(src_paths: list[Path]) -> Iterable[bytes]:
    """WIP"""
    for src_path in src_paths:
        src_path = Path(src_path)
        if src_path.suffix == ".xml":
            with open(src_path, "rb") as f:
                yield f.read()
        elif src_path.suffix == ".zip":
            with MojXMLZipFile(src_path) as mzf:
                yield from (content for (_, content) in mzf.iter_xml_contents())
        else:
            raise ValueError(f"Unsupported file type: {src_path.suffix}")


def process_file(src_paths: list[Path], dst_path: Path) -> None:
    """WIP"""
    process_raw(_iter_content_xml(src_paths), dst_path)
