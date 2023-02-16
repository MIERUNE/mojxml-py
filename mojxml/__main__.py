"""Command line interface for mojxml"""

import logging
from pathlib import Path

import click

from .process import process_file


@click.command()
@click.argument("dst_file", nargs=1, type=click.Path(dir_okay=False, path_type=Path))
@click.argument(
    "src_files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def main(dst_file: Path, src_files: list[Path]):
    """Convert MoJ XMLs to GeoJSON/GeoPackage/FlatGeobuf/etc.

    DST_FILE: output filename (.geojson, .gpkg, .fgb, etc.)

    SRC_FILES: one or more .xml/.zip files
    """
    # Set up logging
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)

    # Process files
    process_file(src_paths=src_files, dst_path=dst_file)


if __name__ == "__main__":
    main()
