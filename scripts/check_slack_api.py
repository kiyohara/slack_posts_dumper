#!/usr/bin/env python3
"""Slack API接続確認スクリプト"""

import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.slack_checker import SlackChecker


def parse_arguments():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description="Slack API接続確認ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 環境変数を使用
  python scripts/check_slack_api.py

  # 引数で指定
  python scripts/check_slack_api.py --workspace-id T1234567890 --channel-id C1234567890

  # 詳細ログ出力
  python scripts/check_slack_api.py --verbose

  # 一部のみ引数指定（channel-idは環境変数から取得）
  python scripts/check_slack_api.py --workspace-id T1234567890
        """
    )
    
    parser.add_argument(
        '--workspace-id',
        help='ワークスペースID（環境変数SLACK_WORKSPACE_IDより優先）'
    )
    
    parser.add_argument(
        '--channel-id',
        help='チャネルID（環境変数SLACK_CHANNEL_IDより優先）'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='詳細ログを出力'
    )
    
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_arguments()
    
    print("=== Slack API接続確認ツール ===")
    print()
    
    # SlackCheckerインスタンスを作成
    checker = SlackChecker(verbose=args.verbose)
    
    # 接続確認を実行
    success = checker.run_check(
        workspace_id=args.workspace_id,
        channel_id=args.channel_id
    )
    
    print()
    if success:
        print("✅ Slack API接続確認が完了しました。")
        sys.exit(0)
    else:
        print("❌ Slack API接続確認に失敗しました。")
        sys.exit(1)


if __name__ == "__main__":
    main() 