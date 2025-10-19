#!/usr/bin/env python3
"""MentionResolver の振る舞いに関するテスト"""

import sys
from pathlib import Path


# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.mention_resolver import MentionResolver


class DummyUserResolver:
    """テスト用のユーザー解決スタブ"""

    def __init__(self, display_names):
        self.display_names = display_names

    def get_user_display_name(self, user_id: str, force_refresh: bool = False) -> str:
        return self.display_names.get(user_id, "")


def test_replace_user_mentions_renders_bold_display_name():
    """メンションが太字付きの display name に変換されることを検証"""

    resolver = MentionResolver(DummyUserResolver({"U123": "Display Name"}))

    result = resolver.replace_user_mentions("Hello <@U123>!")

    assert result == "Hello <strong>@Display Name</strong>!"


def test_replace_user_mentions_escapes_display_name_html():
    """表示名に含まれるHTMLが正しくエスケープされることを検証"""

    resolver = MentionResolver(DummyUserResolver({"U456": "Name <Admin>"}))

    result = resolver.replace_user_mentions("<@U456>")

    assert result == "<strong>@Name &lt;Admin&gt;</strong>"
