# 実装時の注意事項

## 実装済み機能

### Slack API接続確認（最小構成）
- ✅ `src/slack_checker.py`: Slack API接続確認プログラム
- ✅ コマンドライン引数・環境変数の優先順位対応
- ✅ 最新メッセージ1件取得・表示機能

### Workspace ID取得ツール
- ✅ `scripts/get_workspace_id.py`: Workspace ID取得ツール
- ✅ Bot Tokenを使用したWorkspace ID自動取得
- ✅ auth.test APIによるWorkspace情報取得
- ✅ 詳細ログ出力・エラーハンドリング

### チャネル一覧取得ツール
- ✅ `scripts/get_channels.py`: チャネル一覧取得ツール
- ✅ conversations.list APIによるチャネル一覧取得
- ✅ テーブル形式・JSON形式での出力対応
- ✅ チャネル名での検索機能（部分一致）
- ✅ エラーハンドリング・詳細ログ出力
- ✅ 最大1000件までのチャネル取得対応

### 設定管理
- ✅ `src/config/settings.py`: 設定管理モジュール
- ✅ Bot Token、Workspace ID、Channel IDの取得・検証機能
- ✅ 環境変数・コマンドライン引数の優先順位処理

### 最新メッセージ取得ツール
- ✅ `scripts/get_latest_message.py`: 最新メッセージ取得ツール
- ✅ conversations.history APIによる最新メッセージ1件取得
- ✅ 人間が読みやすい形式とJSON形式での出力対応
- ✅ 添付ファイル、リアクション、スレッド情報の表示
- ✅ エラーハンドリング・詳細ログ出力

### ユーザー情報解決ユーティリティ
- ✅ `src/utils/user_resolver.py`: ユーザー情報解決ユーティリティ
- ✅ ユーザーIDからユーザー情報を取得するユーティリティクラス
- ✅ 内部キャッシュ機能（TTL制御、デフォルト1時間）
- ✅ アイコン情報の取得（アバター画像URL、ステータス絵文字、ステータステキスト）
- ✅ 表示名の自動解決（表示名、実名、ユーザー名の優先順位）
- ✅ その他の情報取得（メールアドレス、チームID、Bot判定、削除判定）
- ✅ テストツール（scripts/test_user_resolver.py）の実装
- ✅ 既存スクリプト（get_latest_message.py）への統合

### 絵文字置換機能・HTMLフィルターパイプライン
- ✅ `src/utils/emoji_resolver.py`: 絵文字置換ユーティリティ
- ✅ Slack API emoji.listによる絵文字一覧取得
- ✅ 絵文字キーワード（:emoji:）を画像URLに置換
- ✅ 内部キャッシュ機能（TTL制御）
- ✅ テストツール（scripts/test_emoji_resolver.py）の実装
- ✅ モジュラーなHTMLフィルターパイプライン設計
- ✅ bleachライブラリによる安全なHTMLサニタイズ
- ✅ フィルター処理順序の最適化（絵文字置換 → URL変換 → 改行処理 → サニタイズ）
- ✅ 拡張可能なフィルターパイプライン基盤構築
- ✅ URL変換機能のフィルターパイプライン統合
- ✅ Slack APIのURL形式（<http://example.com>）の調査・実装
- ✅ URL変換フィルター（url_replace）の実装
- ✅ フィルターパイプラインへの統合（emoji_replace → url_replace → nl2br → sanitize_html → safe）
- ✅ 個別のURL変換関数を削除し、フィルターパイプラインに統一

## 現在の実装状況（復元用）

### 動作確認済み環境
- **Python**: 3.13.1 (pyenv管理)
- **Poetry**: 依存関係管理済み
- **Slack API**: slack-sdk 3.35.0以上
- **Workspace**: 設定済み
- **利用可能チャネル**: 72件

### 復元手順
1. **環境復元**: `poetry install --no-root`
2. **動作確認**: `poetry run python scripts/get_channels.py --verbose`
3. **検索テスト**: `poetry run python scripts/get_channels.py --search "general"`
4. **JSON出力テスト**: `poetry run python scripts/get_channels.py --format json`

### 既知の動作確認結果
- Workspace ID取得: 成功
- チャネル一覧取得: 72件成功
- 検索機能: "meetup"で60件、"general"で1件
- エラーハンドリング: 正常動作確認済み

## Slack API関連
- **必要な権限**:
  - `channels:history` - チャネルの履歴を読み取り
  - `channels:read` - チャネル情報を読み取り
  - `users:read` - ユーザー情報を読み取り
  - `files:read` - ファイル情報を読み取り（添付ファイル対応）
  - `emoji:read` - 絵文字情報を読み取り（絵文字置換機能用）

- **レート制限**: Slack APIのレート制限に注意
- **ページネーション**: 大量のデータ取得時はページネーション対応

## データ処理
- **取得データ**: 投稿内容、投稿者、投稿日時、リアクション、スレッド返信、添付ファイル
- **個人情報**: 個人情報の取り扱いに注意
- **ファイル容量**: 添付ファイルの容量制限を考慮

## HTML出力要件
- **デザイン**: Slackの見た目を再現
- **レスポンシブ**: モバイル対応
- **テーマ**: ダークモード/ライトモード切り替え
- **機能**: 時系列表示、スレッド表示、リアクション表示、添付ファイル表示
- **フィルターパイプライン**: 絵文字置換、URL変換、改行処理、HTMLサニタイズ

## 技術スタック詳細
- **Slack API**: `slack-sdk` (>=3.35.0)
- **HTML生成**: Jinja2 (>=3.1.6)
- **HTMLサニタイズ**: bleach (>=6.1.0)
- **環境変数**: python-dotenv (>=1.1.0)
- **日時処理**: python-dateutil (>=2.9.0.post0)
- **HTTP通信**: requests (>=2.32.4)

## セキュリティ考慮事項
- APIトークンは.envファイルで管理（Gitに含めない）
- 個人情報の適切な取り扱い
- ファイルアクセス権限の設定
- ログ出力時の機密情報の除外

## パフォーマンス考慮事項
- 大量データ取得時のメモリ使用量
- ファイルダウンロード時の進捗表示
- HTML生成時の処理時間
- キャッシュ機能の実装検討 