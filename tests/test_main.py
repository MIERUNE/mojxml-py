"""Tests for __main__.py."""

from click.testing import CliRunner

from mojxml.__main__ import main


def test_main():
    """Basic run."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "testdata/output.gpkg",
            "testdata/15222-1107-1553.xml",
            "testdata/12103-0400-76.zip",
        ],
    )
    assert result.exit_code == 0
    assert "1052" in result.stdout


def test_main_arbitrary():
    """Run with --arbitrary."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "testdata/output.gpkg",
            "testdata/15222-1107-1553.xml",
            "--arbitrary",
        ],
    )
    assert result.exit_code == 0
    assert "1051" in result.stdout


def test_main_chikugai():
    """Run with --chikugai."""
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "testdata/output.gpkg",
            "testdata/15222-1107-1553.xml",
            "--chikugai",
            "--worker",
            "thread",
        ],
    )
    assert result.exit_code == 0
    assert "1051" in result.stdout
