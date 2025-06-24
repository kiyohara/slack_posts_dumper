#!/usr/bin/env python3
"""Workspace ID取得スクリプト"""

import sys
import argparse
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="Slack Workspace ID取得ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境変数からBot Tokenを取得
  python scripts/get_workspace_id.py

  # 引数でBot Tokenを指定
  python scripts/get_workspace_id.py --bot-token xoxb-your-bot-token

  # 詳細ログ出力
  python scripts/get_workspace_id.py --verbose

  # JSON形式で出力
  python scripts/get_workspace_id.py --format json
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
        choices=['human', 'json'],
        default='human',
        help='出力形式（デフォルト: human）'
    )
    
    return parser.parse_args()


def get_bot_token(args_bot_token: str = None) -> str:
    """Bot Tokenを取得（引数 > 環境変数の優先順位）"""
    if args_bot_token:
        return args_bot_token
    
    env_bot_token = os.getenv('SLACK_BOT_TOKEN')
    if env_bot_token:
        return env_bot_token
    
    raise ValueError(
        "Bot Tokenが指定されていません。"
        "引数または環境変数SLACK_BOT_TOKENを設定してください。"
    )


def validate_bot_token_format(token: str) -> bool:
    """Bot Tokenの形式を検証"""
    if not token.startswith('xoxb-'):
        return False
    return len(token) > 10


def get_workspace_info(bot_token: str, verbose: bool = False) -> dict:
    """Bot Tokenを使ってWorkspace情報を取得"""
    try:
        if not validate_bot_token_format(bot_token):
            raise ValueError("Bot Tokenの形式が正しくありません。xoxb-で始まる必要があります。")
        
        if verbose:
            print("Slackクライアントを初期化中...")
        
        client = WebClient(token=bot_token)
        
        if verbose:
            print("auth.test APIを呼び出し中...")
        
        # auth.test APIを呼び出してWorkspace情報を取得
        response = client.auth_test()
        
        if not response["ok"]:
            raise Exception(f"auth.test APIが失敗しました: {response.get('error', 'Unknown error')}")
        
        workspace_info = {
            "team_id": response.get("team_id"),
            "team": response.get("team"),
            "team_domain": response.get("team_domain"),
            "user_id": response.get("user_id"),
            "user": response.get("user"),
            "url": response.get("url")
        }
        
        return workspace_info
        
    except SlackApiError as e:
        error_code = e.response.get("error", "unknown_error")
        if error_code == "invalid_auth":
            raise Exception("Bot Tokenが無効です。正しいトークンを設定してください。")
        elif error_code == "token_revoked":
            raise Exception("Bot Tokenが取り消されています。新しいトークンを取得してください。")
        else:
            raise Exception(f"Slack API エラー: {error_code}")
    except Exception as e:
        raise Exception(f"Workspace情報の取得に失敗しました: {e}")


def format_workspace_info(workspace_info: dict) -> str:
    """Workspace情報を整形して表示"""
    formatted = f"""
=== Workspace情報 ===
Team ID: {workspace_info.get('team_id', 'Unknown')}
Team Name: {workspace_info.get('team', 'Unknown')}
Team Domain: {workspace_info.get('team_domain', 'Unknown')}
User ID: {workspace_info.get('user_id', 'Unknown')}
User Name: {workspace_info.get('user', 'Unknown')}
URL: {workspace_info.get('url', 'Unknown')}
===================
"""
    return formatted


def format_workspace_info_json(workspace_info: dict) -> str:
    import json
    return json.dumps(workspace_info, ensure_ascii=False, indent=2)


def main():
    """メイン関数"""
    args = parse_arguments()
    
    # JSONフォーマットの場合はツール名などの出力を抑止
    if args.format != 'json':
        print("=== Slack Workspace ID取得ツール ===")
        print()
    
    try:
        # Bot Tokenを取得
        bot_token = get_bot_token(args.bot_token)
        
        if args.verbose and args.format != 'json':
            print(f"Bot Token: {bot_token[:10]}...")
        
        # Workspace情報を取得
        workspace_info = get_workspace_info(bot_token, args.verbose)
        
        # 結果を表示
        if args.format == 'json':
            print(format_workspace_info_json(workspace_info))
        else:
            print(format_workspace_info(workspace_info))
            # Team IDを強調表示
            team_id = workspace_info.get('team_id')
            if team_id:
                print(f"✅ Workspace ID: {team_id}")
                print()
                print("このTeam IDを.envファイルのSLACK_WORKSPACE_IDに設定してください:")
                print(f"SLACK_WORKSPACE_ID={team_id}")
        return 0
        
    except ValueError as e:
        if args.format == 'json':
            import json
            error_response = {"error": "設定エラー", "message": str(e)}
            print(json.dumps(error_response, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 設定エラー: {e}")
        return 1
    except Exception as e:
        if args.format == 'json':
            import json
            error_response = {"error": "実行エラー", "message": str(e)}
            print(json.dumps(error_response, ensure_ascii=False, indent=2))
        else:
            print(f"❌ エラー: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 