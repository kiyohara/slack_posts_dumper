# Slack Posts Dumper

## プロジェクトの目的

このプロジェクトは、Slackの特定チャネルに書き込まれた内容をHTMLとして保存するプログラムです。

### 主な機能
- Slack APIを通じて指定したチャネルのデータを取得
- 取得したデータをSlack上で閲覧している見栄えと同じような内容となるHTMLとして保存
- チャネルの投稿履歴をローカルに保存し、オフラインでも閲覧可能

### 技術要件
- Slack APIを使用したデータ取得
- HTML形式での出力
- Slackの見た目を再現したスタイリング

## 開発環境
- Cursor Editor
- Git によるバージョン管理
- Python 3.13.1 (pyenv管理)
- Poetry (依存関係管理)
- direnv (環境変数管理)

## セットアップ

### 前提条件
- pyenv がインストールされていること
- Python 3.13.1 が pyenv で利用可能であること
- Poetry がインストールされていること
- direnv がインストールされていること

### 環境構築手順

1. **Python環境の設定**
   ```bash
   # プロジェクトディレクトリでPython 3.13.1を設定
   pyenv local 3.13.1
   ```

2. **direnvの設定**
   ```bash
   # direnvを有効化（初回のみ）
   direnv allow
   ```
   
   ※ プロジェクトディレクトリに入ると自動的にPoetry仮想環境が有効化されます

3. **依存関係のインストール**
   ```bash
   poetry install
   ```

4. **環境変数の設定**
   ```bash
   # 環境変数サンプルファイルをコピー
   cp env.example .env
   
   # .envファイルを編集してSlack APIトークンを設定
   # SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   # SLACK_USER_TOKEN=xoxp-your-user-token-here
   ```

## 使用方法
（開発中）

## 開発者向け情報

### 環境変数管理
このプロジェクトでは `direnv` を使用して環境変数を管理しています：

- **自動仮想環境有効化**: プロジェクトディレクトリに入ると自動的にPoetry仮想環境が有効化されます
- **環境変数の読み込み**: `.env` ファイルから環境変数が自動的に読み込まれます
- **プロジェクト固有の環境変数**: `.envrc` ファイルで設定された環境変数が自動的に設定されます

### 環境変数の設定
```bash
# .envファイルを編集
vim .env

# 主な設定項目
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_TOKEN=xoxp-your-user-token-here
OUTPUT_DIR=output
LOG_LEVEL=INFO
DEBUG=False
```

### Poetryコマンド
```bash
# 依存関係のインストール
poetry install

# 新しい依存関係の追加
poetry add パッケージ名

# 開発用依存関係の追加
poetry add --group dev パッケージ名

# 仮想環境内でコマンド実行
poetry run python script.py

# 仮想環境に入る
poetry shell

# 仮想環境から出る
exit
```

### 開発用ツール
```bash
# コードフォーマット
poetry run black .

# リンター
poetry run flake8 .

# テスト実行
poetry run pytest
``` 