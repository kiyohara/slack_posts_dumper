# Slack Posts Dumper

## プロジェクトの目的

このプロジェクトは、Slackの特定チャネルに書き込まれた内容をHTMLとして保存するプログラムです。

### 主な機能
- Slack APIを通じて指定したチャネルのデータを取得
- 取得したデータをSlack上で閲覧している見栄えと同じような内容となるHTMLとして保存
- チャネルの投稿履歴をローカルに保存し、オフラインでも閲覧可能
- **絵文字の適切な表示** - Slack API emoji.listによる絵文字一覧取得・置換
- **URL変換機能** - Slack APIのURL形式（<http://example.com>）をクリック可能なリンクに変換
- **HTMLフィルターパイプライン** - モジュラーなフィルター設計による安全なHTML処理
- **ローカルアセット管理** - 絵文字やアバター画像をローカルにダウンロードしてオフライン表示
- **統合されたレンダラー** - 通常モードとローカルモードを1つのレンダラーで統一的に処理
- **Unicodeフォールバック機能** - ダウンロードに失敗した標準絵文字をUnicodeに変換して表示

### 技術要件
- Slack APIを使用したデータ取得
- HTML形式での出力
- Slackの見た目を再現したスタイリング
- **絵文字置換機能** - 絵文字キーワード（:emoji:）を画像URLに置換
- **URL変換機能** - Slack APIのURL形式をHTMLの`<a>`タグに変換
- **HTMLサニタイズ** - bleachライブラリによる安全なHTML処理
- **アセット管理システム** - URLハッシュベースのローカルファイル管理
- **アセットダウンロード機能** - Slackアセットの自動ダウンロードとキャッシュ
- **統合フィルターパイプライン** - 絵文字置換とローカルパス置換の統合処理
- **emojiライブラリ統合** - 絵文字のshortnameをUnicodeに変換する機能

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
     - `emoji:read` - 絵文字情報を読み取り（絵文字置換機能用）

3. **Appのインストール**
   - 「OAuth & Permissions」ページの上部で「Install to Workspace」をクリック
   - 権限を確認して「Allow」をクリック

4. **Bot User OAuth Tokenの取得**
   - インストール後、「Bot User OAuth Token」が表示される
   - このトークン（`xoxb-`で始まる）をコピー

#### Botをチャネルに参加させる

作成したBot（App）をターゲットとなるチャネルに参加させる必要があります。以下のいずれかの方法でBotをチャネルに招待してください：

##### 方法A: チャネル内でBotを招待
1. **ターゲットチャネルに移動**
   - メッセージを取得したいチャネルを開く

2. **Botを招待**
   - チャネル内で以下のコマンドを入力：
   ```
   /invite @[Bot名]
   ```
   - 例：`/invite @slack_posts_dumper`

##### 方法B: チャネル設定からBotを追加
1. **チャネル名をクリック**
   - チャネル名の横にある「▼」をクリック
   - 「設定」を選択

2. **インテグレーションを開く**
   - 左メニューから「インテグレーション」を選択
   - 「アプリを追加」をクリック

3. **Botを検索・追加**
   - 作成したBot名で検索
   - 「追加」をクリックして権限を確認

##### 方法C: チャネル作成時にBotを追加
1. **新しいチャネルを作成**
   - 「+」ボタンから「チャンネルを作成」を選択

2. **Botを追加**
   - チャンネル作成画面で「プライベートチャンネルにする」の下にある
   - 「アプリを追加」から作成したBotを選択

#### 注意事項
- Botがチャネルに参加していない場合、メッセージの取得時に「Botがチャネルに参加していません」エラーが発生します
- パブリックチャネルの場合、Botは自動的に参加できません。手動で招待する必要があります
- プライベートチャネルの場合、Botを招待するにはチャンネルの管理者権限が必要です
- Botがチャネルに参加した後、そのチャネルのメッセージを取得できるようになります

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
# 
# 注意: emoji:read権限が必要です（絵文字置換機能用）
# 注意: emojiライブラリが追加されました（Unicodeフォールバック機能用）
   ```

## 使い方

### 絵文字置換テスト

絵文字置換機能の動作を確認するためのテストツールが用意されています。

```bash
# 絵文字一覧取得テスト
poetry run python scripts/test_emoji_resolver.py

# 特定の絵文字のURL取得テスト
poetry run python scripts/test_emoji_resolver.py --emoji slightly_smiling_face

# テキスト置換テスト
poetry run python scripts/test_emoji_resolver.py --text "こんにちは :slightly_smiling_face: 今日は良い天気ですね :sunny:"

# Unicodeフォールバック機能テスト
poetry run python scripts/test_emoji_resolver_unicode.py

# emojiライブラリテスト
poetry run python scripts/test_emoji_library.py
```

### HTMLフィルターパイプライン

HTMLフィルターパイプラインは以下の順序で処理されます：

1. **絵文字置換** - `:emoji:` → `<img>`タグ（ダウンロード失敗時はUnicodeに変換）
2. **URL変換** - `<http://example.com>` → `<a href="...">`タグ
3. **改行処理** - `\n` → `<br>`タグ
4. **HTMLサニタイズ** - 許可されたタグのみ残す
5. **ローカルアセット置換** - ダウンロード済みアセットのURLをローカルパスに置換
6. **安全出力** - HTMLとして出力

### Unicodeフォールバック機能

ダウンロードに失敗した標準絵文字に対して、以下の処理を行います：

1. **ダウンロード成功**: ローカルパス（`assets/xxx.png`）を使用
2. **ダウンロード失敗（標準絵文字）**: Unicode絵文字（`🙂`）に変換
3. **ダウンロード失敗（カスタム絵文字）**: 元のURLをそのまま表示

これにより、Slackの標準絵文字が403エラーでダウンロードに失敗しても、ブラウザのシステムフォントを使用して正しく表示されます。

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

# JSON形式で出力
python scripts/get_workspace_id.py --format json
```

#### オプション
- `--bot-token` : Slack Bot Token（引数があれば優先、なければ環境変数SLACK_BOT_TOKEN）
- `--verbose, -v` : 詳細ログ出力
- `--format` : 出力形式（`human` または `json`、デフォルト: `human`）

#### 出力例（人間が読みやすい形式）
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

#### 出力例（JSON形式）
```json
{
  "team_id": "T0000000001",
  "team": "Example Workspace",
  "team_domain": "example-workspace",
  "user_id": "U0000000001",
  "user": "slack_bot",
  "url": "https://example-workspace.slack.com/"
}
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

### 最新メッセージ取得ツール

指定したチャネルの最新メッセージ1件を取得して表示するツールが用意されています。

#### 実行例
```bash
# 環境変数から設定を取得して最新メッセージを表示
python scripts/get_latest_message.py

# 引数でチャネルIDを指定
python scripts/get_latest_message.py --channel-id C1234567890

# 引数でワークスペースIDとチャネルIDを指定
python scripts/get_latest_message.py --workspace-id T1234567890 --channel-id C1234567890

# 詳細ログ出力
python scripts/get_latest_message.py --verbose

# JSON形式で出力
python scripts/get_latest_message.py --format json
```

#### オプション
- `--bot-token` : Slack Bot Token（引数があれば優先、なければ環境変数SLACK_BOT_TOKEN）
- `--workspace-id` : ワークスペースID（引数があれば優先、なければ環境変数SLACK_WORKSPACE_ID）
- `--channel-id` : チャネルID（引数があれば優先、なければ環境変数SLACK_CHANNEL_ID）
- `--verbose, -v` : 詳細ログ出力
- `--format` : 出力形式（`human` または `json`、デフォルト: `human`）

#### 出力例（人間が読みやすい形式）
```
=== 最新メッセージ ===
投稿日時: 2024-01-15 14:30:25
投稿者: john_doe (U1234567890)
内容:
こんにちは！今日の会議について確認したいことがあります。
添付ファイル: meeting_notes.pdf
リアクション: thumbsup:3, heart:1
（スレッド返信）
```

#### 出力例（JSON形式）
```json
{
  "ts": "1705312225.123456",
  "datetime": "2024-01-15T14:30:25.123456",
  "user": "U1234567890",
  "username": "john_doe",
  "text": "こんにちは！今日の会議について確認したいことがあります。",
  "files": [
    {
      "name": "meeting_notes.pdf",
      "url_private": "https://files.slack.com/files-pri/...",
      "mimetype": "application/pdf"
    }
  ],
  "reactions": [
    {
      "name": "thumbsup",
      "count": 3,
      "users": ["U1234567890", "U2345678901", "U3456789012"]
    },
    {
      "name": "heart",
      "count": 1,
      "users": ["U4567890123"]
    }
  ],
  "thread_ts": "1705312225.123456",
  "is_thread_reply": true,
  "type": "message"
}
```

#### 取得される情報
- **基本情報**: 投稿日時、投稿者、メッセージ内容
- **添付ファイル**: ファイル名、URL、MIMEタイプ
- **リアクション**: 絵文字とその数、リアクションしたユーザー
- **スレッド情報**: スレッド返信かどうか、親メッセージのタイムスタンプ
- **メッセージタイプ**: 通常メッセージ、システムメッセージなど

#### 注意事項
- Bot Token（xoxb-で始まる）が必要です
- `channels:history`権限が必要です
- Botがチャネルに参加している必要があります
- 最新1件のメッセージのみを取得します
- システムメッセージ（Bot参加、チャンネル作成など）も取得されます
- プライベートチャンネルの場合、Botを招待する必要があります

### ユーザー情報解決ユーティリティ

SlackのユーザーIDからユーザー情報を取得するためのユーティリティライブラリが用意されています。内部にキャッシュ機構を持ち、API呼び出し回数を最小限に抑えることができます。

#### 機能
- **ユーザー情報の取得**: ユーザーIDからユーザーの詳細情報を取得
- **キャッシュ機能**: 一度取得したユーザー情報をメモリにキャッシュ
- **TTL制御**: キャッシュの有効期限を設定可能（デフォルト: 1時間）
- **表示名の自動解決**: 表示名、実名、ユーザー名の優先順位で表示名を決定
- **アイコン情報の取得**: アバター画像URL、ステータス絵文字、ステータステキスト
- **その他の情報**: メールアドレス、チームID、Bot判定、削除判定
- **エラーハンドリング**: ユーザーが見つからない場合の適切な処理

#### 使用例

```python
from slack_sdk import WebClient
from src.utils.user_resolver import create_user_resolver

# Slackクライアントを初期化
client = WebClient(token="xoxb-your-bot-token")

# UserResolverインスタンスを作成（キャッシュTTL: 1時間）
resolver = create_user_resolver(client, cache_ttl=3600)

# ユーザー情報を取得
user_info = resolver.get_user_info("U1234567890")
if user_info:
    print(f"表示名: {user_info['display_name']}")
    print(f"実名: {user_info['profile']['real_name']}")
    print(f"ユーザー名: {user_info['name']}")

# 表示名のみを取得
display_name = resolver.get_user_display_name("U1234567890")
print(f"表示名: {display_name}")

# アイコン情報を取得
avatar_url = resolver.get_user_avatar_url("U1234567890")
status_emoji = resolver.get_user_status_emoji("U1234567890")
status_text = resolver.get_user_status_text("U1234567890")
print(f"アバターURL: {avatar_url}")
print(f"ステータス絵文字: {status_emoji}")
print(f"ステータステキスト: {status_text}")

# その他の情報を取得
email = resolver.get_user_email("U1234567890")
team_id = resolver.get_user_team_id("U1234567890")
is_bot = resolver.get_user_is_bot("U1234567890")
print(f"メールアドレス: {email}")
print(f"チームID: {team_id}")
print(f"Bot: {is_bot}")

# キャッシュをクリア
resolver.clear_cache()

# キャッシュ情報を取得
cache_info = resolver.get_cache_info()
print(f"キャッシュ済みユーザー数: {cache_info['total_cached_users']}")
```

#### テストツール

UserResolverの動作をテストするためのツールが用意されています。

##### 実行例
```bash
# 環境変数から設定を取得してテスト
python scripts/test_user_resolver.py

# 特定のユーザーIDを指定してテスト
python scripts/test_user_resolver.py --user-id U1234567890

# キャッシュTTLを変更してテスト
python scripts/test_user_resolver.py --cache-ttl 1800

# 強制リフレッシュでテスト
python scripts/test_user_resolver.py --force-refresh

# 詳細ログ出力
python scripts/test_user_resolver.py --verbose
```

##### オプション
- `--bot-token` : Slack Bot Token（引数があれば優先、なければ環境変数SLACK_BOT_TOKEN）
- `--user-id` : テスト対象のユーザーID（指定しない場合は現在のユーザー）
- `--cache-ttl` : キャッシュの有効期限（秒、デフォルト: 3600）
- `--force-refresh` : キャッシュを無視して強制的に再取得
- `--verbose, -v` : 詳細ログ出力

##### テスト内容
1. **ユーザー情報の取得テスト**: 基本的なユーザー情報取得機能
2. **個別メソッドのテスト**: 表示名、実名、ユーザー名の個別取得
3. **キャッシュ機能のテスト**: キャッシュによる高速化効果の確認
4. **キャッシュ情報の表示**: キャッシュの状態確認
5. **キャッシュクリアのテスト**: キャッシュクリア機能の確認

##### 出力例
```
=== UserResolverテスト ===
テスト対象ユーザーID: U1234567890
キャッシュTTL: 3600秒
強制リフレッシュ: False

1. ユーザー情報の取得テスト
----------------------------------------
✓ ユーザー情報の取得に成功
  ユーザーID: U1234567890
  表示名: John Doe
  実名: John Doe
  ユーザー名: john_doe
  メールアドレス: john.doe@example.com

2. 個別メソッドのテスト
----------------------------------------
表示名: John Doe
実名: John Doe
ユーザー名: john_doe
アバターURL: https://secure.gravatar.com/avatar/...
ステータス絵文字: 🏠
ステータステキスト: Working from home
メールアドレス: john.doe@example.com
チームID: T0000000001
Bot: False
削除済み: False

アバター画像サイズ別テスト:
  サイズ24: https://secure.gravatar.com/avatar/...&s=24
  サイズ32: https://secure.gravatar.com/avatar/...&s=32
  サイズ48: https://secure.gravatar.com/avatar/...&s=48
  サイズ72: https://secure.gravatar.com/avatar/...&s=72
  サイズ192: https://secure.gravatar.com/avatar/...&s=192
  サイズ512: https://secure.gravatar.com/avatar/...&s=512
  サイズ1024: https://secure.gravatar.com/avatar/...&s=1024

3. キャッシュ機能のテスト
----------------------------------------
初回取得時間: 0.1234秒
2回目取得時間: 0.0001秒
キャッシュ効果: 1234.0倍高速

4. キャッシュ情報
----------------------------------------
キャッシュ済みユーザー数: 1
有効キャッシュ数: 1
期限切れキャッシュ数: 0
キャッシュTTL: 3600秒

5. キャッシュクリアのテスト
----------------------------------------
キャッシュクリア前:
  キャッシュ済みユーザー数: 1
キャッシュクリア後:
  キャッシュ済みユーザー数: 0

=== テスト完了 ===
```

#### 注意事項
- Bot Token（xoxb-で始まる）が必要です
- `users:read`権限が必要です
- キャッシュはメモリ上に保存されるため、プログラム終了時に失われます
- 大量のユーザー情報を取得する場合は、定期的に`cleanup_expired_cache()`を呼び出すことを推奨します

### ローカルアセット管理機能

Slackの絵文字やアバター画像などのアセットをローカルにダウンロードし、オフラインでも表示できる機能が追加されました。

#### 主な機能
- **アセット管理システム** - URLハッシュベースのローカルファイル管理
- **アセットダウンロード機能** - Slackアセットの自動ダウンロードとキャッシュ
- **統合フィルターパイプライン** - 絵文字置換とローカルパス置換の統合処理
- **重複ダウンロード防止** - 同じURLのアセットは一度だけダウンロード
- **マニフェスト管理** - ダウンロードしたアセットの情報をJSONファイルで管理

#### 使用方法

```bash
# ローカルファイル形式で出力（アセットをダウンロード）
python scripts/get_latest_message.py --format local --output-dir ./output
```

#### 生成されるファイル構造

```
output/
├── message.html          # ローカルファイル参照のHTML
├── assets/              # ダウンロードしたアセット
│   ├── [hash].png       # アバター画像
│   ├── [hash].gif       # 絵文字画像
│   └── ...
└── assets_manifest.json # アセット情報のマニフェスト
```

#### フィルター処理の流れ

```
1. emoji_replace: :smile: → <img src="https://...">
2. local_asset_replace: <img src="https://..."> → <img src="assets/...">
3. url_replace: URLの置換
4. nl2br: 改行の処理
5. sanitize_html: HTMLサニタイズ
```

#### 統合されたレンダラー

通常モードとローカルモードを1つのレンダラーで統一的に処理します：

```python
# 通常モード
renderer = SlackMessageHtmlRenderer(emoji_resolver=emoji_resolver)

# ローカルモード
renderer = SlackMessageHtmlRenderer(
    emoji_resolver=emoji_resolver, 
    asset_manager=asset_manager
)
```

#### テストツール

ローカルアセット管理機能のテストツールが用意されています：

```bash
# AssetManagerのテスト
python scripts/test_asset_manager.py

# AssetDownloaderのテスト
python scripts/test_asset_downloader.py

# 統合されたレンダラーのテスト
python scripts/test_integrated_renderer.py
```

#### 注意事項
- `format=local`の場合は`--output-dir`オプションが必要です
- アセットのダウンロードには時間がかかる場合があります
- ダウンロードしたアセットは`assets_manifest.json`で管理されます
- 孤立したファイルは`cleanup_orphaned_assets()`で削除できます
- ユーザーが見つからない場合は`None`を返します

### 絵文字解決ユーティリティ

Slackのメッセージ内の絵文字（`:emoji_name:`形式）を画像タグに置換するためのユーティリティライブラリが用意されています。Slack APIの`emoji.list`を使用してカスタム絵文字の情報を取得し、標準絵文字はSlackの公式URLを使用します。

#### 機能
- **絵文字一覧の取得**: Slack APIの`emoji.list`を使用してカスタム絵文字一覧を取得
- **キャッシュ機能**: 一度取得した絵文字情報をメモリにキャッシュ
- **TTL制御**: キャッシュの有効期限を設定可能（デフォルト: 1時間）
- **標準絵文字対応**: Slackの公式絵文字URLを使用
- **テキスト内絵文字置換**: メッセージ内の`:emoji_name:`を画像タグに置換
- **エラーハンドリング**: 絵文字が見つからない場合の適切な処理

#### 使用例

```python
from slack_sdk import WebClient
from src.utils.emoji_resolver import create_emoji_resolver

# Slackクライアントを初期化
client = WebClient(token="xoxb-your-bot-token")

# EmojiResolverインスタンスを作成（キャッシュTTL: 1時間）
resolver = create_emoji_resolver(client, cache_ttl=3600)

# 絵文字一覧を取得
emoji_list = resolver.get_emoji_list()
print(f"取得した絵文字数: {len(emoji_list)}")

# 特定の絵文字のURLを取得
emoji_url = resolver.get_emoji_url("slightly_smiling_face")
print(f"絵文字URL: {emoji_url}")

# テキスト内の絵文字を置換
text = "こんにちは :slightly_smiling_face: 今日は良い天気ですね :sunny:"
replaced_text = resolver.replace_emojis_in_text(text)
print(f"置換後のテキスト: {replaced_text}")

# キャッシュ情報を取得
cache_info = resolver.get_cache_info()
print(f"キャッシュ済み絵文字数: {cache_info['total_cached_emojis']}")
```

#### テストツール

EmojiResolverの動作をテストするためのツールが用意されています。

##### 実行例
```bash
# 環境変数から設定を取得してテスト
python scripts/test_emoji_resolver.py

# 特定の絵文字をテスト
python scripts/test_emoji_resolver.py --emoji "slightly_smiling_face"

# テキスト内の絵文字置換をテスト
python scripts/test_emoji_resolver.py --text "こんにちは :slightly_smiling_face: 今日は良い天気ですね :sunny:"

# キャッシュTTLを変更してテスト
python scripts/test_emoji_resolver.py --cache-ttl 1800

# 強制リフレッシュでテスト
python scripts/test_emoji_resolver.py --force-refresh

# 詳細ログ出力
python scripts/test_emoji_resolver.py --verbose
```

##### オプション
- `--bot-token` : Slack Bot Token（引数があれば優先、なければ環境変数SLACK_BOT_TOKEN）
- `--emoji` : テスト対象の絵文字名（例: slightly_smiling_face）
- `--text` : 絵文字置換をテストするテキスト
- `--cache-ttl` : キャッシュの有効期限（秒、デフォルト: 3600）
- `--force-refresh` : キャッシュを無視して強制的に再取得
- `--verbose, -v` : 詳細ログ出力

##### テスト内容
1. **絵文字一覧の取得テスト**: 基本的な絵文字一覧取得機能
2. **特定絵文字のテスト**: 指定した絵文字のURL取得
3. **テキスト置換のテスト**: メッセージ内の絵文字置換機能
4. **キャッシュ機能のテスト**: キャッシュによる高速化効果の確認
5. **標準絵文字のテスト**: Slack公式絵文字の動作確認

##### 出力例
```
=== 絵文字解決ユーティリティテストツール ===

絵文字一覧を取得中...
✅ 絵文字一覧取得完了: 15件

=== 絵文字一覧 ===
:custom_emoji1: -> https://files.slack.com/files-tmb/...
:custom_emoji2: -> https://files.slack.com/files-tmb/...
:slightly_smiling_face: -> https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/slightly_smiling_face.png
==================

=== 絵文字 'slightly_smiling_face' のテスト ===
絵文字名: :slightly_smiling_face:
URL: https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/slightly_smiling_face.png
HTML: <img src="https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/slightly_smiling_face.png" alt=":slightly_smiling_face:" class="slack-emoji">

=== テキスト内の絵文字置換テスト ===
元のテキスト: こんにちは :slightly_smiling_face: 今日は良い天気ですね :sunny:
置換後のテキスト: こんにちは <img src="https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/slightly_smiling_face.png" alt=":slightly_smiling_face:" class="slack-emoji" width="20" height="20" style="vertical-align: middle;"> 今日は良い天気ですね <img src="https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/sunny.png" alt=":sunny:" class="slack-emoji" width="20" height="20" style="vertical-align: middle;">

=== キャッシュ情報 ===
キャッシュ済み絵文字数: 15
キャッシュTTL: 3600秒
キャッシュ経過時間: 0.0秒
キャッシュ有効: はい

=== 標準絵文字のテスト ===
:slightly_smiling_face: -> https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/slightly_smiling_face.png
:sunny: -> https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/sunny.png
:heart: -> https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/heart.png
:thumbsup: -> https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/thumbsup.png
:check: -> https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/check.png

✅ EmojiResolverテスト完了
```

#### 注意事項
- Bot Token（xoxb-で始まる）が必要です
- `emoji:read`権限が必要です
- キャッシュはメモリ上に保存されるため、プログラム終了時に失われます
- 標準絵文字はSlackの公式URLを使用します
- カスタム絵文字はワークスペース固有のURLを使用します

### .env 設定例
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_WORKSPACE_ID=T0000000001
SLACK_CHANNEL_ID=C0000000001
OUTPUT_DIR=output
LOG_LEVEL=INFO
DEBUG=False
```

## ドキュメント

### プロジェクトドキュメント
- **プロジェクト仕様書**: `PROJECT_SPEC.md` - プロジェクトの詳細仕様
- **開発進捗**: `PROGRESS.md` - 開発の進捗状況
- **Slack API リファレンス**: `docs/slack_api_reference.md` - Slack APIの詳細情報

### 外部リンク
- **Slack API Methods**: https://api.slack.com/methods
- **Slack API Documentation**: https://api.slack.com/
- **Slack SDK for Python**: https://slack.dev/python-slack-sdk/

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