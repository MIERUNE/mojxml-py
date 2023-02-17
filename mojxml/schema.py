"""Schema for OGR"""

from collections import OrderedDict
from typing import TypedDict


class _SchemaType(TypedDict):
    properties: OrderedDict[str, str]
    geometry: str


OGR_SCHEMA: _SchemaType = {
    "properties": OrderedDict(
        [
            ("筆ID", "str"),
            ("地図名", "str"),
            ("市区町村コード", "str"),
            ("市区町村名", "str"),
            ("座標系", "str"),
            ("測地系判別", "str"),
            ("大字コード", "str"),
            ("丁目コード", "str"),
            ("小字コード", "str"),
            ("予備コード", "str"),
            ("大字名", "str"),
            ("丁目名", "str"),
            ("小字名", "str"),
            ("地番", "str"),
            ("筆界未定構成筆", "str"),
            ("代表点経度", "float"),
            ("代表点緯度", "float"),
            ("精度区分", "str"),
            ("座標値種別", "str"),
        ]
    ),
    "geometry": "MultiPolygon",
}
