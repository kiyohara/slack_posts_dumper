"""設定管理モジュール"""

import os
from typing import Optional


def get_slack_bot_token() -> str:
    """Slack Bot Tokenを取得"""
    token = os.getenv('SLACK_BOT_TOKEN')
    if not token:
        raise ValueError(
            "SLACK_BOT_TOKENが設定されていません。"
            ".envファイルにSLACK_BOT_TOKENを設定してください。"
        )
    return token


def get_workspace_id(args_workspace_id: Optional[str] = None) -> str:
    """ワークスペースIDを取得（引数 > 環境変数の優先順位）"""
    if args_workspace_id:
        return args_workspace_id
    
    env_workspace_id = os.getenv('SLACK_WORKSPACE_ID')
    if env_workspace_id:
        return env_workspace_id
    
    raise ValueError(
        "ワークスペースIDが指定されていません。"
        "引数または環境変数SLACK_WORKSPACE_IDを設定してください。"
    )


def get_channel_id(args_channel_id: Optional[str] = None) -> str:
    """チャネルIDを取得（引数 > 環境変数の優先順位）"""
    if args_channel_id:
        return args_channel_id
    
    env_channel_id = os.getenv('SLACK_CHANNEL_ID')
    if env_channel_id:
        return env_channel_id
    
    raise ValueError(
        "チャネルIDが指定されていません。"
        "引数または環境変数SLACK_CHANNEL_IDを設定してください。"
    )


def validate_slack_token_format(token: str) -> bool:
    """Slack Tokenの形式を検証"""
    if not token.startswith('xoxb-'):
        return False
    return len(token) > 10


def validate_channel_id_format(channel_id: str) -> bool:
    """チャネルIDの形式を検証"""
    if not channel_id.startswith('C'):
        return False
    return len(channel_id) >= 9


def validate_workspace_id_format(workspace_id: str) -> bool:
    """ワークスペースIDの形式を検証"""
    if not workspace_id.startswith('T'):
        return False
    return len(workspace_id) >= 9 