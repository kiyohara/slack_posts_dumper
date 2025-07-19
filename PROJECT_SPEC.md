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
  - `emoji:read` - 絵文字情報を読み取り
- **ユーザー情報解決ユーティリティ（UserResolver）**
  - ユーザーIDからユーザー情報を取得
  - 内部キャッシュ機能（TTL制御）
  - アイコン情報（アバター画像URL、ステータス絵文字、ステータステキスト）
  - 表示名の自動解決（表示名、実名、ユーザー名の優先順位）
  - その他の情報（メールアドレス、チームID、Bot判定、削除判定）
- **絵文字置換ユーティリティ（EmojiResolver）**
  - 絵文字キーワード（:emoji:）を画像URLに置換
  - Slack API emoji.listによる絵文字一覧取得
  - 内部キャッシュ機能（TTL制御）
  - カスタム絵文字と標準絵文字の対応
- **URL変換機能**
  - Slack APIのURL形式（<http://example.com>）をクリック可能なリンクに変換
  - 表示テキスト対応（<http://example.com|表示テキスト>）
  - HTMLの`<a>`タグへの変換

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
- **HTMLフィルターパイプライン**
  - モジュラーなフィルター設計
  - 絵文字置換、改行処理、HTMLサニタイズ
  - bleachライブラリによる安全なHTMLサニタイズ
  - 拡張可能なフィルターパイプライン基盤
- **ローカルアセット管理機能**
  - 絵文字やアバター画像のローカルダウンロード
  - URLハッシュベースのファイル管理
  - 統合されたレンダラー（通常モード・ローカルモード）
  - オフライン表示対応

### 4. 保存機能
- 指定したディレクトリにHTMLファイルを保存
- 添付ファイルもローカルにダウンロード
- メタデータ（チャネル情報、取得日時など）も保存
- **ローカルアセット保存機能**
  - 絵文字やアバター画像のローカル保存
  - アセットマニフェストファイルの生成
  - 孤立ファイルの自動クリーンアップ

## 技術スタック
- **言語**: Python 3.13.1
- **Slack API**: `slack-sdk`
- **HTML生成**: Jinja2 テンプレートエンジン
- **HTMLサニタイズ**: `bleach`
- **CSS**: カスタムCSS（Slack風デザイン）
- **JavaScript**: インタラクティブ機能用
- **依存管理**: Poetry（`pyproject.toml`/`poetry.lock`）
- **環境変数管理**: direnv + .env
- **アセット管理**: URLハッシュベースのファイルシステム
- **HTTP通信**: `requests`ライブラリ

## Slack API リファレンス
詳細なAPI情報は `docs/slack_api_reference.md` を参照してください。

### 主要なAPIメソッド
- **認証**: `auth.test` - ワークスペース情報取得
- **チャネル**: `conversations.list`, `conversations.history`, `conversations.info`
- **ユーザー**: `users.info`, `users.list`
- **絵文字**: `emoji.list` - カスタム絵文字一覧取得
- **ファイル**: `files.info`, `files.list`
- **リアクション**: `reactions.get`

### 必要な権限（Bot Token Scopes）
- `channels:history` - チャネルの履歴を読み取り
- `channels:read` - チャネル情報を読み取り
- `users:read` - ユーザー情報を読み取り
- `files:read` - ファイル情報を読み取り
- `emoji:read` - 絵文字情報を読み取り

### HTMLフィルターパイプライン仕様
- **処理順序**: 絵文字置換 → ローカルアセット置換 → URL変換 → 改行処理 → HTMLサニタイズ → 安全出力
- **許可されたHTMLタグ**: `img`, `br`, `a`, `strong`, `em`, `code`, `pre`
- **安全性**: bleachライブラリによるXSS対策
- **拡張性**: 新しいフィルターを簡単に追加可能
- **ローカルアセット置換**: SlackのURLをローカルファイルパスに置換

## ファイル構成（2024年6月時点・現状）
```
.
├── .cursorignore                  # Cursor用無視ファイル
├── .env                           # 環境変数ファイル（git管理外）
├── .envrc                         # direnv用設定ファイル
├── .gitignore                     # Git無視ファイル
├── .python-version                # pyenv用Pythonバージョン指定
├── env.example                    # 環境変数サンプル
├── output/                        # 生成されたHTML等の出力先
│   └── latest_message.html        # 最新メッセージのHTML出力例
├── poetry.lock                    # Poetry依存ロックファイル
├── PROGRESS.md                    # 開発進捗記録
├── PROJECT_SPEC.md                # 本仕様書
├── pyproject.toml                 # Poetryプロジェクト設定
├── README.md                      # プロジェクト概要・使い方
├── scripts/                       # 各種コマンドラインスクリプト
│   ├── get_channels.py            # チャネル一覧取得ツール
│   ├── get_latest_message.py      # 最新メッセージ取得ツール
│   ├── get_workspace_id.py        # Workspace ID取得ツール
│   ├── test_user_resolver.py      # UserResolverテストツール
│   ├── test_emoji_resolver.py     # EmojiResolverテストツール
│   ├── test_asset_manager.py      # AssetManagerテストツール
│   ├── test_asset_downloader.py   # AssetDownloaderテストツール
│   └── test_integrated_renderer.py # 統合レンダラーテストツール
├── src/                           # Pythonパッケージ本体
│   ├── __init__.py                # パッケージ初期化
│   ├── config/                    # 設定管理モジュール
│   │   ├── __init__.py
│   │   └── settings.py            # 設定値取得・検証
│   ├── message_renderer.py        # メッセージHTMLレンダラ
│   ├── slack_checker.py           # Slack API接続確認
│   └── utils/                     # ユーティリティ群
│       ├── __init__.py
│       ├── user_resolver.py       # ユーザー情報解決ユーティリティ
│       ├── emoji_resolver.py      # 絵文字置換ユーティリティ
│       ├── asset_manager.py       # アセット管理ユーティリティ
│       └── asset_downloader.py    # アセットダウンロードユーティリティ
└── templates/                     # Jinja2テンプレート
    ├── message.html               # メッセージ表示用テンプレート
    └── README.md                  # テンプレートディレクトリ説明
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
- **絵文字置換機能・HTMLフィルターパイプラインの実装**
  - src/utils/emoji_resolver.py 作成
  - Slack API emoji.listによる絵文字一覧取得
  - 絵文字キーワード（:emoji:）を画像URLに置換
  - 内部キャッシュ機能（TTL制御）
  - テストツール（scripts/test_emoji_resolver.py）の実装
  - モジュラーなHTMLフィルターパイプライン設計
  - bleachライブラリによる安全なHTMLサニタイズ
  - フィルター処理順序の最適化（絵文字置換 → URL変換 → 改行処理 → サニタイズ）
  - 拡張可能なフィルターパイプライン基盤構築
  - 実際のHTML出力で絵文字表示・URL変換・改行処理・安全なサニタイズを確認
- **URL変換機能のフィルターパイプライン統合**
  - Slack APIのURL形式（<http://example.com>）の調査
  - URL変換フィルター（url_replace）の実装
  - フィルターパイプラインへの統合（emoji_replace → url_replace → nl2br → sanitize_html → safe）
  - 個別のURL変換関数を削除し、フィルターパイプラインに統一
  - 動作確認（HTML形式でクリック可能なリンクに変換）
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
- **絵文字置換機能の実装** ✅
  - Slack API emoji.listによる絵文字一覧取得 ✅
  - 絵文字キーワード（:emoji:）を画像URLに置換 ✅
  - 内部キャッシュ機能（TTL制御） ✅
  - テストツール（scripts/test_emoji_resolver.py）の実装 ✅
  - 既存スクリプト（get_latest_message.py）への統合 ✅
- **HTMLフィルターパイプラインの実装** ✅
  - モジュラーなフィルター設計 ✅
  - bleachライブラリによる安全なHTMLサニタイズ ✅
  - フィルター処理順序の最適化 ✅
  - 拡張可能なフィルターパイプライン基盤構築 ✅
- Slack API連携本体
- チャネル履歴取得
- 基本的なHTML出力

### Phase 2: UI/UX改善
- Slack風デザイン
  - メッセージ中の絵文字（アイコン）を適切に表示する機能 ✅
  - 改行などのHTMLタグを適切に処理する機能 ✅
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
- ✅ 絵文字置換ユーティリティ（EmojiResolver）
- ✅ HTMLフィルターパイプライン
- ✅ HTMLサニタイズ機能
- ✅ ローカルアセット管理機能（AssetManager）
- ✅ アセットダウンロード機能（AssetDownloader）
- ✅ 統合されたレンダラー（通常モード・ローカルモード）
- ✅ ローカルファイル形式出力（format=local）

### 動作確認済み環境
- **Workspace**: 設定済み
- **利用可能チャネル**: 72件
- **検索機能**: "meetup"で60件、"general"で1件
- **出力形式**: テーブル形式・JSON形式
- **最新メッセージ取得**: slack_posts_dumper_testチャンネルで成功

### 復元手順
1. **環境復元**: `poetry install --no-root`
2. **動作確認**: `poetry run python scripts/get_latest_message.py --format html --channel-id C09354HEDC1`
3. **絵文字置換テスト**: `poetry run python scripts/test_emoji_resolver.py`
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