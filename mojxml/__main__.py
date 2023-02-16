"""Command line interface for mojxml"""

import logging
import pathlib
import sys

from .process import process_file

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    src_path = pathlib.Path(sys.argv[1])
    dst_path = src_path.with_suffix(".geojson")
    process_file(src_path, dst_path)
