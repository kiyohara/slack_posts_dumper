"""Slack API接続確認プログラム"""

import logging
from typing import Optional, Dict, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .config.settings import (
    get_slack_bot_token,
    get_workspace_id,
    get_channel_id,
    validate_slack_token_format,
    validate_channel_id_format,
    validate_workspace_id_format,
)


class SlackChecker:
    """Slack API接続確認クラス"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.client = None
        self._setup_logging()
    
    def _setup_logging(self):
        """ログ設定"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_client(self, token: str) -> bool:
        """Slackクライアントを初期化"""
        try:
            if not validate_slack_token_format(token):
                self.logger.error("Slack Tokenの形式が正しくありません。xoxb-で始まる必要があります。")
                return False
            
            self.client = WebClient(token=token)
            self.logger.info("Slackクライアントを初期化しました。")
            return True
            
        except Exception as e:
            self.logger.error(f"Slackクライアントの初期化に失敗しました: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Slack APIとの接続をテスト"""
        try:
            if not self.client:
                self.logger.error("クライアントが初期化されていません。")
                return False
            
            # auth.test APIを呼び出して接続確認
            response = self.client.auth_test()
            
            if response["ok"]:
                self.logger.info("Slack APIとの接続が成功しました。")
                self.logger.info(f"ワークスペース: {response.get('team', 'Unknown')}")
                self.logger.info(f"ユーザー: {response.get('user', 'Unknown')}")
                return True
            else:
                self.logger.error("Slack APIとの接続に失敗しました。")
                return False
                
        except SlackApiError as e:
            self.logger.error(f"Slack API エラー: {e.response['error']}")
            return False
        except Exception as e:
            self.logger.error(f"接続テスト中にエラーが発生しました: {e}")
            return False
    
    def get_latest_message(
        self, 
        channel_id: str, 
        workspace_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """指定されたチャネルから最新メッセージを取得"""
        try:
            if not validate_channel_id_format(channel_id):
                self.logger.error("チャネルIDの形式が正しくありません。Cで始まる必要があります。")
                return None
            
            if workspace_id and not validate_workspace_id_format(workspace_id):
                self.logger.error("ワークスペースIDの形式が正しくありません。Tで始まる必要があります。")
                return None
            
            # チャネル履歴を取得（最新1件）
            response = self.client.conversations_history(
                channel=channel_id,
                limit=1
            )
            
            if not response["ok"]:
                self.logger.error(f"チャネル履歴の取得に失敗しました: {response.get('error', 'Unknown error')}")
                return None
            
            messages = response.get("messages", [])
            if not messages:
                self.logger.info("チャネルにメッセージがありません。")
                return None
            
            latest_message = messages[0]
            self.logger.info("最新メッセージを取得しました。")
            return latest_message
            
        except SlackApiError as e:
            error_code = e.response.get("error", "unknown_error")
            if error_code == "channel_not_found":
                self.logger.error("指定されたチャネルが見つかりません。")
            elif error_code == "not_in_channel":
                self.logger.error("ボットがチャネルに参加していません。")
            elif error_code == "missing_scope":
                self.logger.error("必要な権限が不足しています。")
            else:
                self.logger.error(f"Slack API エラー: {error_code}")
            return None
        except Exception as e:
            self.logger.error(f"メッセージ取得中にエラーが発生しました: {e}")
            return None
    
    def format_message(self, message: Dict[str, Any]) -> str:
        """メッセージを整形して表示"""
        timestamp = message.get("ts", "Unknown")
        user_id = message.get("user", "Unknown")
        text = message.get("text", "")
        
        # ユーザー情報を取得
        user_name = self._get_user_name(user_id)
        
        formatted = f"""
=== 最新メッセージ ===
タイムスタンプ: {timestamp}
ユーザー: {user_name} ({user_id})
内容: {text}
==================
"""
        return formatted
    
    def _get_user_name(self, user_id: str) -> str:
        """ユーザーIDからユーザー名を取得"""
        try:
            if user_id == "Unknown":
                return "Unknown"
            
            response = self.client.users_info(user=user_id)
            if response["ok"]:
                user = response["user"]
                return user.get("real_name", user.get("name", "Unknown"))
            else:
                return "Unknown"
        except Exception:
            return "Unknown"
    
    def run_check(
        self, 
        workspace_id: Optional[str] = None,
        channel_id: Optional[str] = None
    ) -> bool:
        """Slack API接続確認を実行"""
        try:
            # 設定値を取得
            token = get_slack_bot_token()
            workspace_id = get_workspace_id(workspace_id)
            channel_id = get_channel_id(channel_id)
            
            self.logger.info(f"ワークスペースID: {workspace_id}")
            self.logger.info(f"チャネルID: {channel_id}")
            
            # クライアント初期化
            if not self.initialize_client(token):
                return False
            
            # 接続テスト
            if not self.test_connection():
                return False
            
            # 最新メッセージ取得
            message = self.get_latest_message(channel_id, workspace_id)
            if message:
                print(self.format_message(message))
            else:
                self.logger.warning("メッセージを取得できませんでした。")
            
            return True
            
        except ValueError as e:
            self.logger.error(f"設定エラー: {e}")
            return False
        except Exception as e:
            self.logger.error(f"予期しないエラーが発生しました: {e}")
            return False 