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
- `SLACK_USER_TOKEN`: Slack User Token
- `OUTPUT_DIR`: 出力ディレクトリ
- `LOG_LEVEL`: ログレベル
- `DEBUG`: デバッグモード
- `DEFAULT_CHANNEL`: デフォルトチャネル
- `MAX_MESSAGES`: 最大メッセージ数 