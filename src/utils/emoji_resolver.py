"""絵文字情報解決ユーティリティ"""

import re
import logging
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import emoji


class EmojiResolver:
    """絵文字情報解決クラス"""
    
    def __init__(self, client: WebClient, cache_ttl: int = 3600):
        """
        EmojiResolverを初期化
        
        Args:
            client: Slack WebClientインスタンス
            cache_ttl: キャッシュの有効期限（秒、デフォルト: 1時間）
        """
        self.client = client
        self.cache_ttl = cache_ttl
        self._emoji_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)
        
        # 標準絵文字のパターン（:emoji_name:形式）
        self.emoji_pattern = re.compile(r':([a-zA-Z0-9_+-]+):')
        
        # 標準絵文字のURLパターン（Slackの標準絵文字）
        self.standard_emoji_url_pattern = "https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/{}.png"
    
    def get_emoji_list(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        絵文字一覧を取得
        
        Args:
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
        
        Returns:
            絵文字名とURLの辞書
        """
        # キャッシュが有効で、かつ強制リフレッシュでない場合はキャッシュを返す
        if not force_refresh and self._is_cache_valid():
            self.logger.debug("絵文字一覧をキャッシュから取得")
            return self._emoji_cache
        
        try:
            self.logger.info("emoji.list APIを呼び出し中...")
            
            # emoji.list APIを呼び出して絵文字一覧を取得
            response = self.client.emoji_list()
            
            if not response["ok"]:
                raise Exception(f"emoji.list APIが失敗しました: {response.get('error', 'Unknown error')}")
            
            emoji_data = response.get("emoji", {})
            
            # キャッシュを更新
            self._emoji_cache = emoji_data
            self._cache_timestamp = datetime.now()
            
            self.logger.info(f"絵文字一覧を取得しました: {len(emoji_data)}件")
            return emoji_data
            
        except SlackApiError as e:
            error_code = e.response.get("error", "unknown_error")
            if error_code == "missing_scope":
                raise Exception("Bot Tokenに必要な権限がありません。emoji:read権限が必要です。")
            else:
                raise Exception(f"Slack API エラー: {error_code}")
        except Exception as e:
            raise Exception(f"絵文字一覧の取得に失敗しました: {e}")
    
    def get_emoji_url(self, emoji_name: str, force_refresh: bool = False) -> Optional[str]:
        """
        絵文字名からURLを取得
        
        Args:
            emoji_name: 絵文字名（:emoji_name:形式から:を除いたもの）
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
        
        Returns:
            絵文字のURL、見つからない場合はNone
        """
        # 絵文字一覧を取得
        emoji_list = self.get_emoji_list(force_refresh)
        
        # カスタム絵文字を検索
        if emoji_name in emoji_list:
            emoji_url = emoji_list[emoji_name]
            self.logger.debug(f"カスタム絵文字 '{emoji_name}' のURL: {emoji_url}")
            return emoji_url
        
        # 標準絵文字の場合はSlackの標準URLを返す
        standard_url = self.standard_emoji_url_pattern.format(emoji_name)
        self.logger.debug(f"標準絵文字 '{emoji_name}' のURL: {standard_url}")
        return standard_url
    
    def replace_emojis_in_text(self, text: str, force_refresh: bool = False, use_unicode_fallback: bool = True, asset_manager=None) -> str:
        """
        テキスト内の絵文字を画像タグに置換
        
        Args:
            text: 置換対象のテキスト
            force_refresh: キャッシュを無視して強制的に再取得するかどうか
            use_unicode_fallback: ダウンロードに失敗した場合にUnicodeに置き換えるかどうか
            asset_manager: アセットマネージャー（ダウンロード状況をチェックするため）
        
        Returns:
            絵文字が画像タグに置換されたテキスト
        """
        def replace_emoji(match):
            emoji_name = match.group(1)
            emoji_url = self.get_emoji_url(emoji_name, force_refresh)
            
            if emoji_url:
                # アセットマネージャーがある場合、ダウンロード状況をチェック
                if asset_manager and asset_manager.is_registered(emoji_url):
                    if asset_manager.is_downloaded(emoji_url):
                        # ダウンロード成功の場合、ローカルパスを使用
                        local_path = asset_manager.get_local_path(emoji_url)
                        return f'<img src="{local_path}" alt=":{emoji_name}:" class="slack-emoji" width="20" height="20" style="vertical-align: middle;">'
                    elif use_unicode_fallback:
                        # ダウンロード失敗の場合、Unicodeに変換を試行
                        try:
                            unicode_emoji = emoji.emojize(f":{emoji_name}:", language='alias')
                            if unicode_emoji != f":{emoji_name}:":
                                # 変換成功（標準絵文字の場合）
                                return unicode_emoji
                        except Exception as e:
                            self.logger.debug(f"絵文字 '{emoji_name}' のUnicode変換に失敗: {e}")
                
                # アセットマネージャーがない場合や、その他の場合は元のURLを使用
                return f'<img src="{emoji_url}" alt=":{emoji_name}:" class="slack-emoji" width="20" height="20" style="vertical-align: middle;">'
            else:
                # URLが見つからない場合の処理
                if use_unicode_fallback:
                    # emojiライブラリを使用してUnicodeに変換を試行
                    try:
                        unicode_emoji = emoji.emojize(f":{emoji_name}:", language='alias')
                        if unicode_emoji != f":{emoji_name}:":
                            # 変換成功（標準絵文字の場合）
                            return unicode_emoji
                    except Exception as e:
                        self.logger.debug(f"絵文字 '{emoji_name}' のUnicode変換に失敗: {e}")
                
                # Unicode変換に失敗した場合やカスタム絵文字の場合は元のテキストをそのまま返す
                return match.group(0)
        
        # 絵文字パターンを検索して置換
        return self.emoji_pattern.sub(replace_emoji, text)
    
    def _is_cache_valid(self) -> bool:
        """キャッシュが有効かどうかをチェック"""
        if not self._cache_timestamp or not self._emoji_cache:
            return False
        
        cache_age = datetime.now() - self._cache_timestamp
        return cache_age.total_seconds() < self.cache_ttl
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self._emoji_cache.clear()
        self._cache_timestamp = None
        self.logger.info("絵文字キャッシュをクリアしました")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """キャッシュ情報を取得"""
        cache_age = None
        if self._cache_timestamp:
            cache_age = (datetime.now() - self._cache_timestamp).total_seconds()
        
        return {
            "total_cached_emojis": len(self._emoji_cache),
            "cache_ttl": self.cache_ttl,
            "cache_age_seconds": cache_age,
            "is_cache_valid": self._is_cache_valid()
        }


def create_emoji_resolver(client: WebClient, cache_ttl: int = 3600) -> EmojiResolver:
    """
    EmojiResolverインスタンスを作成するファクトリ関数
    
    Args:
        client: Slack WebClientインスタンス
        cache_ttl: キャッシュの有効期限（秒、デフォルト: 1時間）
    
    Returns:
        EmojiResolverインスタンス
    """
    return EmojiResolver(client, cache_ttl) 