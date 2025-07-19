from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import html
import bleach

class SlackMessageHtmlRenderer:
    """
    Slack APIから得た1件のメッセージをHTML化するユーティリティクラス。
    ユーザーのアバター・名前・投稿時刻・本文をSlack風に出力する。
    """
    def __init__(self, template_dir: Optional[str] = None, emoji_resolver=None):
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
        self.env.filters['emoji_replace'] = self._emoji_replace_filter
        self.env.filters['sanitize_html'] = self._html_escape_filter
        self.template = self.env.get_template("message.html")
        self.emoji_resolver = emoji_resolver

    def render(self, message: Dict[str, Any], user_resolver) -> str:
        """
        メッセージとUserResolverからHTMLを生成
        Args:
            message: Slack APIのメッセージdict
            user_resolver: UserResolverインスタンス
        Returns:
            HTML文字列
        """
        user_id = message.get("user")
        user = user_resolver.get_user_info(user_id) if user_id else {}
        if user is None:
            user = {}
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
        return self.emoji_resolver.replace_emojis_in_text(value)
    
    @staticmethod
    def _html_escape_filter(value):
        """HTMLサニタイズ（許可されたタグのみ許可）"""
        if not value:
            return ''
        
        # 許可するHTMLタグと属性を定義
        allowed_tags = [
            'img',  # 絵文字用
            'br',   # 改行用
            'a',    # リンク用（将来的にURL置換機能で使用）
            'strong', 'b',  # 太字
            'em', 'i',      # 斜体
            'code',         # インラインコード
            'pre',          # コードブロック
        ]
        
        allowed_attributes = {
            'img': ['src', 'alt', 'class', 'width', 'height', 'style'],
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