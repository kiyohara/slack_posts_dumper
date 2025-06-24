#!/usr/bin/env python3
"""ユーザー情報解決ユーティリティ"""

import time
from typing import Dict, Optional, Any
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class UserResolver:
    """ユーザー情報を解決するクラス（キャッシュ機能付き）"""
    
    def __init__(self, client: WebClient, cache_ttl: int = 3600):
        """
        UserResolverを初期化
        
        Args:
            client: Slack WebClientインスタンス
            cache_ttl: キャッシュの有効期限（秒、デフォルト: 1時間）
        """
        self.client = client
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[str, float] = {}
    
    def get_user_info(self, user_id: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        ユーザー情報を取得（キャッシュ機能付き）
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            ユーザー情報の辞書、またはNone（ユーザーが見つからない場合）
            
        Raises:
            SlackApiError: Slack API呼び出しでエラーが発生した場合
        """
        # キャッシュチェック
        if not force_refresh and self._is_cached(user_id):
            return self._cache[user_id]
        
        try:
            # Slack APIからユーザー情報を取得
            response = self.client.users_info(user=user_id)
            
            if response["ok"]:
                user_info = response.get("user", {})
                
                # 表示名を優先、なければユーザー名を使用
                profile = user_info.get("profile", {})
                display_name = profile.get("display_name")
                real_name = profile.get("real_name")
                username = user_info.get("name")
                
                # 表示用の名前を決定
                if display_name:
                    user_info["display_name"] = display_name
                elif real_name:
                    user_info["display_name"] = real_name
                elif username:
                    user_info["display_name"] = username
                else:
                    user_info["display_name"] = "Unknown"
                
                # キャッシュに保存
                self._cache_user_info(user_id, user_info)
                
                return user_info
            else:
                # API呼び出しは成功したが、ユーザーが見つからない場合
                return None
                
        except SlackApiError as e:
            error_code = e.response.get("error", "unknown_error")
            if error_code == "user_not_found":
                # ユーザーが見つからない場合はNoneを返す
                return None
            else:
                # その他のエラーは再発生
                raise
    
    def get_user_display_name(self, user_id: str, force_refresh: bool = False) -> str:
        """
        ユーザーの表示名を取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            ユーザーの表示名、または"Unknown"
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            return user_info.get("display_name", "Unknown")
        return "Unknown"
    
    def get_user_real_name(self, user_id: str, force_refresh: bool = False) -> str:
        """
        ユーザーの実名を取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            ユーザーの実名、または"Unknown"
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            profile = user_info.get("profile", {})
            return profile.get("real_name", "Unknown")
        return "Unknown"
    
    def get_user_username(self, user_id: str, force_refresh: bool = False) -> str:
        """
        ユーザーのユーザー名を取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            ユーザーのユーザー名、または"Unknown"
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            return user_info.get("name", "Unknown")
        return "Unknown"
    
    def get_user_avatar_url(self, user_id: str, force_refresh: bool = False, size: str = "192") -> Optional[str]:
        """
        ユーザーのアバター画像URLを取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            size: 画像サイズ（24, 32, 48, 72, 192, 512, 1024、デフォルト: 192）
            
        Returns:
            アバター画像URL、またはNone（アバターが設定されていない場合）
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            profile = user_info.get("profile", {})
            # プロフィール画像のURLを取得
            image_url = profile.get("image_192")  # デフォルトサイズ
            if not image_url:
                # サイズ別のURLを取得
                size_key = f"image_{size}"
                image_url = profile.get(size_key)
                if not image_url:
                    # 利用可能なサイズを順番に試す
                    for available_size in ["192", "512", "1024", "72", "48", "32", "24"]:
                        size_key = f"image_{available_size}"
                        image_url = profile.get(size_key)
                        if image_url:
                            break
            return image_url
        return None
    
    def get_user_status_emoji(self, user_id: str, force_refresh: bool = False) -> Optional[str]:
        """
        ユーザーのステータス絵文字を取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            ステータス絵文字、またはNone（ステータスが設定されていない場合）
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            profile = user_info.get("profile", {})
            return profile.get("status_emoji")
        return None
    
    def get_user_status_text(self, user_id: str, force_refresh: bool = False) -> Optional[str]:
        """
        ユーザーのステータステキストを取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            ステータステキスト、またはNone（ステータスが設定されていない場合）
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            profile = user_info.get("profile", {})
            return profile.get("status_text")
        return None
    
    def get_user_email(self, user_id: str, force_refresh: bool = False) -> Optional[str]:
        """
        ユーザーのメールアドレスを取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            メールアドレス、またはNone（メールアドレスが設定されていない場合）
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            profile = user_info.get("profile", {})
            return profile.get("email")
        return None
    
    def get_user_team_id(self, user_id: str, force_refresh: bool = False) -> Optional[str]:
        """
        ユーザーのチームIDを取得
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            チームID、またはNone
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            return user_info.get("team_id")
        return None
    
    def get_user_is_bot(self, user_id: str, force_refresh: bool = False) -> bool:
        """
        ユーザーがBotかどうかを判定
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            Botの場合はTrue、そうでなければFalse
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            return user_info.get("is_bot", False)
        return False
    
    def get_user_is_deleted(self, user_id: str, force_refresh: bool = False) -> bool:
        """
        ユーザーが削除されているかどうかを判定
        
        Args:
            user_id: ユーザーID
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            
        Returns:
            削除されている場合はTrue、そうでなければFalse
        """
        user_info = self.get_user_info(user_id, force_refresh)
        if user_info:
            return user_info.get("deleted", False)
        return False
    
    def clear_cache(self, user_id: Optional[str] = None):
        """
        キャッシュをクリア
        
        Args:
            user_id: 特定のユーザーIDのキャッシュのみをクリアする場合。
                     Noneの場合は全キャッシュをクリア
        """
        if user_id:
            self._cache.pop(user_id, None)
            self._cache_timestamps.pop(user_id, None)
        else:
            self._cache.clear()
            self._cache_timestamps.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        キャッシュの情報を取得
        
        Returns:
            キャッシュ情報の辞書
        """
        current_time = time.time()
        expired_count = 0
        valid_count = 0
        
        for user_id, timestamp in self._cache_timestamps.items():
            if current_time - timestamp > self.cache_ttl:
                expired_count += 1
            else:
                valid_count += 1
        
        return {
            "total_cached_users": len(self._cache),
            "valid_cache_count": valid_count,
            "expired_cache_count": expired_count,
            "cache_ttl": self.cache_ttl
        }
    
    def _is_cached(self, user_id: str) -> bool:
        """ユーザー情報がキャッシュされているかチェック"""
        if user_id not in self._cache:
            return False
        
        # TTLチェック
        timestamp = self._cache_timestamps.get(user_id, 0)
        return (time.time() - timestamp) < self.cache_ttl
    
    def _cache_user_info(self, user_id: str, user_info: Dict[str, Any]):
        """ユーザー情報をキャッシュに保存"""
        self._cache[user_id] = user_info
        self._cache_timestamps[user_id] = time.time()
    
    def cleanup_expired_cache(self):
        """期限切れのキャッシュを削除"""
        current_time = time.time()
        expired_users = []
        
        for user_id, timestamp in self._cache_timestamps.items():
            if current_time - timestamp > self.cache_ttl:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            self._cache.pop(user_id, None)
            self._cache_timestamps.pop(user_id, None)


# 便利な関数
def create_user_resolver(client: WebClient, cache_ttl: int = 3600) -> UserResolver:
    """
    UserResolverインスタンスを作成する便利関数
    
    Args:
        client: Slack WebClientインスタンス
        cache_ttl: キャッシュの有効期限（秒、デフォルト: 1時間）
        
    Returns:
        UserResolverインスタンス
    """
    return UserResolver(client, cache_ttl) 