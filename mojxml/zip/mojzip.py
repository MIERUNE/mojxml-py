"""法務省登記所備付地図データの多段zip圧縮されたZipアーカイブを扱う"""

from typing import Generator
from zipfile import ZipFile


class MojXMLZipFile(ZipFile):
    """法務省登記所備付地図データの多段zip圧縮されたZipアーカイブを扱うためのクラス"""

    def iter_names(self) -> Generator[str, None, None]:
        """TODO"""
        for name in self.namelist():
            if name.endswith(".zip"):
                yield name[:-4]

    def iter_xml_contents(self):
        """TODO"""
        for name in self.iter_names():
            yield self.extract_xml_content(name)

    def extract_xml_content(self, name) -> tuple[str, bytes]:
        """TODO"""
        with self.open(name + ".zip") as f:
            with ZipFile(f) as zf:
                xml_content = zf.open(name + ".xml").read()
                return (name, xml_content)
