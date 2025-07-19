# Slack API リファレンス

## 概要
このドキュメントは、Slack Posts Dumperプロジェクトで使用するSlack APIの主要なメソッドとその使用方法をまとめたものです。

## 公式ドキュメント
- **Slack API Methods**: https://api.slack.com/methods
- **Slack API Documentation**: https://api.slack.com/
- **Slack SDK for Python**: https://slack.dev/python-slack-sdk/

## 主要なAPIメソッド

### 認証・接続確認
#### `auth.test`
- **説明**: 認証トークンの有効性をテストし、ワークスペース情報を取得
- **権限**: 不要（トークン自体で認証）
- **使用例**: Workspace ID取得ツールで使用

```python
response = client.auth_test()
workspace_info = {
    "team_id": response.get("team_id"),
    "team": response.get("team"),
    "team_domain": response.get("team_domain"),
    "user_id": response.get("user_id"),
    "user": response.get("user"),
    "url": response.get("url")
}
```

### チャネル・会話関連
#### `conversations.list`
- **説明**: ワークスペース内のチャネル一覧を取得
- **権限**: `channels:read`
- **使用例**: チャネル一覧取得ツールで使用

```python
response = client.conversations_list(
    types="public_channel",
    limit=1000
)
channels = response.get("channels", [])
```

#### `conversations.history`
- **説明**: チャネルのメッセージ履歴を取得
- **権限**: `channels:history`
- **使用例**: 最新メッセージ取得ツールで使用

```python
response = client.conversations_history(
    channel=channel_id,
    limit=1
)
messages = response.get("messages", [])
```

#### `conversations.info`
- **説明**: チャネルの詳細情報を取得
- **権限**: `channels:read`

```python
response = client.conversations_info(channel=channel_id)
channel_info = response.get("channel", {})
```

### ユーザー関連
#### `users.info`
- **説明**: ユーザーの詳細情報を取得
- **権限**: `users:read`
- **使用例**: UserResolverで使用

```python
response = client.users_info(user=user_id)
user_info = response.get("user", {})
```

#### `users.list`
- **説明**: ワークスペース内の全ユーザー一覧を取得
- **権限**: `users:read`

```python
response = client.users_list()
users = response.get("members", [])
```

### 絵文字関連
#### `emoji.list`
- **説明**: ワークスペースのカスタム絵文字一覧を取得
- **権限**: `emoji:read`
- **使用例**: EmojiResolverで使用

```python
response = client.emoji_list()
emoji_data = response.get("emoji", {})
```

### ファイル関連
#### `files.info`
- **説明**: ファイルの詳細情報を取得
- **権限**: `files:read`

```python
response = client.files_info(file=file_id)
file_info = response.get("file", {})
```

#### `files.list`
- **説明**: ファイル一覧を取得
- **権限**: `files:read`

```python
response = client.files_list(
    channel=channel_id,
    limit=100
)
files = response.get("files", [])
```

### リアクション関連
#### `reactions.get`
- **説明**: アイテム（メッセージ、ファイル等）のリアクションを取得
- **権限**: `reactions:read`

```python
response = client.reactions_get(
    channel=channel_id,
    timestamp=message_ts
)
reactions = response.get("reactions", [])
```

## エラーハンドリング

### 主要なエラーコード
- `invalid_auth`: 認証トークンが無効
- `token_revoked`: トークンが取り消されている
- `missing_scope`: 必要な権限が不足
- `channel_not_found`: チャネルが見つからない
- `not_in_channel`: Botがチャネルに参加していない

### エラーハンドリング例
```python
try:
    response = client.conversations_history(channel=channel_id)
    if not response["ok"]:
        raise Exception(f"API呼び出しが失敗しました: {response.get('error', 'Unknown error')}")
except SlackApiError as e:
    error_code = e.response.get("error", "unknown_error")
    if error_code == "invalid_auth":
        raise Exception("Bot Tokenが無効です。")
    elif error_code == "missing_scope":
        raise Exception("Bot Tokenに必要な権限がありません。")
    else:
        raise Exception(f"Slack API エラー: {error_code}")
```

## レート制限

### 制限値
- **Tier 1**: 1秒間に1回
- **Tier 2**: 1秒間に20回
- **Tier 3**: 1秒間に50回
- **Tier 4**: 1秒間に100回

### レート制限対応
```python
from slack_sdk.http_retry.builtin_handlers import RateLimitErrorRetryHandler

retry_handler = RateLimitErrorRetryHandler(max_retry_count=3)
client = WebClient(token=token, retry_handlers=[retry_handler])
```

## ページネーション

### cursor-based pagination
```python
response = client.conversations_list(limit=100)
channels = response.get("channels", [])

while response.get("response_metadata", {}).get("next_cursor"):
    cursor = response["response_metadata"]["next_cursor"]
    response = client.conversations_list(limit=100, cursor=cursor)
    channels.extend(response.get("channels", []))
```

## メッセージテキスト処理

### URL形式
Slack APIから取得されるメッセージでは、URLは以下の形式で返されます：

#### 基本的なURL形式
- `<http://example.com>` - 基本的なURL
- `<https://example.com/path>` - HTTPS URL

#### 表示テキスト付きURL形式
- `<http://example.com|表示テキスト>` - カスタム表示テキスト付きURL

#### 処理方法
プロジェクトでは、これらのURL形式をHTMLの`<a>`タグに変換します：

```python
# Slack API形式: <http://example.com>
# 変換後: <a href="http://example.com" target="_blank">http://example.com</a>

# Slack API形式: <http://example.com|表示テキスト>
# 変換後: <a href="http://example.com" target="_blank">表示テキスト</a>
```

### 絵文字形式
- `:emoji_name:` - 絵文字キーワード
- プロジェクトでは、絵文字キーワードを画像URLに置換します

## メッセージオブジェクト構造

### 基本的なメッセージオブジェクト
```json
{
  "type": "message",
  "user": "U1234567890",
  "text": "こんにちは！<http://example.com> :smile:",
  "ts": "1705312225.123456",
  "thread_ts": "1705312225.123456",
  "reply_count": 2,
  "reply_users_count": 1,
  "latest_reply": "1705312300.123456",
  "reactions": [
    {
      "name": "thumbsup",
      "count": 3,
      "users": ["U1234567890", "U2345678901"]
    }
  ],
  "files": [
    {
      "id": "F1234567890",
      "name": "document.pdf",
      "url_private": "https://files.slack.com/files-pri/...",
      "mimetype": "application/pdf"
    }
  ]
}
```

## ユーザーオブジェクト構造

### 基本的なユーザーオブジェクト
```json
{
  "id": "U1234567890",
  "name": "john_doe",
  "real_name": "John Doe",
  "display_name": "John",
  "profile": {
    "real_name": "John Doe",
    "display_name": "John",
    "real_name_normalized": "John Doe",
    "display_name_normalized": "John",
    "email": "john.doe@example.com",
    "image_24": "https://secure.gravatar.com/avatar/...&s=24",
    "image_32": "https://secure.gravatar.com/avatar/...&s=32",
    "image_48": "https://secure.gravatar.com/avatar/...&s=48",
    "image_72": "https://secure.gravatar.com/avatar/...&s=72",
    "image_192": "https://secure.gravatar.com/avatar/...&s=192",
    "image_512": "https://secure.gravatar.com/avatar/...&s=512",
    "status_emoji": "🏠",
    "status_text": "Working from home"
  },
  "is_bot": false,
  "deleted": false,
  "team_id": "T1234567890"
}
```

## チャネルオブジェクト構造

### 基本的なチャネルオブジェクト
```json
{
  "id": "C1234567890",
  "name": "general",
  "is_channel": true,
  "is_group": false,
  "is_im": false,
  "is_mpim": false,
  "is_private": false,
  "is_archived": false,
  "created": 1234567890,
  "creator": "U1234567890",
  "num_members": 100,
  "topic": {
    "value": "チャンネルのトピック",
    "creator": "U1234567890",
    "last_set": 1234567890
  },
  "purpose": {
    "value": "チャンネルの目的",
    "creator": "U1234567890",
    "last_set": 1234567890
  }
}
```

## 開発時の注意事項

### セキュリティ
- APIトークンは環境変数で管理
- `.env`ファイルはGitに含めない
- 本番環境では適切な権限設定

### パフォーマンス
- キャッシュ機能を活用
- レート制限に注意
- 大量データ取得時はページネーション対応

### エラーハンドリング
- 適切なエラーメッセージを表示
- ログ出力でデバッグ情報を記録
- ユーザーフレンドリーなエラー処理

## 更新履歴
- 2024年12月: 初版作成
- 絵文字置換機能対応
- ユーザー情報解決機能対応 