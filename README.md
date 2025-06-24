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
   pyenv local 3.13.1
   ```

2. **direnvの設定**
   ```bash
   direnv allow
   ```
   ※ プロジェクトディレクトリに入ると自動的にPoetry仮想環境が有効化されます

3. **依存関係のインストール**
   ```bash
   poetry install
   ```

4. **環境変数の設定**
   ```bash
   cp env.example .env
   # .envファイルを編集してSlack APIトークンやチャネルID等を設定
   # SLACK_BOT_TOKEN=xoxb-your-bot-token-here
   # SLACK_USER_TOKEN=xoxp-your-user-token-here
   # SLACK_WORKSPACE_ID=T1234567890
   # SLACK_CHANNEL_ID=C1234567890
   ```

## 使い方

### Slack API接続確認プログラム

Slack APIとの接続や環境変数の設定が正しいかを確認するためのチェックプログラムが用意されています。

#### 実行例
```bash
# 環境変数の値を利用
python scripts/check_slack_api.py

# コマンドライン引数で上書き
python scripts/check_slack_api.py --workspace-id T9876543210 --channel-id C9876543210

# 詳細ログ出力
python scripts/check_slack_api.py --verbose
```

#### オプション
- `--workspace-id` : ワークスペースID（引数があれば優先、なければ環境変数SLACK_WORKSPACE_ID）
- `--channel-id`   : チャネルID（引数があれば優先、なければ環境変数SLACK_CHANNEL_ID）
- `--verbose, -v`  : 詳細ログ出力

#### 出力例
- Slack API接続の成否
- 取得した最新メッセージの内容（タイムスタンプ、ユーザー、本文）
- エラー時はエラーメッセージ

### .env 設定例
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_USER_TOKEN=xoxp-your-user-token-here
SLACK_WORKSPACE_ID=T1234567890
SLACK_CHANNEL_ID=C1234567890
OUTPUT_DIR=output
LOG_LEVEL=INFO
DEBUG=False
```

## 開発者向け情報

### 環境変数管理
このプロジェクトでは `direnv` を使って環境変数を管理しています：

- **自動仮想環境有効化**: プロジェクトディレクトリに入ると自動的にPoetry仮想環境が有効化されます
- **環境変数の読み込み**: `.env` ファイルから環境変数が自動的に読み込まれます
- **プロジェクト固有の環境変数**: `.envrc` ファイルで設定された環境変数が自動的に設定されます

### Poetryコマンド
```bash
poetry install
poetry add パッケージ名
poetry add --group dev パッケージ名
poetry run python script.py
poetry shell
exit
```

### 開発用ツール
```bash
poetry run black .
poetry run flake8 .
poetry run pytest
``` 