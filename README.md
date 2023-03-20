# mojxml-py

[![Test](https://github.com/MIERUNE/mojxml-py/actions/workflows/test.yml/badge.svg)](https://github.com/MIERUNE/mojxml-py/actions/workflows/test.yml) [![PyPI Package](https://img.shields.io/pypi/v/mojxml?color=%2334D058&label=PyPI%20package)](https://pypi.org/project/mojxml) [![codecov](https://codecov.io/gh/MIERUNE/mojxml-py/branch/main/graph/badge.svg?token=mkeysxV2xy)](https://codecov.io/gh/MIERUNE/mojxml-py)

法務省登記所備付地図データ（地図XML）を各種GISデータ形式 (GeoJSON, GeoPackage, FlatGeobuf, etc.) に変換するコマンドラインツールです。Pythonライブラリとしても使用できます。

A tool for fast conversion of Japanese "MOJ Map XML" (land registration polygons) into geospatial format, written in Python.

特徴：

- デジタル庁のリファレンス実装 ([mojxml2geojson](https://github.com/JDA-DM/mojxml2geojson)) よりも高速に変換できます（XMLパーサとして [lxml](https://github.com/lxml/lxml) (libxml2) を使用しています）。
- XMLファイルだけなく、配布されているZIPファイルをそのまま入力することができます。
- GeoJSON以外の効率的かつコンパクトな形式 (GeoPackage, FlatGeobuf, etc.) でも出力できます。

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

Options:
  --worker [multiprocess|thread|single]
                                  [default: multiprocess]
  -a, --arbitrary                 Include 任意座標系
  -c, --chikugai                  Include 地区外 and 別図
```

- 出力フォーマットは、出力ファイル名の拡張子から自動で判断されます。
- `-a` オプションを指定すると、任意座標系のXMLファイルも変換されます。
- `-c` オプションを指定すると、地番が「地区外」「別図」の地物も出力されます。

### 使用例

```bash
# XMLファイルをGeoJSONに変換する
❯ mojxml2ogr output.geojson 15222-1107-1553.xml

# 複数のXMLファイルを1つのGeoJSONに変換する
❯ mojxml2ogr output.geojson 15222-1107-1553.xml 15222-1107-1554.xml

# 配布用ZIPファイルに含まれる全XMLをFlatGeobufに変換する
❯ mojxml2ogr output.fgb 15222-1107.zip

# 3つのZIPファイルをまとめて1つのFlatGeobufに変換する
❯ mojxml2ogr output.fgb 01202-4400.zip 01236-4400.zip 01337-4400.zip

# ZIPファイルを1段階展開して出てくるZIPファイルも入力できる
❯ mojxml2ogr output.fgb 15222-1107-15*.zip
```

## License

MIT License

### テスト用データについて

[`./testdata/`](./testdata/) に含まれるZIPファイルおよびXMLファイルは、「登記所備付地図データ」（法務省）を、登記所備付地図データ利用規約に基づいて複製したものです。
