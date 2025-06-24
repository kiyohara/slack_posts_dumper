# プロジェクト仕様書

## 概要
Slackチャネルの投稿をHTML形式で保存するツール

## 機能要件

### 0. Slack API接続確認（最小構成）
- Slack APIトークン・チャネルID等の設定確認
- Slack APIから最新メッセージ1件を取得し、接続・認証・権限の動作確認
- コマンドライン引数と環境変数の優先順位対応
- エラー時は詳細なメッセージを出力
- **Workspace ID取得ツール**
  - Bot Tokenを使用したWorkspace ID自動取得
  - auth.test APIによるWorkspace情報取得
  - .envファイル設定用の出力形式

### 1. Slack API連携
- Slack Web APIを使用
- 必要な権限：
  - `channels:history` - チャネルの履歴を読み取り
  - `channels:read` - チャネル情報を読み取り
  - `users:read` - ユーザー情報を読み取り
  - `files:read` - ファイル情報を読み取り（添付ファイル対応）
- **ユーザー情報解決ユーティリティ（UserResolver）**
  - ユーザーIDからユーザー情報を取得
  - 内部キャッシュ機能（TTL制御）
  - アイコン情報（アバター画像URL、ステータス絵文字、ステータステキスト）
  - 表示名の自動解決（表示名、実名、ユーザー名の優先順位）
  - その他の情報（メールアドレス、チームID、Bot判定、削除判定）

### 2. データ取得
- 指定したチャネルの全投稿を取得
- 投稿の内容、投稿者、投稿日時、リアクション、スレッド返信を含む
- 添付ファイルの情報も取得

### 3. HTML出力
- Slackの見た目を再現したHTML
- レスポンシブデザイン対応
- ダークモード/ライトモード切り替え
- 投稿の時系列表示
- スレッド表示
- リアクション表示
- 添付ファイル表示

### 4. 保存機能
- 指定したディレクトリにHTMLファイルを保存
- 添付ファイルもローカルにダウンロード
- メタデータ（チャネル情報、取得日時など）も保存

## 技術スタック
- **言語**: Python
- **Slack API**: `slack-sdk`
- **HTML生成**: Jinja2 テンプレートエンジン
- **CSS**: カスタムCSS（Slack風デザイン）
- **JavaScript**: インタラクティブ機能用
- **依存管理**: Poetry（`pyproject.toml`/`poetry.lock`）

## ファイル構成（予定・一部実装済み）
```
slack_posts_dumper/
├── README.md
├── PROJECT_SPEC.md
├── pyproject.toml
├── poetry.lock
├── config/
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── slack_checker.py      # Slack API接続確認（最小構成）
│   ├── slack_client.py       # 本体（今後実装）
│   ├── html_generator.py     # 本体（今後実装）
│   ├── data_processor.py     # 本体（今後実装）
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── utils/
│       ├── __init__.py
│       └── user_resolver.py  # ユーザー情報解決ユーティリティ
├── scripts/
│   ├── get_workspace_id.py   # Workspace ID取得用スクリプト（human/json両対応）
│   ├── get_channels.py       # チャネル一覧取得用スクリプト
│   └── get_latest_message.py # 最新メッセージ取得用スクリプト
├── templates/
│   ├── base.html
│   └── channel.html
├── static/
│   ├── css/
│   │   └── slack-style.css
│   └── js/
│       └── main.js
├── output/
│   └── （生成されたHTMLファイル）
└── env.example
```

## 実装フェーズ

### Phase 0: Slack API接続確認（最小構成）
- Slack API接続確認プログラムの実装
- コマンドライン引数・環境変数の優先順位対応
- 最新メッセージ1件取得・表示
- 動作確認
- **Workspace ID取得ツールの実装**
  - Bot Tokenを使用したWorkspace ID自動取得
  - auth.test APIによるWorkspace情報取得
  - 動作確認・.envファイル自動更新
- **チャネル一覧取得ツールの実装**
  - conversations.list APIによるチャネル一覧取得
  - テーブル形式・JSON形式での出力対応
  - チャネル名での検索機能
  - エラーハンドリング・詳細ログ出力
  - 動作確認（72件のチャネル取得成功）
- **最新メッセージ取得ツールの実装**
  - conversations.history APIによる最新メッセージ1件取得
  - 人間が読みやすい形式とJSON形式での出力対応
  - 添付ファイル、リアクション、スレッド情報の表示
  - エラーハンドリング・詳細ログ出力
  - 動作確認（slack_posts_dumper_testチャンネルで成功）
- **ユーザー情報解決ユーティリティ（UserResolver）の実装**
  - ユーザーIDからユーザー情報を取得するユーティリティクラス
  - 内部キャッシュ機能（TTL制御、デフォルト1時間）
  - アイコン情報の取得（アバター画像URL、ステータス絵文字、ステータステキスト）
  - 表示名の自動解決（表示名、実名、ユーザー名の優先順位）
  - その他の情報取得（メールアドレス、チームID、Bot判定、削除判定）
  - テストツール（test_user_resolver.py）の実装
  - 既存スクリプト（get_latest_message.py）への統合
- **プロジェクト簡素化**
  - SLACK_USER_TOKEN削除（Bot Tokenのみに統一）
  - 設定の最適化・セキュリティ向上
  - **重複機能の統合**: check_slack_api.pyを削除（get_workspace_id.pyで代替）

### Phase 1: 基本機能実装
- **Channel ID取得ツールの実装** ✅
  - ワークスペース内のチャネル一覧取得 ✅
  - チャネル名からChannel ID検索機能 ✅
- **最新メッセージ取得ツールの実装** ✅
  - 指定チャネルの最新メッセージ1件取得 ✅
  - 人間が読みやすい形式とJSON形式での出力 ✅
  - 添付ファイル、リアクション、スレッド情報の表示 ✅
- Slack API連携本体
- チャネル履歴取得
- 基本的なHTML出力

### Phase 2: UI/UX改善
- Slack風デザイン
  - メッセージ中の絵文字（アイコン）を適切に表示する機能
  - 改行などのHTMLタグを適切に処理する機能
  - URLリンクを適切に処理する機能
- レスポンシブ対応
- インタラクティブ機能

### Phase 3: 高度な機能
- 添付ファイル対応
- スレッド表示
- 検索機能
- エクスポート機能

## 注意事項
- Slack APIのレート制限に注意
- 大量のデータ取得時はページネーション対応
- 個人情報の取り扱いに注意
- 添付ファイルの容量制限を考慮

## 現在の実装状況（復元用）

### 完了済み機能
- ✅ Slack API接続確認（最小構成）
- ✅ Workspace ID取得ツール
- ✅ チャネル一覧取得ツール
- ✅ 最新メッセージ取得ツール
- ✅ 設定管理モジュール
- ✅ ユーザー情報解決ユーティリティ（UserResolver）

### 動作確認済み環境
- **Workspace**: 設定済み
- **利用可能チャネル**: 72件
- **検索機能**: "meetup"で60件、"general"で1件
- **出力形式**: テーブル形式・JSON形式
- **最新メッセージ取得**: slack_posts_dumper_testチャンネルで成功

### 復元手順
1. **環境復元**: `poetry install --no-root`
2. **動作確認**: `poetry run python scripts/get_channels.py --verbose`
3. **Workspace確認**: `poetry run python scripts/get_workspace_id.py`
4. **最新メッセージ確認**: `poetry run python scripts/get_latest_message.py --channel-id C09354HEDC1`

### 次の実装予定
- templates/ディレクトリ作成
- static/ディレクトリ作成
- Slack API連携本体（slack_client.py）
- データ処理（data_processor.py）
- HTML出力（html_generator.py, Jinja2テンプレート） 

## 今後の残件・改善予定
- メッセージ中の絵文字（アイコン）を適切に表示する機能
- 改行などのHTMLタグを適切に処理する機能
- URLリンクを適切に処理する機能 