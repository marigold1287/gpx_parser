# GPX Utility

このリポジトリは、登山・ハイキング向けにエクスポートした GPX ファイルを整形・加工するための Python スクリプト集です。

主な用途は次のとおりです。

- Yamap などから出力した GPX の時刻をローカルタイムゾーンへ補正する
- GPX のファイル名・タイトルを整理して保存する
- 国土地理院の標高データを使って各ポイントの標高を補正する
- ルートデータを簡単に加工して `output/` 配下に出力する

## 収録スクリプト

### `parse_yamap_gpx.py`
Yamap からエクスポートした GPX を処理します。

- 各ポイントの時刻をローカルタイムゾーンに変換
- CSV ファイル名から日付時刻を抽出
- `YYYY-mm-dd_HH_MM_[活動記録のタイトル].gpx` の形式で保存

例:

```bash
python parse_yamap_gpx.py -f ./resources -o ./output
```

`-f` には入力ファイルまたはディレクトリを指定します。ディレクトリ指定時は `*.gpx` を自動的に処理します。

### `parse_comaps_gpx.py`
Comaps からエクスポートした GPX を編集するためのスクリプトです。

- 位置情報の丸め処理
- 時間間隔に応じたポイントの間引き
- 国土地理院 API を使った標高補正
- 出力ファイル名は元のファイル名をそのまま利用

例:

```bash
python parse_comaps_gpx.py \
  -f ./resources/sample.gpx \
  -o ./output
```


スマホ等で取得したGPSデータは標高精度に欠けている場合が多く、
国土地理院のデータをもとに補正を行います。

YamapはGPSデータ取り込み時にこの補正を実施しているものと思われ、
時間による間引きせず、緯度経度の丸めも行わないで解析をすると
Yamapのデータとほぼ同じになります。

#### オプション

- `--adjust-elevation-accuracy`: 座標丸め精度を指定。小数点以下の桁数で標高補正を行う
- `--time-interval`: 指定秒数ごとにポイントを間引く

### `func.py`
共通処理をまとめたモジュールです。

- GPX ファイルの読み込み
- ローカルタイムゾーン変換
- GPX の時刻抽出
- 標高キャッシュの保存・読み込み
- 国土地理院の標高取得 API 呼び出し

## セットアップ

Python 3.12 で動作を想定しています。

```bash
python -m venv .venv
source .venv/bin/activate
pip install gpxpy requests
```

## 実行例

### Yamap の GPX を正規化

```bash
python parse_yamap_gpx.py -f ./resources -o ./output
```

### Comaps の GPX を標高補正付きで処理

```bash
python parse_comaps_gpx.py -f ./resources -o ./output
```

## 注意事項

- 標高補正は国土地理院 API を利用するため、ネットワーク接続が必要です
- `.cache` に緯度・経度と標高の対応表を保存するため、同じ場所の再取得を高速化できます

## 課題
国土地理院の標高取得APIは1点ごとの取得にしか対応していない。

https://service.gsi.go.jp/kiban/

で標高基盤データを取得してオフライン上で標高を取得できるようにすれば
高速処理できるようになるが未実装です。

