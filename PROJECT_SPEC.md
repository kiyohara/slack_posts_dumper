# プロジェクト仕様書

## 概要
Slackチャネルの投稿をHTML形式で保存するツール

## 機能要件

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

## ファイル構成（予定）
```
slack_posts_dumper/
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt
├── config/
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── slack_client.py
│   ├── html_generator.py
│   ├── data_processor.py
│   └── main.py
├── templates/
│   ├── base.html
│   └── channel.html
├── static/
│   ├── css/
│   │   └── slack-style.css
│   └── js/
│       └── main.js
└── output/
    └── (生成されたHTMLファイル)
```

## 実装フェーズ

### Phase 1: 基本機能
- Slack API接続
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