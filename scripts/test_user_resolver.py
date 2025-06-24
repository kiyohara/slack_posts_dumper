#!/usr/bin/env python3
"""UserResolverテストスクリプト"""

import sys
import argparse
import os
from pathlib import Path
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slack_sdk import WebClient
from src.config.settings import get_slack_bot_token, validate_slack_token_format
from src.utils.user_resolver import UserResolver, create_user_resolver


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="UserResolverテストツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境変数から設定を取得してテスト
  python scripts/test_user_resolver.py

  # 特定のユーザーIDを指定してテスト
  python scripts/test_user_resolver.py --user-id U1234567890

  # キャッシュTTLを変更してテスト
  python scripts/test_user_resolver.py --cache-ttl 1800

  # 強制リフレッシュでテスト
  python scripts/test_user_resolver.py --force-refresh
        """
    )
    
    parser.add_argument(
        '--bot-token',
        help='Slack Bot Token（環境変数SLACK_BOT_TOKENより優先）'
    )
    
    parser.add_argument(
        '--user-id',
        help='テスト対象のユーザーID'
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


def test_user_resolver(bot_token: str, user_id: Optional[str] = None, cache_ttl: int = 3600, 
                      force_refresh: bool = False, verbose: bool = False):
    """UserResolverのテストを実行"""
    
    if not validate_slack_token_format(bot_token):
        raise ValueError("Bot Tokenの形式が正しくありません。xoxb-で始まる必要があります。")
    
    if verbose:
        print("Slackクライアントを初期化中...")
    
    client = WebClient(token=bot_token)
    
    if verbose:
        print(f"UserResolverを初期化中... (キャッシュTTL: {cache_ttl}秒)")
    
    # UserResolverインスタンスを作成
    resolver = create_user_resolver(client, cache_ttl)
    
    # テスト用のユーザーID（指定されていない場合は自分自身）
    if not user_id:
        try:
            if verbose:
                print("auth.test APIを呼び出し中...")
            
            auth_response = client.auth_test()
            if auth_response["ok"]:
                user_id = auth_response.get("user_id")
                if verbose:
                    print(f"現在のユーザーID: {user_id}")
            else:
                raise Exception("auth.test APIが失敗しました")
        except Exception as e:
            print(f"ユーザーIDの取得に失敗: {e}")
            print("--user-idオプションでユーザーIDを指定してください。")
            return
    
    # user_idがNoneの場合は処理を終了
    if not user_id:
        print("ユーザーIDが取得できませんでした。")
        return
    
    print(f"=== UserResolverテスト ===")
    print(f"テスト対象ユーザーID: {user_id}")
    print(f"キャッシュTTL: {cache_ttl}秒")
    print(f"強制リフレッシュ: {force_refresh}")
    print()
    
    try:
        # 1. ユーザー情報の取得テスト
        print("1. ユーザー情報の取得テスト")
        print("-" * 40)
        
        user_info = resolver.get_user_info(user_id, force_refresh)
        
        if user_info:
            print("✓ ユーザー情報の取得に成功")
            print(f"  ユーザーID: {user_info.get('id')}")
            print(f"  表示名: {user_info.get('display_name')}")
            print(f"  実名: {user_info.get('profile', {}).get('real_name')}")
            print(f"  ユーザー名: {user_info.get('name')}")
            print(f"  メールアドレス: {user_info.get('profile', {}).get('email', 'N/A')}")
        else:
            print("✗ ユーザー情報の取得に失敗")
            return
        
        print()
        
        # 2. 個別メソッドのテスト
        print("2. 個別メソッドのテスト")
        print("-" * 40)
        
        display_name = resolver.get_user_display_name(user_id, force_refresh)
        real_name = resolver.get_user_real_name(user_id, force_refresh)
        username = resolver.get_user_username(user_id, force_refresh)
        
        print(f"表示名: {display_name}")
        print(f"実名: {real_name}")
        print(f"ユーザー名: {username}")
        
        # 新しく追加したメソッドのテスト
        avatar_url = resolver.get_user_avatar_url(user_id, force_refresh)
        status_emoji = resolver.get_user_status_emoji(user_id, force_refresh)
        status_text = resolver.get_user_status_text(user_id, force_refresh)
        email = resolver.get_user_email(user_id, force_refresh)
        team_id = resolver.get_user_team_id(user_id, force_refresh)
        is_bot = resolver.get_user_is_bot(user_id, force_refresh)
        is_deleted = resolver.get_user_is_deleted(user_id, force_refresh)
        
        print(f"アバターURL: {avatar_url or 'N/A'}")
        print(f"ステータス絵文字: {status_emoji or 'N/A'}")
        print(f"ステータステキスト: {status_text or 'N/A'}")
        print(f"メールアドレス: {email or 'N/A'}")
        print(f"チームID: {team_id or 'N/A'}")
        print(f"Bot: {is_bot}")
        print(f"削除済み: {is_deleted}")
        
        # アバター画像のサイズ別テスト
        print()
        print("アバター画像サイズ別テスト:")
        for size in ["24", "32", "48", "72", "192", "512", "1024"]:
            avatar_url_size = resolver.get_user_avatar_url(user_id, force_refresh, size)
            if avatar_url_size:
                print(f"  サイズ{size}: {avatar_url_size}")
            else:
                print(f"  サイズ{size}: 利用不可")
        
        print()
        
        # 3. キャッシュ機能のテスト
        print("3. キャッシュ機能のテスト")
        print("-" * 40)
        
        # 初回取得（キャッシュに保存される）
        start_time = time.time()
        resolver.get_user_info(user_id, force_refresh=False)
        first_call_time = time.time() - start_time
        
        # 2回目取得（キャッシュから取得）
        start_time = time.time()
        resolver.get_user_info(user_id, force_refresh=False)
        second_call_time = time.time() - start_time
        
        print(f"初回取得時間: {first_call_time:.4f}秒")
        print(f"2回目取得時間: {second_call_time:.4f}秒")
        print(f"キャッシュ効果: {first_call_time / second_call_time:.1f}倍高速")
        
        print()
        
        # 4. キャッシュ情報の表示
        print("4. キャッシュ情報")
        print("-" * 40)
        
        cache_info = resolver.get_cache_info()
        print(f"キャッシュ済みユーザー数: {cache_info['total_cached_users']}")
        print(f"有効キャッシュ数: {cache_info['valid_cache_count']}")
        print(f"期限切れキャッシュ数: {cache_info['expired_cache_count']}")
        print(f"キャッシュTTL: {cache_info['cache_ttl']}秒")
        
        print()
        
        # 5. キャッシュクリアのテスト
        print("5. キャッシュクリアのテスト")
        print("-" * 40)
        
        print("キャッシュクリア前:")
        cache_info_before = resolver.get_cache_info()
        print(f"  キャッシュ済みユーザー数: {cache_info_before['total_cached_users']}")
        
        resolver.clear_cache()
        
        print("キャッシュクリア後:")
        cache_info_after = resolver.get_cache_info()
        print(f"  キャッシュ済みユーザー数: {cache_info_after['total_cached_users']}")
        
        print()
        print("=== テスト完了 ===")
        
    except Exception as e:
        print(f"テスト実行中にエラーが発生しました: {e}")
        return


def main():
    """メイン関数"""
    args = parse_arguments()
    
    try:
        # Bot Tokenを取得
        bot_token = args.bot_token if args.bot_token else get_slack_bot_token()
        
        # UserResolverテストを実行
        test_user_resolver(
            bot_token=bot_token,
            user_id=args.user_id,
            cache_ttl=args.cache_ttl,
            force_refresh=args.force_refresh,
            verbose=args.verbose
        )
        
    except ValueError as e:
        print(f"設定エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import time
    main() 