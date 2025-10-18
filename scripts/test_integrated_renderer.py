#!/usr/bin/env python3
"""統合されたレンダラーのテストスクリプト"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.asset_manager import AssetManager
from src.message_renderer import SlackMessageHtmlRenderer


def test_integrated_renderer():
    """統合されたレンダラーの基本機能をテスト"""
    print("=== 統合されたレンダラーテスト ===")
    
    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerを初期化
        asset_manager = AssetManager(temp_dir)
        
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
        
        print("\n1. 通常モード（asset_managerなし）のテスト:")
        # 通常モードのレンダラー
        normal_renderer = SlackMessageHtmlRenderer()
        
        # テスト用メッセージ
        test_message = {
            "user": "U1234567890",
            "text": "<@U1234567890> こんにちは！:smile: 素晴らしいですね:custom:",
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
        mock_user_resolver.get_user_display_name.return_value = "テストユーザー"
        
        # HTMLをレンダリング（通常モード）
        html_normal = normal_renderer.render(test_message, mock_user_resolver)
        print("  通常モードのHTML（一部）:")
        print(f"    {html_normal[:200]}...")

        # 通常モードではローカルパスが含まれていないことを確認
        avatar_local_path = asset_manager.get_local_path(test_avatar_url)
        assert avatar_local_path not in html_normal, "通常モードでローカルパスが含まれています"
        assert "@テストユーザー" in html_normal, "メンションが表示名に変換されていません"
        assert "U1234567890" not in html_normal, "ユーザーIDがそのまま残っています"
        
        print("  ✅ 通常モードテスト成功")
        
        print("\n2. フィルター動作テスト:")
        # フィルターの動作を直接テスト
        test_url = "https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/smile.png"
        test_img_tag = f'<img src="{test_url}" alt="avatar" width="48" height="48" class="slack-avatar">'
        
        # ローカルモードのレンダラー
        local_renderer = SlackMessageHtmlRenderer(asset_manager=asset_manager)
        
        # フィルターを直接テスト
        filtered_img_tag = local_renderer._local_asset_replace_filter(test_img_tag)
        print(f"  元のimgタグ: {test_img_tag}")
        print(f"  フィルター適用後: {filtered_img_tag}")
        print(f"  ローカルパスが含まれている: {avatar_local_path in filtered_img_tag}")
        
        # フィルターが正しく動作することを確認
        assert avatar_local_path in filtered_img_tag, f"フィルターが正しく動作していません: {avatar_local_path}"
        
        print("  ✅ フィルター動作テスト成功")
        
        print("\n3. ローカルモード（asset_managerあり）のテスト:")
        # モックのEmojiResolverを作成
        mock_emoji_resolver = Mock()
        mock_emoji_resolver.replace_emojis_in_text.return_value = f'こんにちは！<img src="{test_emoji_url}" alt=":smile:" class="slack-emoji" width="20" height="20"> 素晴らしいですね<img src="{test_emoji_url}" alt=":custom:" class="slack-emoji" width="20" height="20">'
        
        # ローカルモードのレンダラー
        local_renderer = SlackMessageHtmlRenderer(asset_manager=asset_manager, emoji_resolver=mock_emoji_resolver)
        
        # HTMLをレンダリング（ローカルモード）
        html_local = local_renderer.render(test_message, mock_user_resolver)
        print("  ローカルモードのHTML（一部）:")
        print(f"    {html_local[:200]}...")
        
        # デバッグ情報を出力
        print(f"  期待するローカルパス: {avatar_local_path}")
        print(f"  アバターURL: {test_avatar_url}")
        print(f"  アバターがダウンロード済み: {asset_manager.is_downloaded(test_avatar_url)}")
        print(f"  ローカルパスがHTMLに含まれている: {avatar_local_path in html_local}")
        
        # ローカルモードではローカルパスが含まれていることを確認
        assert avatar_local_path in html_local, f"ローカルモードでローカルパスが含まれていません: {avatar_local_path}"
        
        # 絵文字が画像タグに変換されているかチェック
        assert '<img' in html_local, "絵文字が画像タグに変換されていません"
        assert 'slack-emoji' in html_local, "slack-emojiクラスが含まれていません"
        
        print("  ✅ ローカルモードテスト成功")
        
        print("\n3. フィルター処理の順序テスト:")
        # フィルター処理の順序を確認
        # 1. emoji_replace: :smile: → <img src="https://...">
        # 2. local_asset_replace: <img src="https://..."> → <img src="assets/...">
        
        # 絵文字URLがローカルパスに置換されているかチェック
        emoji_local_path = asset_manager.get_local_path(test_emoji_url)
        
        print(f"  絵文字URL: {test_emoji_url}")
        print(f"  絵文字ローカルパス: {emoji_local_path}")
        print(f"  絵文字がダウンロード済み: {asset_manager.is_downloaded(test_emoji_url)}")
        print(f"  元のURLがHTMLに含まれている: {test_emoji_url in html_local}")
        print(f"  ローカルパスがHTMLに含まれている: {emoji_local_path in html_local}")
        
        # HTMLの内容を詳しく確認
        if test_emoji_url in html_local:
            print(f"  問題: 元の絵文字URLが残っています")
            # HTMLから絵文字のimgタグを探す
            import re
            img_pattern = r'<img[^>]+src="[^"]*"[^>]*>'
            img_tags = re.findall(img_pattern, html_local)
            print(f"  見つかったimgタグ数: {len(img_tags)}")
            for i, tag in enumerate(img_tags):
                print(f"    {i+1}: {tag}")
        
        # 元のURLが含まれていないことを確認
        assert test_emoji_url not in html_local, "元の絵文字URLが残っています"
        
        # ローカルパスが含まれていることを確認（絵文字がダウンロード済みの場合）
        if asset_manager.is_downloaded(test_emoji_url):
            assert emoji_local_path in html_local, f"絵文字のローカルパスが含まれていません: {emoji_local_path}"
        
        print("  ✅ フィルター処理順序テスト成功")
        
        print("\n✅ 統合されたレンダラーテスト完了")


if __name__ == "__main__":
    test_integrated_renderer() 