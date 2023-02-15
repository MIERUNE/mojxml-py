"""Command line interface for mojxml"""

import pathlib
import sys

from .process import process

if __name__ == "__main__":
    src_path = pathlib.Path(sys.argv[1])
    dst_path = src_path.with_suffix(".geojson")

    process(src_path, dst_path)
