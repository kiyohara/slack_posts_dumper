"""Slackメンションを表示名に置き換えるユーティリティ"""

import html
import re
from typing import Dict, Protocol


class SupportsUserDisplayName(Protocol):
    """ユーザー表示名を取得するためのプロトコル."""

    def get_user_display_name(self, user_id: str, force_refresh: bool = False) -> str:
        ...


class MentionResolver:
    """テキスト内のSlackユーザーメンションを表示名に置換するクラス."""

    USER_MENTION_PATTERN = re.compile(r"<@([A-Z0-9]+)(?:\|[^>]+)?>")

    def __init__(self, user_resolver: SupportsUserDisplayName, unknown_display_name: str = "Unknown") -> None:
        self.user_resolver = user_resolver
        self.unknown_display_name = unknown_display_name
        self._display_name_cache: Dict[str, str] = {}

    def replace_user_mentions(self, text: str) -> str:
        """テキスト内のユーザーメンションを表示名に置換する."""

        if not text:
            return text

        def replace(match: re.Match) -> str:
            user_id = match.group(1)
            display_name = self._get_display_name(user_id)
            return f"@{html.escape(display_name)}"

        return self.USER_MENTION_PATTERN.sub(replace, text)

    def _get_display_name(self, user_id: str) -> str:
        if user_id in self._display_name_cache:
            return self._display_name_cache[user_id]

        display_name = self.user_resolver.get_user_display_name(user_id)
        if not display_name:
            display_name = self.unknown_display_name

        self._display_name_cache[user_id] = display_name
        return display_name
