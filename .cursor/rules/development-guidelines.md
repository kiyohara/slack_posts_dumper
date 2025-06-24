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

## 現在の開発環境（復元用）

### 環境情報
- **OS**: macOS (darwin 24.5.0)
- **Python**: 3.13.1 (pyenv管理)
- **Poetry**: 依存関係管理済み
- **Shell**: /opt/homebrew/bin/zsh
- **Workspace**: /Users/kiyohara/projects/slack_posts_dumper

### 復元に必要なコマンド
```bash
# プロジェクトディレクトリに移動
cd /Users/kiyohara/projects/slack_posts_dumper

# Poetry環境を復元
poetry install --no-root

# 動作確認
poetry run python scripts/get_channels.py --verbose

# 環境変数確認
cat .env
```

### 現在の設定状況
- **SLACK_BOT_TOKEN**: 設定済み（実際の値）
- **SLACK_WORKSPACE_ID**: 設定済み
- **SLACK_CHANNEL_ID**: 未設定
- **Git状態**: クリーン（コミット済み）

## ファイル構成
```
slack_posts_dumper/
├── README.md                    ✅
├── PROJECT_SPEC.md              ✅
├── PROGRESS.md                  ✅
├── pyproject.toml               ✅
├── poetry.lock                  ✅
├── .envrc                       ✅
├── env.example                  ✅
├── .gitignore                   ✅
├── .cursorignore                ✅
├── .cursor/rules/               ✅
│   ├── project-overview.md      ✅
│   ├── development-guidelines.md ✅
│   ├── implementation-notes.md  ✅
│   └── ai-assistant-rules.md    ✅
├── src/                         ✅
│   ├── __init__.py              ✅
│   ├── slack_checker.py         ✅
│   └── config/                  ✅
│       ├── __init__.py          ✅
│       └── settings.py          ✅
├── scripts/                     ✅
│   ├── check_slack_api.py       ✅
│   ├── get_workspace_id.py      ✅
│   └── get_channels.py          ✅
├── templates/                   ⏳ (今後実装)
├── static/                      ⏳ (今後実装)
└── output/                      ⏳ (今後実装)
```

## 環境変数
- `SLACK_BOT_TOKEN`: Slack Bot Token
- `SLACK_WORKSPACE_ID`: ワークスペースID（設定済み）
- `SLACK_CHANNEL_ID`: チャネルID（未設定）
- `OUTPUT_DIR`: 出力ディレクトリ
- `LOG_LEVEL`: ログレベル
- `DEBUG`: デバッグモード
- `DEFAULT_CHANNEL`: デフォルトチャネル
- `MAX_MESSAGES`: 最大メッセージ数

## ドキュメント作成ルール

### 出力例の記述
- **汎用性を重視**: 特定のワークスペース、ユーザー、チャネルを特定する情報は避ける
- **例示用の値を使用**: 実際のIDや名前ではなく、`T0000000001`、`Example Workspace`、`U0000000001`などの汎用的な例を使用
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

### プライバシー保護ルール
- **具体的なWorkspace名を保存しない**: 実際のワークスペース名をファイルに記録しない
- **具体的なWorkspace IDを保存しない**: 実際のWorkspace IDをファイルに記録しない
- **具体的なChannel IDを保存しない**: 実際のChannel IDをファイルに記録しない
- **理由**: プライバシー保護とセキュリティのため
- **代替記述**: 「設定済み」「成功」「正常動作」などの一般的な記述を使用
- **例外**: 例示用のID（T0000000001等）は使用可能

## Pythonコマンド実行ルール
- Pythonスクリプトを実行する際は、必ず `poetry run python ...` の形式で実行すること。
- 例: `poetry run python scripts/get_latest_message.py --format html`
- 直接 `python ...` で実行しないこと（仮想環境のパスや依存解決のため）。