#!/usr/bin/env python3
"""AssetManagerテストスクリプト"""

import sys
import tempfile
import shutil
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.asset_manager import AssetManager


def test_asset_manager():
    """AssetManagerの基本機能をテスト"""
    print("=== AssetManager テスト ===")
    
    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerを初期化
        asset_manager = AssetManager(temp_dir)
        
        # テスト用URL
        test_urls = [
            "https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/smile.png",
            "https://files.slack.com/files-pri/T1234567890-F1234567890/avatar.jpg",
            "https://emoji.slack-edge.com/T1234567890/custom_emoji/1234567890.1234567890/custom.gif",
            "https://a.slack-edge.com/production-standard-emoji-assets/14.0/apple-medium/check_mark.webp"
        ]
        
        print("\n1. ローカルパス生成テスト:")
        for url in test_urls:
            local_path = asset_manager.get_local_path(url)
            absolute_path = asset_manager.get_absolute_path(url)
            print(f"  URL: {url}")
            print(f"  ローカルパス: {local_path}")
            print(f"  絶対パス: {absolute_path}")
            print(f"  ダウンロード済み: {asset_manager.is_downloaded(url)}")
            print()
        
        print("2. アセット登録テスト:")
        # テスト用のダミーファイルを作成
        test_asset_path = asset_manager.get_absolute_path(test_urls[0])
        test_asset_path.parent.mkdir(parents=True, exist_ok=True)
        test_asset_path.write_text("dummy content")
        
        # アセットを登録
        local_path = asset_manager.get_local_path(test_urls[0])
        asset_manager.register_asset(
            test_urls[0], 
            local_path, 
            metadata={"type": "emoji", "name": "smile"}
        )
        
        print(f"  登録したアセット: {test_urls[0]}")
        print(f"  ダウンロード済み: {asset_manager.is_downloaded(test_urls[0])}")
        
        # アセット情報を取得
        asset_info = asset_manager.get_asset_info(test_urls[0])
        print(f"  アセット情報: {asset_info}")
        
        print("\n3. アセット一覧テスト:")
        assets = asset_manager.list_assets()
        print(f"  登録済みアセット数: {len(assets)}")
        for url, info in assets.items():
            print(f"    {url} -> {info['local_path']}")
        
        print("\n4. 孤立ファイル削除テスト:")
        # 孤立したファイルを作成
        orphaned_file = asset_manager.assets_dir / "orphaned.txt"
        orphaned_file.write_text("orphaned content")
        print(f"  孤立ファイルを作成: {orphaned_file}")
        
        # 孤立ファイルを削除
        deleted_count = asset_manager.cleanup_orphaned_assets()
        print(f"  削除したファイル数: {deleted_count}")
        print(f"  孤立ファイルの存在: {orphaned_file.exists()}")
        
        print("\n✅ テスト完了")


if __name__ == "__main__":
    test_asset_manager() 