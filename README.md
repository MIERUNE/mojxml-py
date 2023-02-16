# mojxml-py

[![Test](https://github.com/MIERUNE/mojxml-py/actions/workflows/test.yaml/badge.svg)](https://github.com/MIERUNE/mojxml-py/actions/workflows/test.yaml)

法務省登記所備付地図データ（地図XML）を各種形式 (GeoJSON, GeoPackage, FlatGeobuf, etc.) に変換するPythonライブラリ、およびコマンドラインインタフェースです。

## インストール

```
pip3 install mojxml
```

## コマンドラインインタフェース

```bash
❯ mojxml2ogr --help
Usage: mojxml2ogr [OPTIONS] OUTPUT_FILE INPUT_FILES...

  Convert MoJ XMLs to GeoJSON/GeoPackage/FlatGeobuf/etc.

  OUTPUT_FILE: Output file (.geojson, .gpkg, .fgb, etc.)

  INPUT_FILES: Input .xml or .zip files
```

### 使用例

```bash
# XMLファイルをGeoJSONに変換
❯ mojxml2ogr output.geojson 15222-1107-1553.xml

# 複数のXMLファイルを1つのGeoJSONに変換
❯ mojxml2ogr output.geojson 15222-1107-1553.xml 15222-1107-1554.xml

# 配布されているZipファイルに含まれる全XMLをFlatGeobufに変換
❯ mojxml2ogr output.fgb 15222-1107.zip
```
