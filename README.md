# 棋書ミシュラン スクレイパー

将棋書籍の書評サイト「[棋書ミシュラン](https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/serial-number.htm)」から書評データを抽出するPythonスクリプトです。

## 概要

このスクリプトは、「棋書ミシュラン」サイトから各書籍レビューページにアクセスし、以下の情報を抽出してTSV形式で保存します：

- 書名
- 著者
- 総合評価
- 戦法分類（居飛車、振り飛車、四間飛車、三間飛車、中飛車、角換わり、横歩取り）
- 発行年月
- レビューページURL

## 必要条件

- Python 3.6以上
- 以下のPythonパッケージ:
  - requests
  - beautifulsoup4

## インストール

依存パッケージのインストール:

```bash
pip install requests beautifulsoup4
```

## 使用方法

スクリプトを実行するには:

```bash
python kisho_michelin.py
```

実行すると、カレントディレクトリに `kisho_reviews.tsv` ファイルが生成されます。

## 出力形式

出力されるTSVファイルは以下の列を含みます:

| 書名 | 総合評価 | 戦法 | 著者 | 発行年月 |
|------|----------|------|------|----------|

書名はハイパーリンクとしてフォーマットされており、Excelで開くと元のレビューページにジャンプできます。

## 特徴

- サーバー負荷を考慮した遅延機能（デフォルト1.2秒）
- 詳細なロギング
- 複数のHTMLパターンに対応した堅牢な抽出ロジック
- エラーハンドリングとリカバリーのサポート

## カスタマイズ

スクリプト内の以下の定数を変更することで、動作をカスタマイズできます:

```python
BASE_URL = "https://rocky-and-hopper.sakura.ne.jp/Kisho-Michelin/serial-number.htm"
OUTPUT_FILE = "kisho_reviews.tsv"
REQUEST_DELAY = 1.2  # スクレイピング間隔（秒）
ENCODING = "shift_jis"  # サイトのエンコーディング

# 抽出対象の戦法リスト
STRATEGY_PATTERNS = ["居飛車", "振り飛車", "四間飛車", "三間飛車", "中飛車", "角換わり", "横歩取り"]
```

## 注意事項

Webスクレイピングはサイト所有者のサーバーに負荷をかける可能性があります。個人研究や非商用目的に限って使用し、適切な間隔（REQUEST_DELAY）を設定してください。

## ライセンス

MITライセンス