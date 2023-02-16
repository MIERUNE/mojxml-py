"""法務省登記所備付地図データの多段zip圧縮されたアーカイブを扱う"""

from zipfile import ZipFile


class MojXMLZipFile(ZipFile):
    """法務省登記所備付地図データの多段zip圧縮されたアーカイブを扱う"""

    def iter_xml_contents(self):
        """TODO"""
        for name in self.namelist():
            if name.endswith(".zip"):
                yield self._extract_xml_content(name[:-4])
            elif name.endswith(".xml"):
                yield self.open(name).read()

    def _extract_xml_content(self, internal_name: str) -> tuple[str, bytes]:
        """TODO"""
        with self.open(internal_name + ".zip") as f:
            with ZipFile(f) as zf:
                xml_content = zf.open(internal_name + ".xml").read()
                return (internal_name, xml_content)
