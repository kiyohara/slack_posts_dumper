#!/usr/bin/env python3
"""絵文字解決ユーティリティテストスクリプト"""

import sys
import argparse
import os
from pathlib import Path
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.config.settings import get_slack_bot_token, validate_slack_token_format
from src.utils.emoji_resolver import create_emoji_resolver


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="絵文字解決ユーティリティテストツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境変数からBot Tokenを取得してテスト
  python scripts/test_emoji_resolver.py

  # 引数でBot Tokenを指定してテスト
  python scripts/test_emoji_resolver.py --bot-token xoxb-your-bot-token

  # 特定の絵文字をテスト
  python scripts/test_emoji_resolver.py --emoji "slightly_smiling_face"

  # テキスト内の絵文字置換をテスト
  python scripts/test_emoji_resolver.py --text "こんにちは :slightly_smiling_face: 今日は良い天気ですね :sunny:"

  # キャッシュTTLを変更してテスト
  python scripts/test_emoji_resolver.py --cache-ttl 1800

  # 強制リフレッシュでテスト
  python scripts/test_emoji_resolver.py --force-refresh

  # 詳細ログ出力
  python scripts/test_emoji_resolver.py --verbose
        """
    )
    
    parser.add_argument(
        '--bot-token',
        help='Slack Bot Token（環境変数SLACK_BOT_TOKENより優先）'
    )
    
    parser.add_argument(
        '--emoji',
        help='テスト対象の絵文字名（例: slightly_smiling_face）'
    )
    
    parser.add_argument(
        '--text',
        help='絵文字置換をテストするテキスト'
    )
    
    parser.add_argument(
        '--cache-ttl',
        type=int,
        default=3600,
        help='キャッシュの有効期限（秒、デフォルト: 3600）'
    )
    
    parser.add_argument(
        '--force-refresh',
        action='store_true',
        help='キャッシュを無視して強制的に再取得'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを出力'
    )
    
    return parser.parse_args()


def get_bot_token(bot_token_arg: Optional[str]) -> str:
    """Bot Tokenを取得（引数優先、次に環境変数）"""
    if bot_token_arg:
        return bot_token_arg
    
    return get_slack_bot_token()


def format_emoji_list(emoji_list: dict) -> str:
    """絵文字一覧を人間が読みやすい形式でフォーマット"""
    if not emoji_list:
        return "絵文字が見つかりませんでした。"
    
    lines = []
    lines.append("=== 絵文字一覧 ===")
    
    # 最初の10件を表示
    for i, (emoji_name, emoji_url) in enumerate(emoji_list.items()):
        if i >= 10:
            lines.append(f"... 他 {len(emoji_list) - 10}件")
            break
        lines.append(f":{emoji_name}: -> {emoji_url}")
    
    lines.append("==================")
    return "\n".join(lines)


def format_emoji_list_json(emoji_list: dict) -> str:
    """絵文字一覧をJSON形式でフォーマット"""
    import json
    return json.dumps(emoji_list, ensure_ascii=False, indent=2)


def test_emoji_resolver(bot_token: str, args) -> int:
    """EmojiResolverのテストを実行"""
    try:
        if not validate_slack_token_format(bot_token):
            raise ValueError("Bot Tokenの形式が正しくありません。xoxb-で始まる必要があります。")
        
        if args.verbose:
            print("Slackクライアントを初期化中...")
        
        client = WebClient(token=bot_token)
        
        if args.verbose:
            print(f"EmojiResolverを初期化中... (キャッシュTTL: {args.cache_ttl}秒)")
        
        # EmojiResolverインスタンスを作成
        resolver = create_emoji_resolver(client, cache_ttl=args.cache_ttl)
        
        # 絵文字一覧を取得
        print("絵文字一覧を取得中...")
        emoji_list = resolver.get_emoji_list(force_refresh=args.force_refresh)
        
        print(f"✅ 絵文字一覧取得完了: {len(emoji_list)}件")
        print()
        
        # 絵文字一覧を表示
        print(format_emoji_list(emoji_list))
        print()
        
        # 特定の絵文字をテスト
        if args.emoji:
            print(f"=== 絵文字 '{args.emoji}' のテスト ===")
            emoji_url = resolver.get_emoji_url(args.emoji, force_refresh=args.force_refresh)
            if emoji_url:
                print(f"絵文字名: :{args.emoji}:")
                print(f"URL: {emoji_url}")
                print(f"HTML: <img src=\"{emoji_url}\" alt=\":{args.emoji}:\" class=\"slack-emoji\">")
            else:
                print(f"❌ 絵文字 '{args.emoji}' が見つかりませんでした")
            print()
        
        # テキスト内の絵文字置換をテスト
        if args.text:
            print("=== テキスト内の絵文字置換テスト ===")
            print(f"元のテキスト: {args.text}")
            replaced_text = resolver.replace_emojis_in_text(args.text, force_refresh=args.force_refresh)
            print(f"置換後のテキスト: {replaced_text}")
            print()
        
        # キャッシュ情報を表示
        cache_info = resolver.get_cache_info()
        print("=== キャッシュ情報 ===")
        print(f"キャッシュ済み絵文字数: {cache_info['total_cached_emojis']}")
        print(f"キャッシュTTL: {cache_info['cache_ttl']}秒")
        print(f"キャッシュ経過時間: {cache_info['cache_age_seconds']:.1f}秒")
        print(f"キャッシュ有効: {'はい' if cache_info['is_cache_valid'] else 'いいえ'}")
        print()
        
        # 標準絵文字のテスト
        print("=== 標準絵文字のテスト ===")
        standard_emojis = ["slightly_smiling_face", "sunny", "heart", "thumbsup", "check"]
        for emoji in standard_emojis:
            emoji_url = resolver.get_emoji_url(emoji, force_refresh=args.force_refresh)
            print(f":{emoji}: -> {emoji_url}")
        print()
        
        print("✅ EmojiResolverテスト完了")
        return 0
        
    except SlackApiError as e:
        error_code = e.response.get("error", "unknown_error")
        if error_code == "invalid_auth":
            print("❌ Bot Tokenが無効です。正しいトークンを設定してください。")
        elif error_code == "token_revoked":
            print("❌ Bot Tokenが取り消されています。新しいトークンを取得してください。")
        elif error_code == "missing_scope":
            print("❌ Bot Tokenに必要な権限がありません。emoji:read権限が必要です。")
        else:
            print(f"❌ Slack API エラー: {error_code}")
        return 1
    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1


def main():
    """メイン関数"""
    args = parse_arguments()
    
    print("=== 絵文字解決ユーティリティテストツール ===")
    print()
    
    try:
        # Bot Tokenを取得
        bot_token = get_bot_token(args.bot_token)
        
        if args.verbose:
            print(f"Bot Token: {bot_token[:10]}...")
        
        # テストを実行
        return test_emoji_resolver(bot_token, args)
        
    except ValueError as e:
        print(f"❌ 設定エラー: {e}")
        return 1
    except Exception as e:
        print(f"❌ 予期しないエラーが発生しました: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 