#!/usr/bin/env python3
"""チャネル一覧取得スクリプト"""

import sys
import argparse
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.config.settings import get_slack_bot_token, validate_slack_token_format


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="Slack チャネル一覧取得ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境変数からBot Tokenを取得してチャネル一覧を表示
  python scripts/get_channels.py

  # 引数でBot Tokenを指定
  python scripts/get_channels.py --bot-token xoxb-your-bot-token

  # 詳細ログ出力
  python scripts/get_channels.py --verbose

  # JSON形式で出力
  python scripts/get_channels.py --format json

  # チャネル名で検索
  python scripts/get_channels.py --search "general"
        """
    )
    
    parser.add_argument(
        '--bot-token',
        help='Slack Bot Token（環境変数SLACK_BOT_TOKENより優先）'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを出力'
    )
    
    parser.add_argument(
        '--format',
        choices=['table', 'json'],
        default='table',
        help='出力形式（デフォルト: table）'
    )
    
    parser.add_argument(
        '--search',
        help='チャネル名で検索（部分一致）'
    )
    
    return parser.parse_args()


def get_bot_token(args_bot_token: Optional[str] = None) -> str:
    """Bot Tokenを取得（引数 > 環境変数の優先順位）"""
    if args_bot_token:
        return args_bot_token
    
    return get_slack_bot_token()


def get_channels_list(bot_token: str, verbose: bool = False) -> List[Dict[str, Any]]:
    """Bot Tokenを使ってチャネル一覧を取得"""
    try:
        if not validate_slack_token_format(bot_token):
            raise ValueError("Bot Tokenの形式が正しくありません。xoxb-で始まる必要があります。")
        
        if verbose:
            print("Slackクライアントを初期化中...")
        
        client = WebClient(token=bot_token)
        
        if verbose:
            print("conversations.list APIを呼び出し中...")
        
        # conversations.list APIを呼び出してチャネル一覧を取得
        # パブリックチャネルのみを取得
        response = client.conversations_list(
            types="public_channel",
            limit=1000  # 最大1000件取得
        )
        
        if not response["ok"]:
            raise Exception(f"conversations.list APIが失敗しました: {response.get('error', 'Unknown error')}")
        
        channels = response.get("channels", [])
        
        if verbose:
            print(f"取得したチャネル数: {len(channels)}")
        
        return channels
        
    except SlackApiError as e:
        error_code = e.response.get("error", "unknown_error")
        if error_code == "invalid_auth":
            raise Exception("Bot Tokenが無効です。正しいトークンを設定してください。")
        elif error_code == "token_revoked":
            raise Exception("Bot Tokenが取り消されています。新しいトークンを取得してください。")
        elif error_code == "missing_scope":
            raise Exception("Bot Tokenに必要な権限がありません。channels:read権限が必要です。")
        else:
            raise Exception(f"Slack API エラー: {error_code}")
    except Exception as e:
        raise Exception(f"チャネル一覧の取得に失敗しました: {e}")


def filter_channels_by_search(channels: List[Dict[str, Any]], search_term: str) -> List[Dict[str, Any]]:
    """チャネル名で検索してフィルタリング"""
    if not search_term:
        return channels
    
    search_term_lower = search_term.lower()
    filtered_channels = []
    
    for channel in channels:
        channel_name = channel.get("name", "").lower()
        if search_term_lower in channel_name:
            filtered_channels.append(channel)
    
    return filtered_channels


def format_channels_table(channels: List[Dict[str, Any]]) -> str:
    """チャネル一覧をテーブル形式で整形"""
    if not channels:
        return "チャネルが見つかりませんでした。"
    
    # ヘッダー
    header = f"{'チャネル名':<20} {'チャネルID':<15} {'メンバー数':<10} {'説明':<30}"
    separator = "-" * 80
    
    # チャネル情報
    rows = []
    for channel in channels:
        name = channel.get("name", "Unknown")[:19]
        channel_id = channel.get("id", "Unknown")
        num_members = str(channel.get("num_members", 0))
        purpose = channel.get("purpose", {}).get("value", "")[:29]
        
        row = f"{name:<20} {channel_id:<15} {num_members:<10} {purpose:<30}"
        rows.append(row)
    
    # テーブルを組み立て
    table = f"{header}\n{separator}\n" + "\n".join(rows)
    
    return table


def format_channels_json(channels: List[Dict[str, Any]]) -> str:
    """チャネル一覧をJSON形式で整形"""
    import json
    
    # 必要な情報のみを抽出
    simplified_channels = []
    for channel in channels:
        simplified_channel = {
            "name": channel.get("name"),
            "id": channel.get("id"),
            "num_members": channel.get("num_members"),
            "purpose": channel.get("purpose", {}).get("value", ""),
            "topic": channel.get("topic", {}).get("value", ""),
            "is_private": channel.get("is_private", False),
            "is_archived": channel.get("is_archived", False)
        }
        simplified_channels.append(simplified_channel)
    
    return json.dumps(simplified_channels, ensure_ascii=False, indent=2)


def main():
    """メイン関数"""
    args = parse_arguments()
    
    print("=== Slack チャネル一覧取得ツール ===")
    print()
    
    try:
        # Bot Tokenを取得
        bot_token = get_bot_token(args.bot_token)
        
        if args.verbose:
            print(f"Bot Token: {bot_token[:10]}...")
        
        # チャネル一覧を取得
        channels = get_channels_list(bot_token, args.verbose)
        
        # 検索フィルタリング
        if args.search:
            channels = filter_channels_by_search(channels, args.search)
            if args.verbose:
                print(f"検索結果: '{args.search}' に一致するチャネル数: {len(channels)}")
        
        # 結果を表示
        if args.format == 'json':
            print(format_channels_json(channels))
        else:
            print(format_channels_table(channels))
        
        print()
        print(f"✅ 取得完了: {len(channels)}件のチャネル")
        
        if args.format == 'table' and channels:
            print()
            print("チャネルIDを使用する際は、以下の形式で.envファイルに設定してください:")
            print("SLACK_CHANNEL_ID=C1234567890")
        
        return 0
        
    except ValueError as e:
        print(f"❌ 設定エラー: {e}")
        return 1
    except Exception as e:
        print(f"❌ エラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 