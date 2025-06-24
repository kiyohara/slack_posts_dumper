# AIアシスタント用ルール

## 基本方針
- **言語**: 日本語で応答
- **プロジェクト理解**: このプロジェクトはSlackチャネルの投稿をHTMLとして保存するツール
- **技術スタック**: Python + Poetry + pyenv + direnv

## 開発環境の理解
- **Python**: 3.13.1 (pyenv管理)
- **依存管理**: Poetry (`pyproject.toml`/`poetry.lock`)
- **環境変数**: direnv + .env
- **仮想環境**: Poetry仮想環境（自動有効化）

## コーディング規約
- **フォーマッター**: Black
- **リンター**: flake8
- **テスト**: pytest
- **ファイル構成**: src/, templates/, static/, config/, output/

## 実装時の注意点
1. **Slack API**: レート制限、ページネーション対応
2. **セキュリティ**: APIトークンの適切な管理
3. **パフォーマンス**: 大量データ処理の最適化
4. **UI/UX**: Slack風デザインの再現

## 推奨される実装順序
1. **Phase 1**: 基本機能（Slack API接続、データ取得、基本HTML出力）
2. **Phase 2**: UI/UX改善（デザイン、レスポンシブ、インタラクティブ機能）
3. **Phase 3**: 高度な機能（添付ファイル、スレッド、検索、エクスポート）

## 環境変数の理解
- `SLACK_BOT_TOKEN`: Slack Bot Token
- `SLACK_USER_TOKEN`: Slack User Token
- `OUTPUT_DIR`: 出力ディレクトリ
- `LOG_LEVEL`: ログレベル
- `DEBUG`: デバッグモード
- `DEFAULT_CHANNEL`: デフォルトチャネル
- `MAX_MESSAGES`: 最大メッセージ数

## 開発コマンドの理解
```bash
poetry install          # 依存関係インストール
poetry add パッケージ名    # 依存関係追加
poetry run black .      # コードフォーマット
poetry run flake8 .     # リンター
poetry run pytest       # テスト実行
```

## ファイル管理の理解
- `.env`: 環境変数（Git除外）
- `env.example`: 環境変数サンプル
- `pyproject.toml`: Poetry設定
- `poetry.lock`: 依存関係ロック
- `.envrc`: direnv設定
- `output/`: 生成されたHTMLファイル（Git除外） 