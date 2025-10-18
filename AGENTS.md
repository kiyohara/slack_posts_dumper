# リポジトリガイドライン

## プロジェクト構成とモジュール整理
中核のロジックは `src/` にあり、`slack_checker.py` が API へのアクセスを調整し、`message_renderer.py` が HTML 出力を整形します。ヘルパーは `utils/` と `config/settings.py` に分かれています。フェッチャーや回帰テストなどの CLI 風ユーティリティは `scripts/` にまとまっています。HTML および README のテンプレートは `templates/` に配置されています。生成されたエクスポートは `output/` に保持し、背景資料や参照情報は `docs/` にまとめてください。

## ビルド・テスト・開発コマンド
- `poetry install` — 仮想環境とロックファイルの依存関係をセットアップします。
- `poetry run python scripts/get_channels.py --token "$SLACK_BOT_TOKEN"` — 利用可能なチャンネルを列挙し、認証情報を確認します。
- `poetry run python scripts/get_latest_message.py --channel general --format local` — 最新のメッセージを `output/` に書き出します。
- `poetry run pytest` — ダウンロードとレンダーのヘルパーを検証する回帰スイートを実行します。
- `poetry run black src scripts` および `poetry run flake8 src scripts` — PR を作成する前にフォーマットとリンタを実行します。

## コーディングスタイルと命名規則
インデントは 4 スペース、文字列は UTF-8 セーフで扱ってください。モジュールはアンダースコア区切りの小文字、クラスはパスカルケース、関数や変数はスネークケースを使用します。`templates/message.html` で定義された Jinja ブロック名を踏襲し、レンダラーテンプレートの一貫性を保ってください。可能な場合はデータクラス風の DTO を採用し、Slack API のレスポンスには明示的なエラーハンドリングを加えます。

## テストガイドライン
Pytest は `scripts/test_*.py` のテストを検出します。新しいファイルや関数には自動検出されるように `test_` 接頭辞を付けてください。認証情報の欠如やレート制限などの境界ケース、絵文字フォールバックやリンクのサニタイズといったレンダリング回帰をカバーすることを目指します。テストで API フィクスチャが必要な場合は、実呼び出しではなく VCR 形式のカセットやスタブレスポンスを優先してください。全体実行の前にポイント確認を行うときは `poetry run pytest -k your_feature` を利用します。

## コミットとプルリクエストのガイドライン
従来の Conventional Commit スタイル（`feat:`、`fix:`、`refactor:`、`docs:`）に従い、簡潔で説明的なサマリを付けてください。変更の理解を助ける場合は日本語の文脈説明も添えます。各 PR では関連する仕様（`PROJECT_SPEC.md` を参照）へのリンク、設定変更の説明、レンダラーが変わる場合はマスク済みのスクリーンショットや HTML スニペットを添付してください。挙動が変化した際には `README.md` やテンプレートも更新し、CI フレンドリーなコマンド（`pytest`、`black`、`flake8`）がローカルで成功することを確認します。

## 設定とセキュリティに関する注意
`env.example` を `.env` にコピーし、スクリプトを実行する前に Slack トークンとワークスペース ID を設定してください。トークンは機密情報として扱い、コミットには含めず、コマンドを実行するときは環境変数のエクスポート（`export SLACK_BOT_TOKEN=...`）を利用してください。チーム外に成果物を共有する前に、`output/` から機密情報を取り除いてください。
