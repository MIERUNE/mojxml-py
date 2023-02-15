"""ひとまず雑に実装"""

from pathlib import Path

import pyproj
import shapely

try:
    import ujson as json
except ImportError:
    import json

import lxml.etree as et

from .constants import CRS_MAP
from .constants import XML_NAMESPACES as _NS


# TODO: 仮
def process_raw(src_content: bytes, dst_path: str | Path) -> None:
    """TODO:"""
    doc = et.fromstring(src_content, None)

    spatial_elem = doc.find("./空間属性", _NS)

    points = {}
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
                raise ValueError("Unknown tag: {}".format(xy.tag))
        assert x is not None and y is not None
        point_id = point.attrib["id"]
        points[point_id] = (x, y)

    source_crs = CRS_MAP[doc.find("./座標系", _NS).text]
    if source_crs is not None:
        transformer = pyproj.Transformer.from_crs(
            source_crs, "epsg:4326", always_xy=True
        )
    else:
        transformer = None

    curves = {}
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
                    raise ValueError("Unknown tag: {}".format(xy.tag))
        else:
            raise ValueError("Unknown tag: {}".format(pos.tag))

        curve_id = curve.attrib["id"]
        assert x is not None and y is not None
        assert curve_id not in curves

        if transformer:
            (x, y) = transformer.transform(y, x)

        curves[curve_id] = (
            int(x * 1000000000) / 1000000000,
            int(y * 1000000000) / 1000000000,
        )

    surfaces = {}
    for surface in spatial_elem.iterfind("./zmn:GM_Surface", _NS):
        assert surface.find(".//zmn:GM_SurfaceBoundary.exterior", _NS) is not None
        polygons = surface.findall("./zmn:GM_Surface.patch/zmn:GM_Polygon", _NS)
        assert len(polygons) == 1
        polygon = polygons[0]

        surface_id = surface.attrib["id"]
        surface_curves = []
        for cc in polygon.iterfind(".//zmn:GM_CompositeCurve.generator", _NS):
            curve_id = cc.attrib["idref"]
            assert curve_id in curves
            assert surface_id not in surface_curves
            surface_curves.append(curves[curve_id])

        assert surface_id not in surfaces
        assert len(surface_curves) > 0, surface_id
        surface_curves.append(surface_curves[0])
        surfaces[surface_id] = [[surface_curves]]

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

    crs_det_elem = doc.find("./測地系判別", _NS)
    base_props = {
        "地図名": doc.find("./地図名", _NS).text,
        "市区町村コード": doc.find("./市区町村コード", _NS).text,
        "市区町村名": doc.find("./市区町村名", _NS).text,
        "座標系": doc.find("./座標系", _NS).text,
        "測地系判別": crs_det_elem.text if crs_det_elem is not None else None,
    }

    features = []
    for fude in subject_elem.iterfind("./筆", _NS):
        fude_id = fude.attrib["id"]
        properties = {
            "筆ID": fude_id,
        }
        properties.update(base_props)
        geometry = None
        for entry in fude:
            key = entry.tag.split("}")[1]
            if key == "形状":
                coordinates = surfaces[entry.attrib["idref"]]
                geometry = {"type": "MultiPolygon", "coordinates": coordinates}
                rep_point = shapely.MultiPolygon(
                    (p[0], p[1:]) for p in coordinates
                ).point_on_surface()
                properties["代表点経度"] = rep_point.x
                properties["代表点緯度"] = rep_point.y
            else:
                value = entry.text
                properties[key] = value

        features.append(
            {"type": "Feature", "geometry": geometry, "properties": properties}
        )

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }
    with open(dst_path, "w") as f:
        json.dump(geojson, f, ensure_ascii=False)


# TODO: 仮
def process(src_path: str | Path, dst_path: str | Path) -> None:
    """WIP"""
    with open(src_path, "rb") as f:
        src_content = f.read()
        return process_raw(src_content, dst_path)
