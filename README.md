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
- 仮想環境 (venv)
- direnv (環境変数管理)

## セットアップ

### 前提条件
- pyenv がインストールされていること
- Python 3.13.1 が pyenv で利用可能であること
- direnv がインストールされていること

### 環境構築手順

1. **Python環境の設定**
   ```bash
   # プロジェクトディレクトリでPython 3.13.1を設定
   pyenv local 3.13.1
   
   # 仮想環境を作成
   python -m venv venv
   ```

2. **direnvの設定**
   ```bash
   # direnvを有効化（初回のみ）
   direnv allow
   ```
   
   ※ プロジェクトディレクトリに入ると自動的に仮想環境が有効化されます

3. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
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

- **自動仮想環境有効化**: プロジェクトディレクトリに入ると自動的に仮想環境が有効化されます
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

### 仮想環境の手動操作
```bash
# 仮想環境の有効化（direnvが無効な場合）
source venv/bin/activate

# 仮想環境の無効化
deactivate
```

### 依存関係の更新
```bash
pip install -r requirements.txt --upgrade
```

### 新しい依存関係の追加
```bash
pip install パッケージ名
pip freeze > requirements.txt
``` 