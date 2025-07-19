# Slack API 開発ルール

## 概要
このファイルは、Slack Posts DumperプロジェクトでのSlack API開発時に参照すべき情報をまとめたものです。

## 主要なAPIメソッド

### 認証・接続確認
- `auth.test`: 認証トークンの有効性をテストし、ワークスペース情報を取得

### チャネル・会話関連
- `conversations.list`: ワークスペース内のチャネル一覧を取得（権限: channels:read）
- `conversations.history`: チャネルのメッセージ履歴を取得（権限: channels:history）
- `conversations.info`: チャネルの詳細情報を取得（権限: channels:read）

### ユーザー関連
- `users.info`: ユーザーの詳細情報を取得（権限: users:read）
- `users.list`: ワークスペース内の全ユーザー一覧を取得（権限: users:read）

### 絵文字関連
- `emoji.list`: ワークスペースのカスタム絵文字一覧を取得（権限: emoji:read）

### ファイル関連
- `files.info`: ファイルの詳細情報を取得（権限: files:read）
- `files.list`: ファイル一覧を取得（権限: files:read）

### リアクション関連
- `reactions.get`: アイテムのリアクションを取得（権限: reactions:read）

## 必要なBot Token Scopes
- `channels:history` - チャネルの履歴を読み取り
- `channels:read` - チャネル情報を読み取り
- `users:read` - ユーザー情報を読み取り
- `files:read` - ファイル情報を読み取り（添付ファイル対応）
- `emoji:read` - 絵文字情報を読み取り（絵文字置換機能用）

## エラーハンドリング
主要なエラーコード:
- `invalid_auth`: 認証トークンが無効
- `token_revoked`: トークンが取り消されている
- `missing_scope`: 必要な権限が不足
- `channel_not_found`: チャネルが見つからない
- `not_in_channel`: Botがチャネルに参加していない

## レート制限
- Tier 1: 1秒間に1回
- Tier 2: 1秒間に20回
- Tier 3: 1秒間に50回
- Tier 4: 1秒間に100回

## 開発時の注意事項
- APIトークンは環境変数で管理
- キャッシュ機能を活用
- 適切なエラーハンドリングを実装
- レート制限に注意
- 大量データ取得時はページネーション対応

## 参考リンク
- [Slack API Methods](https://api.slack.com/methods)
- [Slack API Documentation](https://api.slack.com/)
- [Slack SDK for Python](https://slack.dev/python-slack-sdk/) 