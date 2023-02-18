"""xmlおよびzipファイルを透過的に扱う"""

from zipfile import ZipFile
from pathlib import Path
from typing import Iterable


def iter_content_xmls(src_paths: list[Path]) -> Iterable[bytes]:
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


class MojXMLZipFile(ZipFile):
    """法務省登記所備付地図データの多段zip圧縮されたアーカイブを扱う"""

    def iter_xml_contents(self):
        """TODO"""
        for name in self.namelist():
            if name.endswith(".zip"):
                yield self._extract_xml_content(name[:-4])
            elif name.endswith(".xml"):
                yield self.open(name).read()

    def _extract_xml_content(self, internal_name: str) -> bytes:
        """TODO"""
        with self.open(internal_name + ".zip") as f:
            with ZipFile(f) as zf:
                xml_content = zf.open(internal_name + ".xml").read()
                return xml_content
