# mojxml-py

[![Test](https://github.com/MIERUNE/mojxml-py/actions/workflows/test.yaml/badge.svg)](https://github.com/MIERUNE/mojxml-py/actions/workflows/test.yaml) [![PyPI Package](https://img.shields.io/pypi/v/mojxml?color=%2334D058&label=PyPI%20package)](https://pypi.org/project/mojxml)

法務省登記所備付地図データ（地図XML）を各種GISデータ形式 (GeoJSON, GeoPackage, FlatGeobuf, etc.) に変換するコマンドラインツールです。地図XMLを読み込むためのPythonライブラリとしても使用できます。

## インストール

Ubuntu/Debian:

```bash
apt install libgdal-dev
pip3 install mojxml
```

macOS (Homebrew):

```bash
brew install gdal
pip3 install mojxml
```

## コマンドラインインタフェース

```
Usage: mojxml2ogr [OPTIONS] DST_FILE SRC_FILES...

  Convert MoJ XMLs to GeoJSON/GeoPackage/FlatGeobuf/etc.

  DST_FILE: output filename (.geojson, .gpkg, .fgb, etc.)

  SRC_FILES: one or more .xml/.zip files
```

### 使用例

- 出力形式は拡張子で判断されます。
- 任意座標系のXMLファイルは無視します（今後オプションを追加）。

```bash
# XMLファイルをGeoJSONに変換
❯ mojxml2ogr output.geojson 15222-1107-1553.xml

# 複数のXMLファイルを1つのGeoJSONに変換
❯ mojxml2ogr output.geojson 15222-1107-1553.xml 15222-1107-1554.xml

# 配布用zipファイルに含まれる全XMLをFlatGeobufに変換
❯ mojxml2ogr output.fgb 15222-1107.zip

# 3つのzipファイルをまとめて1つのFlatGeobufに変換
❯ mojxml2ogr output.fgb 01202-4400.zip 01236-4400.zip 01337-4400.zip

# zipファイルを1段階展開して出てくる.zipファイルのうち100個をFlatGeobufに変換
❯ mojxml2ogr output.fgb 15222-1107-15*.zip
```
