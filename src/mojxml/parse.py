"""Parse MOJ MAP XML files"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, TypedDict

import lxml.etree as et
import pyproj

from .constants import CRS_MAP
from .constants import XML_NAMESPACES as _NS

Point = Tuple[float, float]
Curve = Tuple[float, float]
Surface = List[List[List[Tuple[float, float]]]]


@dataclass
class ParseOptions:
    """Options for parsing XMLs"""

    include_arbitrary_crs: bool = False
    include_chikugai: bool = False


class Feature(TypedDict):
    """GeoJSON-like feature representation"""

    type: str
    geometry: Dict[str, list]
    properties: Dict[str, object]


def _parse_base_properties(root: et._Element) -> Dict[str, object]:
    crs_det_elem = root.find("./測地系判別", _NS)
    return {
        "地図名": root.find("./地図名", _NS).text,
        "市区町村コード": root.find("./市区町村コード", _NS).text,
        "市区町村名": root.find("./市区町村名", _NS).text,
        "座標系": root.find("./座標系", _NS).text,
        "測地系判別": crs_det_elem.text if crs_det_elem is not None else None,
    }


def _parse_points(spatial_elem: et._Element) -> Dict[str, Point]:
    points: Dict[str, Point] = {}
    for point in spatial_elem.iterfind("./zmn:GM_Point", _NS):
        pos = point.find(".//zmn:DirectPosition", _NS)
        x = None
        y = None
        for xy in pos:
            if xy.tag == "{http://www.moj.go.jp/MINJI/tizuzumen}X":
                x = float(xy.text)
            elif xy.tag == "{http://www.moj.go.jp/MINJI/tizuzumen}Y":
                y = float(xy.text)
            else:
                raise ValueError(f"Unknown tag: {xy.tag}")  # pragma: no cover
        assert x is not None and y is not None
        point_id = point.attrib["id"]
        points[point_id] = (x, y)

    return points


def _parse_curves(
    spatial_elem: et._Element, points: Dict[str, Point]
) -> Dict[str, Curve]:
    curves: Dict[str, Curve] = {}
    for curve in spatial_elem.iterfind("./zmn:GM_Curve", _NS):
        segments = curve.findall("./zmn:GM_Curve.segment", _NS)
        assert len(segments) == 1
        segment = segments[0]

        columns = segment.findall(".//zmn:GM_PointArray.column", _NS)
        assert len(columns) == 2
        column = columns[0]
        assert len(column) == 1
        pos = column[0]
        x = None
        y = None
        if pos.tag == "{http://www.moj.go.jp/MINJI/tizuzumen}GM_Position.indirect":
            ref = pos[0]
            idref = ref.attrib["idref"]
            (x, y) = points[idref]
        elif pos.tag == "{http://www.moj.go.jp/MINJI/tizuzumen}GM_Position.direct":
            for xy in pos:
                if xy.tag == "{http://www.moj.go.jp/MINJI/tizuzumen}X":
                    x = float(xy.text)
                elif xy.tag == "{http://www.moj.go.jp/MINJI/tizuzumen}Y":
                    y = float(xy.text)
                else:
                    raise ValueError(f"Unknown tag: {xy.tag}")  # pragma: no cover
        else:
            raise ValueError(f"Unknown tag: {pos.tag}")  # pragma: no cover

        curve_id = curve.attrib["id"]
        assert x is not None and y is not None

        curves[curve_id] = (y, x)

    return curves


def _parse_surfaces(
    spatial_elem: et._Element, curves: Dict[str, Curve]
) -> Dict[str, Surface]:
    surfaces: Dict[str, Surface] = {}
    for surface in spatial_elem.iterfind("./zmn:GM_Surface", _NS):
        polygons = surface.findall("./zmn:GM_Surface.patch/zmn:GM_Polygon", _NS)
        assert len(polygons) == 1
        polygon = polygons[0]
        surface_id = surface.attrib["id"]
        rings: list[list[tuple[float, float]]] = []

        exterior = polygon.find(".//zmn:GM_SurfaceBoundary.exterior", _NS)
        ring: list[tuple[float, float]] = []
        for cc in exterior.find(".//zmn:GM_Ring", _NS):
            curve_id = cc.attrib["idref"]
            assert curve_id in curves
            ring.append(curves[curve_id])
        ring.append(ring[0])
        rings.append(ring)

        for interior in polygon.iterfind(".//zmn:GM_SurfaceBoundary.interior", _NS):
            ring: list[tuple[float, float]] = []
            for cc in interior.find(".//zmn:GM_Ring", _NS):
                curve_id = cc.attrib["idref"]
                assert curve_id in curves
                ring.append(curves[curve_id])
            ring.append(ring[0])
            rings.append(ring)

        assert surface_id not in surfaces
        surfaces[surface_id] = [rings]

    return surfaces


def _parse_features(
    subject_elem: et._Element, surfaces: Dict[str, Surface], include_chikugai: bool
) -> List[Feature]:
    features = []
    for fude in subject_elem.iterfind("./筆", _NS):
        fude_id = fude.attrib["id"]
        properties = {
            "筆ID": fude_id,
            "精度区分": None,
            "大字コード": None,
            "丁目コード": None,
            "小字コード": None,
            "予備コード": None,
            "大字名": None,
            "丁目名": None,
            "小字名": None,
            "予備名": None,
            "地番": None,
            "座標値種別": None,
            "筆界未定構成筆": None,
            "地図名": None,
            "市区町村コード": None,
            "市区町村名": None,
            "座標系": None,
            "測地系判別": None,
        }
        geometry = None
        for entry in fude:
            key = entry.tag.split("}")[1]
            if key == "形状":
                coordinates = surfaces[entry.attrib["idref"]]
                geometry = {"type": "MultiPolygon", "coordinates": coordinates}
            else:
                value = entry.text
                properties[key] = value

        if not include_chikugai:
            # 地番が地区外や別図の場合はスキップする
            chiban = properties.get("地番", "")
            if "地区外" in chiban or "別図" in chiban:
                continue

        features.append(
            {"type": "Feature", "geometry": geometry, "properties": properties}
        )

    return features


def parse_raw(content: bytes, options: ParseOptions) -> List[Feature]:
    """Parse raw XML content and get a list of features."""
    doc = et.fromstring(content, None)

    # このファイルの座標参照系を取得する
    source_crs = CRS_MAP[doc.find("./座標系", _NS).text]
    if (not options.include_arbitrary_crs) and source_crs is None:
        return []

    spatial_elem = doc.find("./空間属性", _NS)
    points = _parse_points(spatial_elem)
    curves = _parse_curves(spatial_elem, points)

    # 平面直角座標系を WGS84 に変換する
    if source_crs is not None:
        transformer = pyproj.Transformer.from_crs(
            source_crs, "epsg:4326", always_xy=True
        )
        curve_ids: list[str] = []
        xx: list[float] = []
        yy: list[float] = []
        for curve_id, (x, y) in curves.items():
            curve_ids.append(curve_id)
            xx.append(x)
            yy.append(y)
        (xx, yy) = transformer.transform(xx, yy)
        for curve_id, x, y in zip(curve_ids, xx, yy):
            curves[curve_id] = (x, y)

    # 小数点以下9ケタに丸める
    for curve_id, (x, y) in curves.items():
        curves[curve_id] = (
            int(x * 1000000000) / 1000000000,
            int(y * 1000000000) / 1000000000,
        )

    surfaces = _parse_surfaces(spatial_elem, curves)

    # Note: 図郭についてはひとまず扱わないことにする。
    # デジタル庁の実装は筆に図郭の情報を付与しているのものの、
    # これは筆に複数の図郭が結びつく場合に問題があるように思う
    #
    # fude_to_zukakus = {}
    # for zk in doc.iterfind(".//図郭", _NS):
    #     zukaku = {
    #         "地図番号": zk.find("地図番号", _NS).text,
    #         "縮尺分母": zk.find("縮尺分母", _NS).text,
    #     }
    #     for fude_ref in zk.iterfind("筆参照", _NS):
    #         fude_id = fude_ref.get("idref")
    #         assert fude_id not in fude_to_zukakus
    #         fude_to_zukakus[fude_id] = zukaku

    subject_elem = doc.find("./主題属性", _NS)
    features = _parse_features(
        subject_elem, surfaces, include_chikugai=options.include_chikugai
    )

    # XMLのルート要素にある属性情報をFeatureのプロパティに追加する
    base_props = _parse_base_properties(doc)
    for feature in features:
        feature["properties"].update(base_props)

    return features
