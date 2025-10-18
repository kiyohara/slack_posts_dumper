from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import bleach
import re

from src.utils.mention_resolver import MentionResolver, SupportsUserDisplayName

class SlackMessageHtmlRenderer:
    """
    Slack APIから得た1件のメッセージをHTML化するユーティリティクラス。
    ユーザーのアバター・名前・投稿時刻・本文をSlack風に出力する。
    """
    def __init__(
        self,
        template_dir: Optional[str] = None,
        emoji_resolver=None,
        asset_manager=None,
        mention_resolver_factory: Optional[Callable[[SupportsUserDisplayName], MentionResolver]] = None,
    ):
        if template_dir is None:
            # プロジェクトのtemplatesディレクトリを自動検出
            project_root = Path(__file__).parent.parent
            template_dir = str(project_root / "templates")
        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self.env.filters['slack_time'] = self._slack_time_filter
        self.env.filters['nl2br'] = self._nl2br_filter
        self.env.filters['mention_replace'] = self._mention_replace_filter
        self.env.filters['emoji_replace'] = self._emoji_replace_filter
        self.env.filters['local_asset_replace'] = self._local_asset_replace_filter
        self.env.filters['url_replace'] = self._url_replace_filter
        self.env.filters['sanitize_html'] = self._html_escape_filter
        self.template = self.env.get_template("message.html")
        self.emoji_resolver = emoji_resolver
        self.asset_manager = asset_manager
        self._mention_resolver_factory = mention_resolver_factory or MentionResolver
        self._user_resolver: Optional[SupportsUserDisplayName] = None
        self._mention_resolver: Optional[MentionResolver] = None

    def render(self, message: Dict[str, Any], user_resolver: Optional[SupportsUserDisplayName] = None) -> str:
        """
        メッセージとUserResolverからHTMLを生成
        Args:
            message: Slack APIのメッセージdict
            user_resolver: UserResolverインスタンス（省略時は前回使用したものを再利用）
        Returns:
            HTML文字列
        """
        effective_user_resolver = user_resolver or self._user_resolver

        if user_resolver is not None and user_resolver is not self._user_resolver:
            self._user_resolver = user_resolver
            self._mention_resolver = self._mention_resolver_factory(user_resolver)
        elif effective_user_resolver is not None and self._mention_resolver is None:
            self._mention_resolver = self._mention_resolver_factory(effective_user_resolver)

        user_id = message.get("user")
        user = effective_user_resolver.get_user_info(user_id) if effective_user_resolver and user_id else {}
        if user is None:
            user = {}

        # アセットマネージャーがある場合、ユーザーアバターのURLをローカルパスに置換
        if self.asset_manager and user and "profile" in user:
            profile = user["profile"]
            avatar_url = profile.get("image_72")
            if avatar_url and self.asset_manager.is_downloaded(avatar_url):
                local_avatar_path = self.asset_manager.get_local_path(avatar_url)
                # ユーザー情報のコピーを作成してアバターURLを置換
                user_copy = user.copy()
                user_copy["profile"] = profile.copy()
                user_copy["profile"]["image_72"] = local_avatar_path
                user = user_copy
        
        return self.template.render(message=message, user=user)

    @staticmethod
    def _slack_time_filter(ts):
        """Slackのts(float/str)を人間が読みやすい時刻に変換"""
        try:
            ts = float(ts)
            dt = datetime.fromtimestamp(ts)
            return dt.strftime('%H:%M')
        except Exception:
            return str(ts)

    @staticmethod
    def _nl2br_filter(value):
        """改行を<br>に変換（純粋な改行処理）"""
        if not value:
            return ''
        # 改行を<br>に変換
        return value.replace('\n', '<br>')
    
    def _emoji_replace_filter(self, value):
        """絵文字を画像タグに置換（純粋な置換機能）"""
        if not value or not self.emoji_resolver:
            return value
        return self.emoji_resolver.replace_emojis_in_text(value, asset_manager=self.asset_manager)
    
    def _local_asset_replace_filter(self, value):
        """画像タグのsrcをローカルパスに置換"""
        if not value or not self.asset_manager:
            return value
        
        import re
        
        # <img src="..." alt="..."> 形式の画像タグを検索
        img_pattern = r'<img[^>]+src="([^"]+)"[^>]*>'
        
        def replace_src(match):
            img_tag = match.group(0)
            src_url = match.group(1)
            
            # SlackのURLで、ローカルに登録済みの場合のみ置換
            if self._is_slack_url(src_url) and self.asset_manager.is_registered(src_url):
                local_path = self.asset_manager.get_local_path(src_url)
                return img_tag.replace(f'src="{src_url}"', f'src="{local_path}"')
            return img_tag
        
        return re.sub(img_pattern, replace_src, value)
    
    def _is_slack_url(self, url: str) -> bool:
        """URLがSlackのドメインかチェック"""
        from urllib.parse import urlparse
        
        slack_domains = [
            'slack-edge.com',
            'files.slack.com',
            'emoji.slack-edge.com',
            'a.slack-edge.com'
        ]
        
        parsed = urlparse(url)
        return any(domain in parsed.netloc for domain in slack_domains)
    
    @staticmethod
    def _url_replace_filter(value):
        """SlackのURL形式をクリック可能なリンクに変換"""
        if not value:
            return value
        
        # <http://example.com> 形式のURLを検出して変換
        # パターン: <http(s)://...> または <http(s)://...|表示テキスト>
        url_pattern = r'<(https?://[^>|]+)(?:\|([^>]+))?>'
        
        def replace_url(match):
            url = match.group(1)
            display_text = match.group(2) if match.group(2) else url
            return f'<a href="{url}" target="_blank">{display_text}</a>'
        
        return re.sub(url_pattern, replace_url, value)
    
    @staticmethod
    def _html_escape_filter(value):
        """HTMLサニタイズ（許可されたタグのみ許可）"""
        if not value:
            return ''
        
        # 許可するHTMLタグと属性を定義
        allowed_tags = [
            'img',  # 絵文字用
            'br',   # 改行用
            'a',    # リンク用（URL置換機能で使用）
            'strong', 'b',  # 太字
            'em', 'i',      # 斜体
            'code',         # インラインコード
            'pre',          # コードブロック
        ]
        
        allowed_attributes = {
            'img': ['src', 'alt', 'class', 'width', 'height'],
            'a': ['href', 'target', 'rel'],
            'br': [],
            'strong': [], 'b': [],
            'em': [], 'i': [],
            'code': [],
            'pre': [],
        }

        # bleachを使用してHTMLサニタイズ
        cleaned_html = bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

        return cleaned_html

    def _mention_replace_filter(self, value):
        """ユーザーメンションを表示名に変換"""
        if not value or not self._mention_resolver:
            return value
        return self._mention_resolver.replace_user_mentions(value)
