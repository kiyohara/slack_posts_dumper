"""アセットダウンロードユーティリティ"""

import requests
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from urllib.parse import urlparse
import re
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from .asset_manager import AssetManager


class AssetDownloader:
    """Slackアセット（画像、絵文字等）のダウンロードを行うクラス"""
    
    def __init__(self, client: WebClient, asset_manager: AssetManager):
        """
        AssetDownloaderを初期化
        
        Args:
            client: Slack WebClientインスタンス
            asset_manager: AssetManagerインスタンス
        """
        self.client = client
        self.asset_manager = asset_manager
        self.logger = logging.getLogger(__name__)
        
        # ダウンロード済みURLを記録（重複ダウンロード防止）
        self._downloaded_urls: Set[str] = set()
        
        # セッションを作成（接続の再利用）
        self.session = requests.Session()
        # User-Agentを設定
        self.session.headers.update({
            'User-Agent': 'SlackPostsDumper/1.0'
        })
    
    def download_asset(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        アセットをダウンロード
        
        Args:
            url: ダウンロードするアセットのURL
            metadata: アセットのメタデータ
            
        Returns:
            ダウンロード成功時はTrue、失敗時はFalse
        """
        # 既にダウンロード済みの場合はスキップ
        if url in self._downloaded_urls:
            self.logger.debug(f"既にダウンロード済み: {url}")
            return True
        
        # 既にローカルに存在する場合はスキップ
        if self.asset_manager.is_downloaded(url):
            self.logger.debug(f"ローカルファイルが既に存在: {url}")
            self._downloaded_urls.add(url)
            return True
        
        try:
            self.logger.info(f"アセットをダウンロード中: {url}")
            
            # URLがSlackのドメインかチェック
            if not self._is_slack_url(url):
                self.logger.warning(f"Slack以外のURLはダウンロードしません: {url}")
                return False
            
            # リクエストを送信
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # ファイルを保存
            local_path = self.asset_manager.get_local_path(url)
            absolute_path = self.asset_manager.get_absolute_path(url)
            
            # ディレクトリを作成
            absolute_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ファイルを書き込み
            with open(absolute_path, 'wb') as f:
                f.write(response.content)
            
            # アセットを登録
            self.asset_manager.register_asset(url, local_path, metadata)
            
            # ダウンロード済みとして記録
            self._downloaded_urls.add(url)
            
            self.logger.info(f"アセットのダウンロード完了: {url} -> {local_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"アセットのダウンロードに失敗: {url}, エラー: {e}")
            return False
        except Exception as e:
            self.logger.error(f"アセットの保存に失敗: {url}, エラー: {e}")
            return False
    
    def download_assets_from_message(self, message: Dict[str, Any], user_resolver) -> List[str]:
        """
        メッセージからアセットURLを抽出してダウンロード
        
        Args:
            message: Slack APIのメッセージdict
            user_resolver: UserResolverインスタンス
            
        Returns:
            ダウンロードしたアセットのローカルパスのリスト
        """
        downloaded_paths = []
        
        # ユーザーアバターをダウンロード
        user_id = message.get("user")
        if user_id and user_id != "USLACKBOT":
            try:
                user_info = user_resolver.get_user_info(user_id)
                if user_info:
                    profile = user_info.get("profile", {})
                    avatar_url = profile.get("image_72")
                    if avatar_url:
                        success = self.download_asset(
                            avatar_url, 
                            metadata={"type": "avatar", "user_id": user_id}
                        )
                        if success:
                            local_path = self.asset_manager.get_local_path(avatar_url)
                            downloaded_paths.append(local_path)
            except Exception as e:
                self.logger.warning(f"ユーザーアバターのダウンロードに失敗: {e}")
        
        # メッセージテキストから絵文字URLを抽出してダウンロード
        text = message.get("text", "")
        emoji_urls = self._extract_emoji_urls_from_text(text)
        for emoji_url in emoji_urls:
            success = self.download_asset(
                emoji_url, 
                metadata={"type": "emoji", "source": "message_text"}
            )
            if success:
                local_path = self.asset_manager.get_local_path(emoji_url)
                downloaded_paths.append(local_path)
        
        # 添付ファイルのアセットをダウンロード
        files = message.get("files", [])
        for file_info in files:
            # サムネイル画像
            thumb_url = file_info.get("thumb_360")
            if thumb_url:
                success = self.download_asset(
                    thumb_url, 
                    metadata={"type": "file_thumbnail", "file_id": file_info.get("id")}
                )
                if success:
                    local_path = self.asset_manager.get_local_path(thumb_url)
                    downloaded_paths.append(local_path)
            
            # プレビュー画像
            preview_url = file_info.get("preview")
            if preview_url:
                success = self.download_asset(
                    preview_url, 
                    metadata={"type": "file_preview", "file_id": file_info.get("id")}
                )
                if success:
                    local_path = self.asset_manager.get_local_path(preview_url)
                    downloaded_paths.append(local_path)
        
        self.logger.info(f"メッセージから {len(downloaded_paths)} 個のアセットをダウンロード")
        return downloaded_paths
    
    def download_emoji_assets(self, emoji_names: List[str]) -> List[str]:
        """
        絵文字名のリストからアセットをダウンロード
        
        Args:
            emoji_names: 絵文字名のリスト（:emoji_name:形式から:を除いたもの）
            
        Returns:
            ダウンロードしたアセットのローカルパスのリスト
        """
        downloaded_paths = []
        
        for emoji_name in emoji_names:
            try:
                # 絵文字のURLを取得
                emoji_url = self._get_emoji_url(emoji_name)
                if emoji_url:
                    success = self.download_asset(
                        emoji_url, 
                        metadata={"type": "emoji", "name": emoji_name}
                    )
                    if success:
                        local_path = self.asset_manager.get_local_path(emoji_url)
                        downloaded_paths.append(local_path)
            except Exception as e:
                self.logger.warning(f"絵文字 '{emoji_name}' のダウンロードに失敗: {e}")
        
        return downloaded_paths
    
    def _is_slack_url(self, url: str) -> bool:
        """
        URLがSlackのドメインかチェック
        
        Args:
            url: チェックするURL
            
        Returns:
            Slackのドメインの場合はTrue
        """
        slack_domains = [
            'slack-edge.com',
            'files.slack.com',
            'emoji.slack-edge.com',
            'a.slack-edge.com'
        ]
        
        parsed = urlparse(url)
        return any(domain in parsed.netloc for domain in slack_domains)
    
    def _extract_emoji_urls_from_text(self, text: str) -> List[str]:
        """
        テキストから絵文字URLを抽出
        
        Args:
            text: 抽出対象のテキスト
            
        Returns:
            絵文字URLのリスト
        """
        emoji_urls = []
        
        # <img src="..." alt=":emoji_name:"> 形式の画像タグからURLを抽出
        img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
        img_matches = re.findall(img_pattern, text)
        emoji_urls.extend(img_matches)
        
        return emoji_urls
    
    def _get_emoji_url(self, emoji_name: str) -> Optional[str]:
        """
        絵文字名からURLを取得
        
        Args:
            emoji_name: 絵文字名
            
        Returns:
            絵文字のURL、見つからない場合はNone
        """
        try:
            # emoji.list APIを呼び出して絵文字一覧を取得
            response = self.client.emoji_list()
            
            if response["ok"]:
                emoji_data = response.get("emoji", {})
                
                # カスタム絵文字を検索
                if emoji_name in emoji_data:
                    return emoji_data[emoji_name]
                
                # 標準絵文字の場合はSlackの標準URLを返す
                standard_url = f"https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/{emoji_name}.png"
                return standard_url
            
        except SlackApiError as e:
            self.logger.warning(f"絵文字一覧の取得に失敗: {e}")
        except Exception as e:
            self.logger.warning(f"絵文字URLの取得に失敗: {e}")
        
        return None
    
    def get_download_stats(self) -> Dict[str, Any]:
        """
        ダウンロード統計を取得
        
        Returns:
            ダウンロード統計の辞書
        """
        return {
            "downloaded_urls_count": len(self._downloaded_urls),
            "downloaded_urls": list(self._downloaded_urls),
            "total_assets": len(self.asset_manager.list_assets())
        }
    
    def clear_download_cache(self):
        """ダウンロードキャッシュをクリア"""
        self._downloaded_urls.clear()
        self.logger.info("ダウンロードキャッシュをクリアしました") 