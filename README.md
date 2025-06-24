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

### Slack APIトークンの取得

#### Bot Token (xoxb-) の取得方法

1. **Slack Appの作成**
   - [Slack API](https://api.slack.com/apps) にアクセス
   - 「Create New App」→「From scratch」を選択
   - App名とワークスペースを設定

2. **Bot Token Scopesの設定**
   - 左メニューから「OAuth & Permissions」を選択
   - 「Scopes」セクションの「Bot Token Scopes」に以下を追加：
     - `channels:history` - チャネルの履歴を読み取り
     - `channels:read` - チャネル情報を読み取り
     - `users:read` - ユーザー情報を読み取り
     - `files:read` - ファイル情報を読み取り（添付ファイル対応）

3. **Appのインストール**
   - 「OAuth & Permissions」ページの上部で「Install to Workspace」をクリック
   - 権限を確認して「Allow」をクリック

4. **Bot User OAuth Tokenの取得**
   - インストール後、「Bot User OAuth Token」が表示される
   - このトークン（`xoxb-`で始まる）をコピー

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
   # SLACK_WORKSPACE_ID=T1234567890
   # SLACK_CHANNEL_ID=C1234567890
   ```

## 使い方

### Workspace ID取得ツール

SlackのWorkspace ID（Team ID）を簡単に取得するためのツールが用意されています。

#### 実行例
```bash
# 環境変数からBot Tokenを取得
python scripts/get_workspace_id.py

# 引数でBot Tokenを指定
python scripts/get_workspace_id.py --bot-token xoxb-your-bot-token

# 詳細ログ出力
python scripts/get_workspace_id.py --verbose
```

#### オプション
- `--bot-token` : Slack Bot Token（引数があれば優先、なければ環境変数SLACK_BOT_TOKEN）
- `--verbose, -v` : 詳細ログ出力

#### 出力例
```
=== Workspace情報 ===
Team ID: T0000000001
Team Name: Example Workspace
Team Domain: example-workspace
User ID: U0000000001
User Name: slack_bot
URL: https://example-workspace.slack.com/
===================

✅ Workspace ID: T0000000001

このTeam IDを.envファイルのSLACK_WORKSPACE_IDに設定してください:
SLACK_WORKSPACE_ID=T0000000001
```

#### 注意事項
- Bot Token（xoxb-で始まる）が必要です
- User Token（xoxp-で始まる）では動作しません
- Bot Tokenの取得方法は「Slack APIトークンの取得」セクションを参照してください

#### オプショナル: ブラウザでの手動取得方法

User Tokenがない場合や、スクリプトが使用できない環境では、ブラウザを使って手動でWorkspace IDを取得することもできます。

##### 方法A: 開発者ツールを使用
1. **SlackのWeb版にアクセス**
   - `https://[workspace名].slack.com/` にアクセス
   - アカウントにログイン

2. **開発者ツールを開く**
   - F12キーを押すか、右クリック→「検証」を選択
   - 「Network」タブを選択

3. **ネットワークリクエストを確認**
   - チャンネルを切り替えるなど、何か操作を行う
   - リクエストのURLやレスポンスのJSONを確認
   - `"team_id":"Txxxxxxx"` という形式でTeam IDが含まれている

##### 方法B: ページソースから取得
1. **SlackのWeb版にアクセス**
   - `https://[workspace名].slack.com/` にアクセス
   - アカウントにログイン

2. **ページソースを確認**
   - 右クリック→「ページのソースを表示」を選択
   - Ctrl+F（Cmd+F）で `"team_id"` を検索
   - `"team_id":"Txxxxxxx"` という形式でTeam IDを探す

##### 方法C: localStorageから取得
1. **SlackのWeb版にアクセス**
   - `https://[workspace名].slack.com/` にアクセス
   - アカウントにログイン

2. **開発者ツールを開く**
   - F12キーを押すか、右クリック→「検証」を選択
   - 「Application」タブ（Chrome）または「Storage」タブ（Firefox）を選択
   - 「Local Storage」→「https://[workspace名].slack.com」を選択

3. **localStorageの値を確認**
   - キーと値の一覧から、Team IDを含むエントリを探す
   - `Txxxxxxx` 形式のIDを探す

##### 注意事項
- これらの方法は一時的なもので、Slackの仕様変更により動作しなくなる可能性があります
- 推奨は「Workspace ID取得ツール」を使用することです
- 手動取得したIDは、必ず `T` で始まることを確認してください

### チャネル一覧取得ツール

Slackワークスペース内のチャネル一覧を取得し、チャネルIDを簡単に見つけるためのツールが用意されています。

#### 実行例
```bash
# 環境変数からBot Tokenを取得してチャネル一覧を表示
python scripts/get_channels.py

# 引数でBot Tokenを指定
python scripts/get_channels.py --bot-token xoxb-your-bot-token

# 詳細ログ出力
python scripts/get_channels.py --verbose

# JSON形式で出力
python scripts/get_channels.py --format json

# チャネル名で検索
python scripts/get_channels.py --search "general"
```

#### オプション
- `--bot-token` : Slack Bot Token（引数があれば優先、なければ環境変数SLACK_BOT_TOKEN）
- `--verbose, -v` : 詳細ログ出力
- `--format` : 出力形式（`table` または `json`、デフォルト: `table`）
- `--search` : チャネル名で検索（部分一致）

#### 出力例（テーブル形式）
```
チャネル名                チャネルID          メンバー数      説明                            
--------------------------------------------------------------------------------
general              C0000000001       100        This channel is for team-wide 
random               C0000000002       100        A place for non-work banter              
github               C0000000003       16         GitHub integration channel
twitter              C0000000004       0          Twitter feed updates

✅ 取得完了: 72件のチャネル

チャネルIDを使用する際は、以下の形式で.envファイルに設定してください:
SLACK_CHANNEL_ID=C0000000001
```

#### 出力例（JSON形式）
```json
[
  {
    "name": "general",
    "id": "C0000000001",
    "num_members": 100,
    "purpose": "This channel is for team-wide communication",
    "topic": "",
    "is_private": false,
    "is_archived": false
  }
]
```

#### 検索機能
チャネル名での部分一致検索が可能です：
```bash
# "meetup"を含むチャネルを検索
python scripts/get_channels.py --search "meetup"

# "general"チャネルを検索
python scripts/get_channels.py --search "general"

# "project"を含むチャネルを検索
python scripts/get_channels.py --search "project"
```

#### 注意事項
- Bot Token（xoxb-で始まる）が必要です
- `channels:read`権限が必要です
- パブリックチャネルのみが取得されます
- 最大1000件までのチャネルを取得できます

### .env 設定例
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_WORKSPACE_ID=T0000000001
SLACK_CHANNEL_ID=C0000000001
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