# 開発ガイドライン

## 環境設定
- **Python**: 3.13.1 (pyenv管理)
- **依存管理**: Poetry (`pyproject.toml`/`poetry.lock`)
- **環境変数**: direnv + .env
- **仮想環境**: Poetry仮想環境（自動有効化）

## コーディング規約
- **言語**: Python
- **フォーマッター**: Black
- **リンター**: flake8
- **テスト**: pytest

## 開発コマンド
```bash
# 依存関係のインストール
poetry install

# 新しい依存関係の追加
poetry add パッケージ名

# 開発用依存関係の追加
poetry add --group dev パッケージ名

# コードフォーマット
poetry run black .

# リンター
poetry run flake8 .

# テスト実行
poetry run pytest

# 仮想環境内でコマンド実行
poetry run python script.py
```

## 実装済みスクリプト

### Slack API接続確認
```bash
# 基本的な接続確認
poetry run python scripts/check_slack_api.py

# 詳細ログ出力
poetry run python scripts/check_slack_api.py --verbose

# 引数で設定を上書き
poetry run python scripts/check_slack_api.py --workspace-id T1234567890 --channel-id C1234567890
```

### Workspace ID取得
```bash
# 環境変数からBot Tokenを取得
poetry run python scripts/get_workspace_id.py

# 引数でBot Tokenを指定
poetry run python scripts/get_workspace_id.py --bot-token xoxb-your-token

# 詳細ログ出力
poetry run python scripts/get_workspace_id.py --verbose
```

### チャネル一覧取得
```bash
# 基本的なチャネル一覧表示
poetry run python scripts/get_channels.py

# 詳細ログ出力
poetry run python scripts/get_channels.py --verbose

# JSON形式で出力
poetry run python scripts/get_channels.py --format json

# チャネル名で検索
poetry run python scripts/get_channels.py --search "general"

# 引数でBot Tokenを指定
poetry run python scripts/get_channels.py --bot-token xoxb-your-token
```

## ファイル構成
```
slack_posts_dumper/
├── src/                    # ソースコード
│   ├── slack_client.py     # Slack API連携
│   ├── html_generator.py   # HTML生成
│   ├── data_processor.py   # データ処理
│   └── main.py            # メイン処理
├── templates/              # HTMLテンプレート
├── static/                 # CSS/JSファイル
├── config/                 # 設定ファイル
└── output/                 # 生成されたHTMLファイル
```

## 環境変数
- `SLACK_BOT_TOKEN`: Slack Bot Token
- `OUTPUT_DIR`: 出力ディレクトリ
- `LOG_LEVEL`: ログレベル
- `DEBUG`: デバッグモード
- `DEFAULT_CHANNEL`: デフォルトチャネル
- `MAX_MESSAGES`: 最大メッセージ数

## ドキュメント作成ルール

### 出力例の記述
- **汎用性を重視**: 特定のワークスペース、ユーザー、チャネルを特定する情報は避ける
- **例示用の値を使用**: 実際のIDや名前ではなく、`T1234567890`、`My Workspace`、`U1234567890`などの汎用的な例を使用
- **プライバシー保護**: 実際のSlackワークスペース名、ユーザー名、URLなどの個人情報を含めない
- **一貫性を保つ**: 同じドキュメント内では同じ例示用の値を使用する

### 例示用の値
- **Workspace ID**: `T0000000001`
- **Channel ID**: `C0000000001`
- **User ID**: `U0000000001`
- **Workspace Name**: `Example Workspace`
- **Channel Name**: `general`
- **User Name**: `slack_bot`
- **Domain**: `example-workspace`
- **URL**: `https://example-workspace.slack.com/`

### ID判例のルール
- **Workspace ID**: `T0000000001` 形式（T + 10桁の0）
- **Channel ID**: `C0000000001` 形式（C + 10桁の0）
- **User ID**: `U0000000001` 形式（U + 10桁の0）
- **理由**: 実在するIDと明確に区別するため、連続した0を使用
- **注意**: 実際のSlack IDは英数字の組み合わせなので、0000000000は明らかに例示用 