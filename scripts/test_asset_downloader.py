#!/usr/bin/env python3
"""AssetDownloaderテストスクリプト"""

import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.asset_manager import AssetManager
from src.utils.asset_downloader import AssetDownloader


def test_asset_downloader():
    """AssetDownloaderの基本機能をテスト"""
    print("=== AssetDownloader テスト ===")
    
    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerを初期化
        asset_manager = AssetManager(temp_dir)
        
        # モックのSlackクライアントを作成
        mock_client = Mock()
        
        # AssetDownloaderを初期化
        downloader = AssetDownloader(mock_client, asset_manager)
        
        print("\n1. Slack URL判定テスト:")
        test_urls = [
            "https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/smile.png",
            "https://files.slack.com/files-pri/T1234567890-F1234567890/avatar.jpg",
            "https://emoji.slack-edge.com/T1234567890/custom_emoji/1234567890.1234567890/custom.gif",
            "https://example.com/image.png",  # Slack以外のURL
            "https://google.com/logo.png"     # Slack以外のURL
        ]
        
        for url in test_urls:
            is_slack = downloader._is_slack_url(url)
            print(f"  {url} -> {'Slack' if is_slack else '非Slack'}")
        
        print("\n2. 絵文字URL抽出テスト:")
        test_text = """
        こんにちは！<img src="https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/smile.png" alt=":smile:" class="slack-emoji" width="20" height="20">
        素晴らしいですね<img src="https://emoji.slack-edge.com/T1234567890/custom_emoji/1234567890.1234567890/custom.gif" alt=":custom:" class="slack-emoji" width="20" height="20">
        """
        
        emoji_urls = downloader._extract_emoji_urls_from_text(test_text)
        print(f"  抽出された絵文字URL数: {len(emoji_urls)}")
        for url in emoji_urls:
            print(f"    {url}")
        
        print("\n3. ダウンロード統計テスト:")
        stats = downloader.get_download_stats()
        print(f"  ダウンロード済みURL数: {stats['downloaded_urls_count']}")
        print(f"  総アセット数: {stats['total_assets']}")
        
        print("\n4. キャッシュクリアテスト:")
        downloader.clear_download_cache()
        stats_after_clear = downloader.get_download_stats()
        print(f"  クリア後のダウンロード済みURL数: {stats_after_clear['downloaded_urls_count']}")
        
        print("\n✅ テスト完了")


def test_asset_downloader_with_mock_download():
    """モックダウンロード機能のテスト"""
    print("\n=== AssetDownloader モックダウンロードテスト ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerを初期化
        asset_manager = AssetManager(temp_dir)
        
        # モックのSlackクライアントを作成
        mock_client = Mock()
        
        # AssetDownloaderを初期化
        downloader = AssetDownloader(mock_client, asset_manager)
        
        # モックレスポンスを作成
        mock_response = Mock()
        mock_response.content = b"fake image content"
        mock_response.raise_for_status.return_value = None
        
        # requests.Session.getをモック
        with patch.object(downloader.session, 'get', return_value=mock_response):
            print("\n1. アセットダウンロードテスト:")
            test_url = "https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/smile.png"
            
            success = downloader.download_asset(
                test_url, 
                metadata={"type": "emoji", "name": "smile"}
            )
            
            print(f"  ダウンロード成功: {success}")
            print(f"  ローカルファイル存在: {asset_manager.is_downloaded(test_url)}")
            
            if success:
                local_path = asset_manager.get_local_path(test_url)
                absolute_path = asset_manager.get_absolute_path(test_url)
                print(f"  ローカルパス: {local_path}")
                print(f"  絶対パス: {absolute_path}")
                print(f"  ファイルサイズ: {absolute_path.stat().st_size} bytes")
        
        print("\n✅ モックダウンロードテスト完了")


if __name__ == "__main__":
    test_asset_downloader()
    test_asset_downloader_with_mock_download() 