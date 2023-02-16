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


def process_raw(src_iter: Iterable[bytes], dst_path: str | Path) -> None:
    """WIP"""
    dst_path = Path(dst_path)
    with fiona.open(
        dst_path.with_suffix(".geojson"),
        "w",
        driver="GeoJSON",
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


def process_xml(src_path: str | Path, dst_path: str | Path) -> None:
    """WIP"""
    src_path = Path(src_path)
    with open(src_path, "rb") as f:
        src_content = f.read()
        return process_raw([src_content], dst_path)


def process_zip(src_path: str | Path, dst_path: str | Path) -> None:
    """WIP"""
    src_path = Path(src_path)
    with MojXMLZipFile(src_path) as mzf:
        process_raw((content for (_, content) in mzf.iter_xml_contents()), dst_path)


def process_file(src_path: str | Path, dst_path: str | Path) -> None:
    """WIP"""
    src_path = Path(src_path)

    if src_path.suffix == ".xml":
        process_xml(src_path, dst_path)
    elif src_path.suffix == ".zip":
        process_zip(src_path, dst_path)
    else:
        raise ValueError(f"Unsupported file type: {src_path.suffix}")
