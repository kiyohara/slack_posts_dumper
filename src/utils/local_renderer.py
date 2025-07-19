"""ローカルファイル参照用メッセージレンダラー"""

from typing import Dict, Any, Optional
from .asset_manager import AssetManager
from ..message_renderer import SlackMessageHtmlRenderer


class LocalMessageRenderer(SlackMessageHtmlRenderer):
    """ローカルファイル参照でHTMLを生成するレンダラー"""
    
    def __init__(self, asset_manager: AssetManager, *args, **kwargs):
        """
        LocalMessageRendererを初期化
        
        Args:
            asset_manager: AssetManagerインスタンス
            *args, **kwargs: SlackMessageHtmlRendererの引数
        """
        super().__init__(*args, **kwargs)
        self.asset_manager = asset_manager
    
    def render(self, message: Dict[str, Any], user_resolver) -> str:
        """
        ローカルファイル参照でHTMLを生成
        
        Args:
            message: Slack APIのメッセージdict
            user_resolver: UserResolverインスタンス
            
        Returns:
            HTML文字列（ローカルファイル参照）
        """
        # ユーザー情報を取得
        user_id = message.get("user")
        user = user_resolver.get_user_info(user_id) if user_id else {}
        if user is None:
            user = {}
        
        # ユーザーアバターのURLをローカルパスに置換
        if user and "profile" in user:
            profile = user["profile"]
            avatar_url = profile.get("image_72")
            if avatar_url and self.asset_manager.is_downloaded(avatar_url):
                local_avatar_path = self.asset_manager.get_local_path(avatar_url)
                # ユーザー情報のコピーを作成してアバターURLを置換
                user_copy = user.copy()
                user_copy["profile"] = profile.copy()
                user_copy["profile"]["image_72"] = local_avatar_path
                user = user_copy
        
        # メッセージのコピーを作成
        message_copy = message.copy()
        
        # メッセージテキスト内の絵文字URLをローカルパスに置換
        text = message.get("text", "")
        if text:
            # ローカル絵文字置換フィルターを適用
            text = self._local_emoji_replace_filter(text)
            message_copy["text"] = text
        
        # テンプレートレンダリング時にローカル絵文字置換フィルターを使用
        original_emoji_replace_filter = self.env.filters.get('emoji_replace')
        self.env.filters['emoji_replace'] = self._local_emoji_replace_filter
        
        try:
            html = self.template.render(message=message_copy, user=user)
        finally:
            # 元のフィルターを復元
            if original_emoji_replace_filter:
                self.env.filters['emoji_replace'] = original_emoji_replace_filter
            else:
                del self.env.filters['emoji_replace']
        
        return html
    
    def _local_emoji_replace_filter(self, value: str) -> str:
        """
        絵文字をローカルファイル参照の画像タグに置換
        
        Args:
            value: 置換対象のテキスト
            
        Returns:
            ローカルファイル参照に置換されたテキスト
        """
        if not value:
            return value
        
        import re
        
        # <img src="..." alt=":emoji_name:"> 形式の画像タグを検索
        img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
        
        def replace_img_tag(match):
            img_tag = match.group(0)
            src_url = match.group(1)
            
            # SlackのURLで、ローカルにダウンロード済みの場合のみ置換
            if self._is_slack_url(src_url) and self.asset_manager.is_downloaded(src_url):
                local_path = self.asset_manager.get_local_path(src_url)
                # src属性をローカルパスに置換
                new_img_tag = img_tag.replace(f'src="{src_url}"', f'src="{local_path}"')
                return new_img_tag
            
            # 置換できない場合は元のタグをそのまま返す
            return img_tag
        
        return re.sub(img_pattern, replace_img_tag, value)
    
    def _is_slack_url(self, url: str) -> bool:
        """
        URLがSlackのドメインかチェック
        
        Args:
            url: チェックするURL
            
        Returns:
            Slackのドメインの場合はTrue
        """
        from urllib.parse import urlparse
        
        slack_domains = [
            'slack-edge.com',
            'files.slack.com',
            'emoji.slack-edge.com',
            'a.slack-edge.com'
        ]
        
        parsed = urlparse(url)
        return any(domain in parsed.netloc for domain in slack_domains) 