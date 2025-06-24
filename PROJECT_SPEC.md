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
│   └── config/
│       ├── __init__.py
│       └── settings.py
├── scripts/
│   ├── check_slack_api.py    # Slack API接続確認用スクリプト
│   └── get_workspace_id.py   # Workspace ID取得用スクリプト
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
- **プロジェクト簡素化**
  - SLACK_USER_TOKEN削除（Bot Tokenのみに統一）
  - 設定の最適化・セキュリティ向上

### Phase 1: 基本機能実装
- **Channel ID取得ツールの実装**
  - ワークスペース内のチャネル一覧取得
  - チャネル名からChannel ID検索機能
- Slack API連携本体
- チャネル履歴取得
- 基本的なHTML出力

### Phase 2: UI/UX改善
- Slack風デザイン
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