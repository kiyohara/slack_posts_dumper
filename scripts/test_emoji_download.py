#!/usr/bin/env python3
"""絵文字ダウンロード機能のテストスクリプト"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.asset_downloader import AssetDownloader
from src.utils.asset_manager import AssetManager


def test_emoji_url_detection():
    """絵文字URL検出機能をテスト"""
    print("=== 絵文字URL検出テスト ===")
    
    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerとAssetDownloaderを初期化
        asset_manager = AssetManager(temp_dir)
        mock_client = Mock()
        downloader = AssetDownloader(mock_client, asset_manager)
        
        # テストケース
        test_emojis = [
            "smile",
            "heart",
            "+1",
            "slightly_smiling_face",
            "custom_emoji"
        ]
        
        for emoji_name in test_emojis:
            print(f"\n絵文字名: {emoji_name}")
            emoji_url = downloader._get_emoji_url(emoji_name)
            print(f"  取得されたURL: {emoji_url}")
            
            if emoji_url:
                # URLがSlackのドメインかチェック
                is_slack = downloader._is_slack_url(emoji_url)
                print(f"  Slackドメイン: {is_slack}")
                
                # ローカルパスを生成
                local_path = asset_manager.get_local_path(emoji_url)
                print(f"  ローカルパス: {local_path}")
            else:
                print("  URL取得失敗")
        
        print("\n✅ 絵文字URL検出テスト完了")


def test_emoji_download_with_auth():
    """認証付き絵文字ダウンロードをテスト"""
    print("\n=== 認証付き絵文字ダウンロードテスト ===")
    
    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerとAssetDownloaderを初期化
        asset_manager = AssetManager(temp_dir)
        mock_client = Mock()
        mock_client.token = "xoxb-test-token"  # テスト用トークン
        downloader = AssetDownloader(mock_client, asset_manager)
        
        # 認証ヘッダーが設定されているかチェック
        auth_header = downloader.session.headers.get('Authorization')
        print(f"認証ヘッダー: {auth_header}")
        
        if auth_header:
            print("✅ 認証ヘッダーが設定されています")
        else:
            print("❌ 認証ヘッダーが設定されていません")
        
        print("✅ 認証付き絵文字ダウンロードテスト完了")


if __name__ == "__main__":
    test_emoji_url_detection()
    test_emoji_download_with_auth()
    print("\n🎉 全テスト完了") 