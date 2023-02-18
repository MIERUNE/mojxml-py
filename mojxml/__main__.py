"""Command line interface for mojxml"""

import logging
from pathlib import Path

import click

from .parse import ParseOptions
from .process import files_to_ogr_file
from .process.executor import EXECUTOR_MAP


@click.command()
@click.argument("dst_file", nargs=1, type=click.Path(dir_okay=False, path_type=Path))
@click.argument(
    "src_files",
    nargs=-1,
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--worker",
    type=click.Choice(list(EXECUTOR_MAP.keys())),
    default="multiprocess",
    show_default=True,
)
@click.option(
    "-a",
    "--arbitrary",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include 任意座標系",
)
@click.option(
    "-c",
    "--chikugai",
    is_flag=True,
    show_default=True,
    default=False,
    help="Include 地区外 and 別図",
)
def main(
    dst_file: Path, src_files: list[Path], worker: str, arbitrary: bool, chikugai: bool
) -> None:
    """Convert MoJ XMLs to GeoJSON/GeoPackage/FlatGeobuf/etc.

    DST_FILE: output filename (.geojson, .gpkg, .fgb, etc.)

    SRC_FILES: one or more .xml/.zip files
    """
    # Set up logging
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    options = ParseOptions(
        include_arbitrary_crs=arbitrary,
        include_chikugai=chikugai,
    )
    executor = EXECUTOR_MAP[worker](options)

    # Process files
    files_to_ogr_file(src_paths=src_files, dst_path=dst_file, executor=executor)


if __name__ == "__main__":
    main()
