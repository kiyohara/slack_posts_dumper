#!/usr/bin/env python3
"""最新メッセージ取得スクリプト"""

import sys
import argparse
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from src.config.settings import (
    get_slack_bot_token, 
    get_workspace_id, 
    get_channel_id,
    validate_slack_token_format,
    validate_channel_id_format,
    validate_workspace_id_format
)


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="Slack チャネルの最新メッセージ取得ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境変数から設定を取得して最新メッセージを表示
  python scripts/get_latest_message.py

  # 引数でチャネルIDを指定
  python scripts/get_latest_message.py --channel-id C1234567890

  # 引数でワークスペースIDとチャネルIDを指定
  python scripts/get_latest_message.py --workspace-id T1234567890 --channel-id C1234567890

  # 詳細ログ出力
  python scripts/get_latest_message.py --verbose

  # JSON形式で出力
  python scripts/get_latest_message.py --format json
        """
    )
    
    parser.add_argument(
        '--bot-token',
        help='Slack Bot Token（環境変数SLACK_BOT_TOKENより優先）'
    )
    
    parser.add_argument(
        '--workspace-id',
        help='ワークスペースID（環境変数SLACK_WORKSPACE_IDより優先）'
    )
    
    parser.add_argument(
        '--channel-id',
        help='チャネルID（環境変数SLACK_CHANNEL_IDより優先）'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを出力'
    )
    
    parser.add_argument(
        '--format',
        choices=['human', 'json'],
        default='human',
        help='出力形式（デフォルト: human）'
    )
    
    return parser.parse_args()


def get_bot_token(args_bot_token: Optional[str] = None) -> str:
    """Bot Tokenを取得（引数 > 環境変数の優先順位）"""
    if args_bot_token:
        return args_bot_token
    
    return get_slack_bot_token()


def get_latest_message(
    bot_token: str, 
    channel_id: str, 
    verbose: bool = False
) -> Optional[Dict[str, Any]]:
    """指定したチャネルの最新メッセージを取得"""
    try:
        if not validate_slack_token_format(bot_token):
            raise ValueError("Bot Tokenの形式が正しくありません。xoxb-で始まる必要があります。")
        
        if not validate_channel_id_format(channel_id):
            raise ValueError("チャネルIDの形式が正しくありません。Cで始まる必要があります。")
        
        if verbose:
            print("Slackクライアントを初期化中...")
        
        client = WebClient(token=bot_token)
        
        if verbose:
            print(f"conversations.history APIを呼び出し中... (チャネル: {channel_id})")
        
        # conversations.history APIを呼び出して最新メッセージを取得
        response = client.conversations_history(
            channel=channel_id,
            limit=1  # 最新1件のみ取得
        )
        
        if not response["ok"]:
            raise Exception(f"conversations.history APIが失敗しました: {response.get('error', 'Unknown error')}")
        
        messages = response.get("messages", [])
        
        if verbose:
            print(f"取得したメッセージ数: {len(messages)}")
        
        if not messages:
            return None
        
        return messages[0]
        
    except SlackApiError as e:
        error_code = e.response.get("error", "unknown_error")
        if error_code == "invalid_auth":
            raise Exception("Bot Tokenが無効です。正しいトークンを設定してください。")
        elif error_code == "token_revoked":
            raise Exception("Bot Tokenが取り消されています。新しいトークンを取得してください。")
        elif error_code == "missing_scope":
            raise Exception("Bot Tokenに必要な権限がありません。channels:history権限が必要です。")
        elif error_code == "channel_not_found":
            raise Exception(f"チャネルが見つかりません: {channel_id}")
        elif error_code == "not_in_channel":
            raise Exception(f"Botがチャネルに参加していません: {channel_id}")
        else:
            raise Exception(f"Slack API エラー: {error_code}")
    except Exception as e:
        raise Exception(f"メッセージの取得に失敗しました: {e}")


def format_message_human(message: Dict[str, Any]) -> str:
    """メッセージを人間が読みやすい形式で整形"""
    # タイムスタンプを日時に変換
    ts = float(message.get("ts", 0))
    message_time = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    
    # ユーザー情報
    user_id = message.get("user", "Unknown")
    username = message.get("username", "Unknown")
    
    # メッセージ内容
    text = message.get("text", "")
    
    # 添付ファイル情報
    files = message.get("files", [])
    file_info = ""
    if files:
        file_names = [f.get("name", "Unknown") for f in files]
        file_info = f"\n添付ファイル: {', '.join(file_names)}"
    
    # リアクション情報
    reactions = message.get("reactions", [])
    reaction_info = ""
    if reactions:
        reaction_texts = [f"{r.get('name', '?')}:{r.get('count', 0)}" for r in reactions]
        reaction_info = f"\nリアクション: {', '.join(reaction_texts)}"
    
    # スレッド情報
    thread_ts = message.get("thread_ts")
    thread_info = ""
    if thread_ts:
        thread_info = "\n（スレッド返信）"
    
    # 整形されたメッセージ
    formatted = f"""
=== 最新メッセージ ===
投稿日時: {message_time}
投稿者: {username} ({user_id})
内容:
{text}{file_info}{reaction_info}{thread_info}
"""
    
    return formatted.strip()


def format_message_json(message: Dict[str, Any]) -> str:
    """メッセージをJSON形式で整形"""
    import json
    
    # タイムスタンプを日時に変換
    ts = float(message.get("ts", 0))
    message_time = datetime.fromtimestamp(ts).isoformat()
    
    # 必要な情報のみを抽出
    simplified_message = {
        "ts": message.get("ts"),
        "datetime": message_time,
        "user": message.get("user"),
        "username": message.get("username"),
        "text": message.get("text"),
        "files": message.get("files", []),
        "reactions": message.get("reactions", []),
        "thread_ts": message.get("thread_ts"),
        "is_thread_reply": bool(message.get("thread_ts")),
        "type": message.get("type")
    }
    
    return json.dumps(simplified_message, ensure_ascii=False, indent=2)


def main():
    """メイン関数"""
    args = parse_arguments()
    
    print("=== Slack 最新メッセージ取得ツール ===")
    print()
    
    try:
        # 設定値を取得
        bot_token = get_bot_token(args.bot_token)
        workspace_id = get_workspace_id(args.workspace_id)
        channel_id = get_channel_id(args.channel_id)
        
        if args.verbose:
            print(f"Bot Token: {bot_token[:10]}...")
            print(f"Workspace ID: {workspace_id}")
            print(f"Channel ID: {channel_id}")
            print()
        
        # 最新メッセージを取得
        message = get_latest_message(bot_token, channel_id, args.verbose)
        
        if not message:
            print("メッセージが見つかりませんでした。")
            return
        
        # メッセージを表示
        if args.format == 'json':
            print(format_message_json(message))
        else:
            print(format_message_human(message))
        
    except ValueError as e:
        print(f"設定エラー: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 