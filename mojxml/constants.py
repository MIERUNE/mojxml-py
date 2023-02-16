"""定数値"""

from typing import Optional

XML_NAMESPACES: dict[Optional[str], str] = {
    None: "http://www.moj.go.jp/MINJI/tizuxml",
    "zmn": "http://www.moj.go.jp/MINJI/tizuzumen",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}

CRS_MAP: dict[str, Optional[str]] = {
    "任意座標系": None,
    "公共座標1系": "epsg:2443",
    "公共座標2系": "epsg:2444",
    "公共座標3系": "epsg:2445",
    "公共座標4系": "epsg:2446",
    "公共座標5系": "epsg:2447",
    "公共座標6系": "epsg:2448",
    "公共座標7系": "epsg:2449",
    "公共座標8系": "epsg:2450",
    "公共座標9系": "epsg:2451",
    "公共座標10系": "epsg:2452",
    "公共座標11系": "epsg:2453",
    "公共座標12系": "epsg:2454",
    "公共座標13系": "epsg:2455",
    "公共座標14系": "epsg:2456",
    "公共座標15系": "epsg:2457",
    "公共座標16系": "epsg:2458",
    "公共座標17系": "epsg:2459",
    "公共座標18系": "epsg:2460",
    "公共座標19系": "epsg:2461",
}
