from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import html

class SlackMessageHtmlRenderer:
    """
    Slack APIから得た1件のメッセージをHTML化するユーティリティクラス。
    ユーザーのアバター・名前・投稿時刻・本文をSlack風に出力する。
    """
    def __init__(self, template_dir: str = None):
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
        self.template = self.env.get_template("message.html")

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
        """改行を<br>に変換"""
        return html.escape(value).replace('\n', '<br>') if value else '' 