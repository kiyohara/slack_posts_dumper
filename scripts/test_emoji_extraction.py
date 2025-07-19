#!/usr/bin/env python3
"""絵文字名抽出機能のテストスクリプト"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.asset_downloader import AssetDownloader
from src.utils.asset_manager import AssetManager


def test_emoji_extraction():
    """絵文字名抽出機能をテスト"""
    print("=== 絵文字名抽出テスト ===")
    
    # 一時ディレクトリでテスト
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"テストディレクトリ: {temp_dir}")
        
        # AssetManagerとAssetDownloaderを初期化
        asset_manager = AssetManager(temp_dir)
        mock_client = Mock()
        downloader = AssetDownloader(mock_client, asset_manager)
        
        # テストケース
        test_cases = [
            ("こんにちは！:smile: 素晴らしいですね", ["smile"]),
            (":heart: 大好きです :+1: 素晴らしい", ["heart", "+1"]),
            ("絵文字なしのテキスト", []),
            ("複数の絵文字 :smile: :heart: :+1: :custom_emoji:", ["smile", "heart", "+1", "custom_emoji"]),
            ("特殊文字 :smile_face: :heart-eyes: :100:", ["smile_face", "heart-eyes", "100"]),
            ("絵文字の前後に文字 :smile:test:heart:", ["smile", "heart"]),
        ]
        
        for i, (text, expected) in enumerate(test_cases, 1):
            print(f"\n{i}. テストケース: {text}")
            extracted = downloader._extract_emoji_names_from_text(text)
            print(f"   抽出された絵文字名: {extracted}")
            print(f"   期待される絵文字名: {expected}")
            
            if extracted == expected:
                print("   ✅ 成功")
            else:
                print("   ❌ 失敗")
                return False
        
        print("\n✅ 絵文字名抽出テスト完了")
        return True


if __name__ == "__main__":
    success = test_emoji_extraction()
    sys.exit(0 if success else 1) 