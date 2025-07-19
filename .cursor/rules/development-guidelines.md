# 開発ガイドライン

## プロジェクト概要
**プロジェクト名**: Slack Posts Dumper  
**目的**: Slackチャネルの投稿をHTMLとして保存するツール  
**技術スタック**: Python 3.13.1, Poetry, Slack SDK, Jinja2, bleach

## 開発環境設定

### 必須ツール
- **Python**: 3.13.1 (pyenv管理)
- **依存管理**: Poetry
- **環境変数**: direnv + .env
- **エディタ**: Cursor Editor推奨

### 環境構築手順
```bash
# Python環境設定
pyenv local 3.13.1

# Poetry環境構築
poetry install --no-root

# 環境変数設定
cp env.example .env
# .envファイルを編集してSlack APIトークンを設定

# direnv有効化
direnv allow
```

## コーディング規約

### Python
- **フォーマッター**: Black
- **リンター**: flake8
- **型ヒント**: 必須
- **ドキュメント文字列**: 必須

### ファイル構成
```
src/
├── config/           # 設定管理
├── utils/            # ユーティリティ
│   ├── user_resolver.py    # ユーザー情報解決
│   └── emoji_resolver.py   # 絵文字置換
├── slack_checker.py  # Slack API接続確認
└── message_renderer.py     # HTMLレンダリング
```

## Slack API 開発ガイドライン

### 必要な権限（Bot Token Scopes）
- `channels:history` - チャネルの履歴を読み取り
- `channels:read` - チャネル情報を読み取り
- `users:read` - ユーザー情報を読み取り
- `files:read` - ファイル情報を読み取り
- `emoji:read` - 絵文字情報を読み取り（絵文字置換機能用）

### 主要APIメソッド
- **認証**: `auth.test` - ワークスペース情報取得
- **チャネル**: `conversations.list`, `conversations.history`
- **ユーザー**: `users.info`, `users.list`
- **絵文字**: `emoji.list` - カスタム絵文字一覧取得
- **ファイル**: `files.info`, `files.list`

### エラーハンドリング
- レート制限対応（指数バックオフ）
- ネットワークエラー処理
- API権限エラー処理
- データ不整合対応

### キャッシュ戦略
- **ユーザー情報**: TTL 1時間
- **絵文字情報**: TTL 1時間
- **チャネル情報**: TTL 30分

## HTMLフィルターパイプライン設計

### フィルター処理順序
1. **絵文字置換** - `:emoji:` → `<img>`タグ
2. **改行処理** - `\n` → `<br>`タグ
3. **HTMLサニタイズ** - 許可されたタグのみ残す
4. **安全出力** - HTMLとして出力

### 許可されたHTMLタグ
- `img` - 絵文字画像用
- `br` - 改行用
- `a` - リンク用
- `strong`, `em` - 強調用
- `code`, `pre` - コード用

### 安全性
- bleachライブラリによるXSS対策
- 許可されたタグ・属性のみ出力
- 危険なタグ（script, iframe等）の自動除去

### 拡張性
- 新しいフィルターを簡単に追加可能
- 処理順序の柔軟な変更
- モジュラーな設計

## コンポーネント設計

### EmojiResolver（絵文字置換）
```python
class EmojiResolver:
    def __init__(self, ttl_hours: int = 1):
        # TTL制御付きキャッシュ初期化
    
    def get_emoji_list(self) -> Dict[str, str]:
        # Slack API emoji.list呼び出し
    
    def replace_emojis(self, text: str) -> str:
        # 絵文字キーワードを画像URLに置換
```

### UserResolver（ユーザー情報解決）
```python
class UserResolver:
    def __init__(self, ttl_hours: int = 1):
        # TTL制御付きキャッシュ初期化
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        # ユーザーIDからユーザー情報を取得
    
    def get_display_name(self, user_info: Dict[str, Any]) -> str:
        # 表示名の自動解決（優先順位: 表示名 > 実名 > ユーザー名）
```

### SlackMessageHtmlRenderer（HTMLレンダリング）
```python
class SlackMessageHtmlRenderer:
    def __init__(self):
        # Jinja2環境初期化
        # フィルター登録
    
    def render_message(self, message: Dict[str, Any]) -> str:
        # メッセージをHTML形式でレンダリング
```

## テスト戦略

### 単体テスト
- 各コンポーネントの独立テスト
- モックを使用したAPI呼び出しテスト
- エラーハンドリングテスト

### 統合テスト
- 実際のSlack API接続テスト
- フィルターパイプライン全体のテスト
- HTML出力の検証

### 手動テスト
- 実際のSlackワークスペースでの動作確認
- 絵文字置換の視覚的確認
- HTMLサニタイズの安全性確認

## セキュリティ考慮事項

### APIトークン管理
- .envファイルによる安全な管理
- .gitignoreによる除外
- 最小権限の原則

### HTMLサニタイズ
- bleachライブラリによるXSS対策
- 許可されたタグのみ出力
- 危険な属性の除去

### データ保護
- 個人情報の適切な取り扱い
- キャッシュのTTL制御
- ログ出力の制限

## パフォーマンス考慮事項

### API制限対応
- レート制限の監視
- 指数バックオフ
- バッチ処理の検討

### キャッシュ最適化
- 適切なTTL設定
- メモリ使用量の監視
- キャッシュ無効化戦略

## デバッグ・ログ

### ログレベル
- **DEBUG**: 詳細な処理情報
- **INFO**: 一般的な処理情報
- **WARNING**: 警告（処理は継続）
- **ERROR**: エラー（処理中断）

### デバッグツール
- `scripts/test_emoji_resolver.py` - 絵文字置換テスト
- `scripts/test_user_resolver.py` - ユーザー情報解決テスト
- `scripts/get_latest_message.py --verbose` - 詳細ログ出力

## 今後の拡張計画

### Phase 1: 基本機能実装（完了）
- [x] 環境構築・プロジェクト基盤
- [x] Slack API接続・基本機能
- [x] ユーザー情報解決
- [x] 絵文字置換機能
- [x] HTMLフィルターパイプライン

### Phase 2: UI/UX改善（進行中）
- [x] Slack風デザイン実装
- [x] 絵文字表示機能
- [x] 改行処理機能
- [ ] URLリンク処理機能
- [ ] レスポンシブ対応

### Phase 3: 高度な機能（計画中）
- [ ] 添付ファイル対応
- [ ] スレッド表示
- [ ] リアクション表示
- [ ] 検索機能
- [ ] エクスポート機能

## 参考資料

### ドキュメント
- [プロジェクト仕様書](PROJECT_SPEC.md)
- [開発進捗状況](PROGRESS.md)
- [Slack API詳細リファレンス](docs/slack_api_reference.md)

### 外部リンク
- [Slack API Methods](https://api.slack.com/methods)
- [Slack API Reference](https://api.slack.com/web)
- [bleach Documentation](https://bleach.readthedocs.io/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)