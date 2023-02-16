"""Command line interface for mojxml"""

import logging
from pathlib import Path

import click

from .process import process_file


@click.command()
@click.argument("output_file", nargs=1, type=click.Path(dir_okay=False, path_type=Path))
@click.argument(
    "input_files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def main(output_file: Path, input_files: list[Path]):
    """Convert MoJ XMLs to GeoJSON/GeoPackage/FlatGeobuf/etc.

    OUTPUT_FILE: Output file (.geojson, .gpkg, .fgb, etc.)

    INPUT_FILES: Input .xml or .zip files
    """
    logging.basicConfig(level=logging.INFO)

    process_file(src_paths=input_files, dst_path=output_file)


if __name__ == "__main__":
    main()
