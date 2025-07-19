#!/usr/bin/env python3
"""emojiライブラリのテストスクリプト"""

import emoji


def test_emoji_library():
    """emojiライブラリの基本機能をテスト"""
    print("=== emojiライブラリテスト ===")
    
    # テストケース
    test_cases = [
        ":smile:",
        ":heart:",
        ":+1:",
        ":slightly_smiling_face:",
        ":thumbsup:",
        ":custom_emoji:",  # カスタム絵文字（変換されないはず）
        "絵文字なしのテキスト",
        "複数の絵文字 :smile: :heart: :+1:",
    ]
    
    for text in test_cases:
        print(f"\n入力: {text}")
        
        # emoji.emojizeでshortnameをUnicodeに変換
        converted = emoji.emojize(text, language='alias')
        print(f"変換後: {converted}")
        
        # 変換されたかどうかをチェック
        if converted != text:
            print("✅ 変換成功")
        else:
            print("❌ 変換されませんでした")
    
    print("\n=== 逆変換テスト ===")
    
    # Unicode絵文字をshortnameに変換
    unicode_emojis = ["😊", "❤️", "👍", "😀"]
    
    for emoji_char in unicode_emojis:
        print(f"\nUnicode: {emoji_char}")
        shortname = emoji.demojize(emoji_char)
        print(f"Shortname: {shortname}")
    
    print("\n🎉 emojiライブラリテスト完了")


if __name__ == "__main__":
    test_emoji_library() 