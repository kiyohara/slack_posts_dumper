#!/usr/bin/env python3
"""LocalMessageRendererテストスクリプト"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.asset_manager import AssetManager
from src.utils.local_renderer import LocalMessageRenderer


def test_local_renderer():
    """LocalMessageRendererの基本機能をテスト"""
    print("=== LocalMessageRenderer テスト ===")
    
    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerを初期化
        asset_manager = AssetManager(temp_dir)
        
        # LocalMessageRendererを初期化
        renderer = LocalMessageRenderer(asset_manager)
        
        # テスト用のダミーファイルを作成
        test_avatar_url = "https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/smile.png"
        test_emoji_url = "https://emoji.slack-edge.com/T1234567890/custom_emoji/1234567890.1234567890/custom.gif"
        
        # アバターファイルを作成
        avatar_path = asset_manager.get_absolute_path(test_avatar_url)
        avatar_path.parent.mkdir(parents=True, exist_ok=True)
        avatar_path.write_text("dummy avatar content")
        asset_manager.register_asset(test_avatar_url, asset_manager.get_local_path(test_avatar_url))
        
        # 絵文字ファイルを作成
        emoji_path = asset_manager.get_absolute_path(test_emoji_url)
        emoji_path.parent.mkdir(parents=True, exist_ok=True)
        emoji_path.write_text("dummy emoji content")
        asset_manager.register_asset(test_emoji_url, asset_manager.get_local_path(test_emoji_url))
        
        print("\n1. ローカルURL判定テスト:")
        test_urls = [
            test_avatar_url,
            test_emoji_url,
            "https://example.com/image.png",
            "https://google.com/logo.png"
        ]
        
        for url in test_urls:
            is_slack = renderer._is_slack_url(url)
            print(f"  {url} -> {'Slack' if is_slack else '非Slack'}")
        
        print("\n2. ローカル絵文字置換テスト:")
        test_text = f"""
        こんにちは！<img src="{test_avatar_url}" alt=":smile:" class="slack-emoji" width="20" height="20">
        素晴らしいですね<img src="{test_emoji_url}" alt=":custom:" class="slack-emoji" width="20" height="20">
        外部画像<img src="https://example.com/image.png" alt="external" width="20" height="20">
        """
        
        replaced_text = renderer._local_emoji_replace_filter(test_text)
        print("  元のテキスト:")
        print(f"    {test_text.strip()}")
        print("  置換後のテキスト:")
        print(f"    {replaced_text.strip()}")
        
        # 置換が正しく行われたかチェック
        avatar_local_path = asset_manager.get_local_path(test_avatar_url)
        emoji_local_path = asset_manager.get_local_path(test_emoji_url)
        
        assert avatar_local_path in replaced_text, f"アバターのローカルパスが置換されていません: {avatar_local_path}"
        assert emoji_local_path in replaced_text, f"絵文字のローカルパスが置換されていません: {emoji_local_path}"
        assert "https://example.com/image.png" in replaced_text, "外部URLは置換されません"
        
        print("  ✅ 絵文字置換テスト成功")
        
        print("\n3. 完全なレンダリングテスト:")
        # テスト用メッセージ
        test_message = {
            "user": "U1234567890",
            "text": f"こんにちは！<img src=\"{test_avatar_url}\" alt=\":smile:\" class=\"slack-emoji\" width=\"20\" height=\"20\"> 素晴らしいですね<img src=\"{test_emoji_url}\" alt=\":custom:\" class=\"slack-emoji\" width=\"20\" height=\"20\">",
            "ts": "1234567890.123456"
        }
        
        # モックのUserResolver
        mock_user_resolver = Mock()
        mock_user_resolver.get_user_info.return_value = {
            "display_name": "テストユーザー",
            "profile": {
                "image_72": test_avatar_url
            }
        }
        
        # HTMLをレンダリング
        html = renderer.render(test_message, mock_user_resolver)
        
        print("  生成されたHTML:")
        print(f"    {html}")
        
        # ローカルパスが含まれているかチェック
        assert avatar_local_path in html, f"アバターのローカルパスがHTMLに含まれていません: {avatar_local_path}"
        assert emoji_local_path in html, f"絵文字のローカルパスがHTMLに含まれていません: {emoji_local_path}"
        
        print("  ✅ 完全なレンダリングテスト成功")
        
        print("\n✅ テスト完了")


if __name__ == "__main__":
    test_local_renderer() 