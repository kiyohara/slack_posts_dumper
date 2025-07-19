#!/usr/bin/env python3
"""Unicodeフォールバック機能付きEmojiResolverのテストスクリプト"""

import sys
from pathlib import Path
from unittest.mock import Mock

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.emoji_resolver import EmojiResolver


def test_emoji_resolver_unicode():
    """Unicodeフォールバック機能をテスト"""
    print("=== Unicodeフォールバック機能テスト ===")
    
    # モッククライアントを作成
    mock_client = Mock()
    mock_response = {"ok": True, "emoji": {}}
    mock_client.emoji_list.return_value = mock_response
    
    # EmojiResolverを初期化
    resolver = EmojiResolver(mock_client)
    
    # テストケース
    test_cases = [
        "こんにちは！:smile: 素晴らしいですね",
        ":heart: 大好きです :+1: 素晴らしい",
        "絵文字なしのテキスト",
        "複数の絵文字 :smile: :heart: :+1: :custom_emoji:",
        "特殊文字 :smile_face: :heart-eyes: :100:",
        "カスタム絵文字 :custom_emoji: と標準絵文字 :smile:",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n{i}. テストケース: {text}")
        
        # Unicodeフォールバックありでテスト
        result_with_fallback = resolver.replace_emojis_in_text(text, use_unicode_fallback=True)
        print(f"   Unicodeフォールバックあり: {result_with_fallback}")
        
        # Unicodeフォールバックなしでテスト
        result_without_fallback = resolver.replace_emojis_in_text(text, use_unicode_fallback=False)
        print(f"   Unicodeフォールバックなし: {result_without_fallback}")
        
        # 結果の比較
        if result_with_fallback != result_without_fallback:
            print("   ✅ Unicodeフォールバックが動作しています")
        else:
            print("   ℹ️ フォールバックの違いはありません")
    
    print("\n✅ Unicodeフォールバック機能テスト完了")


if __name__ == "__main__":
    test_emoji_resolver_unicode() 