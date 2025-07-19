"""アセット管理ユーティリティ"""

import hashlib
import re
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import logging


class AssetManager:
    """アセット（画像、絵文字等）のローカル管理を行うクラス"""
    
    def __init__(self, base_dir: str):
        """
        AssetManagerを初期化
        
        Args:
            base_dir: アセットを保存するベースディレクトリ
        """
        self.base_dir = Path(base_dir)
        self.assets_dir = self.base_dir / "assets"
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # アセット情報を記録するファイル
        self.manifest_file = self.base_dir / "assets_manifest.json"
        self._manifest: Dict[str, Dict[str, Any]] = self._load_manifest()
    
    def get_local_path(self, url: str) -> str:
        """
        URLからローカルファイルパスを生成
        
        Args:
            url: アセットのURL
            
        Returns:
            ローカルファイルの相対パス（assets/ディレクトリからの相対パス）
        """
        # URLのハッシュ値を生成
        url_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        
        # URLからファイル拡張子を抽出
        extension = self._extract_extension_from_url(url)
        
        # ローカルファイル名を生成
        local_filename = f"{url_hash}{extension}"
        
        return str(Path("assets") / local_filename)
    
    def get_absolute_path(self, url: str) -> Path:
        """
        URLからローカルファイルの絶対パスを取得
        
        Args:
            url: アセットのURL
            
        Returns:
            ローカルファイルの絶対パス
        """
        local_path = self.get_local_path(url)
        return self.base_dir / local_path
    
    def is_downloaded(self, url: str) -> bool:
        """
        アセットが既にダウンロード済みかチェック
        
        Args:
            url: アセットのURL
            
        Returns:
            ダウンロード済みの場合はTrue
        """
        absolute_path = self.get_absolute_path(url)
        return absolute_path.exists()
    
    def register_asset(self, url: str, local_path: str, metadata: Optional[Dict[str, Any]] = None):
        """
        アセット情報をマニフェストに登録
        
        Args:
            url: アセットのURL
            local_path: ローカルファイルパス
            metadata: 追加のメタデータ
        """
        self._manifest[url] = {
            "local_path": local_path,
            "absolute_path": str(self.get_absolute_path(url)),
            "metadata": metadata or {},
            "registered_at": self._get_current_timestamp()
        }
        self._save_manifest()
        self.logger.debug(f"アセットを登録: {url} -> {local_path}")
    
    def get_asset_info(self, url: str) -> Optional[Dict[str, Any]]:
        """
        アセット情報を取得
        
        Args:
            url: アセットのURL
            
        Returns:
            アセット情報の辞書、見つからない場合はNone
        """
        return self._manifest.get(url)
    
    def list_assets(self) -> Dict[str, Dict[str, Any]]:
        """
        登録されているアセット一覧を取得
        
        Returns:
            アセット情報の辞書
        """
        return self._manifest.copy()
    
    def cleanup_orphaned_assets(self) -> int:
        """
        マニフェストに登録されていない孤立したファイルを削除
        
        Returns:
            削除したファイル数
        """
        deleted_count = 0
        
        # マニフェストに登録されているファイルの絶対パスを取得
        registered_paths = set()
        for asset_info in self._manifest.values():
            registered_paths.add(asset_info["absolute_path"])
        
        # assetsディレクトリ内のファイルをチェック
        for file_path in self.assets_dir.rglob("*"):
            if file_path.is_file():
                if str(file_path) not in registered_paths:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        self.logger.info(f"孤立したファイルを削除: {file_path}")
                    except Exception as e:
                        self.logger.warning(f"ファイル削除に失敗: {file_path}, エラー: {e}")
        
        return deleted_count
    
    def _extract_extension_from_url(self, url: str) -> str:
        """
        URLからファイル拡張子を抽出
        
        Args:
            url: アセットのURL
            
        Returns:
            ファイル拡張子（.jpg, .png等）
        """
        # URLパースでパスを取得
        parsed = urlparse(url)
        path = parsed.path
        
        # クエリパラメータを除去
        if '?' in path:
            path = path.split('?')[0]
        
        # 拡張子を抽出
        match = re.search(r'\.([a-zA-Z0-9]+)$', path)
        if match:
            extension = match.group(1).lower()
            # 一般的な画像形式のみ許可
            if extension in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                return f".{extension}"
        
        # 拡張子が見つからない場合はデフォルトで.png
        return ".png"
    
    def _load_manifest(self) -> Dict[str, Dict[str, Any]]:
        """マニフェストファイルを読み込み"""
        if self.manifest_file.exists():
            try:
                import json
                with open(self.manifest_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"マニフェストファイルの読み込みに失敗: {e}")
        
        return {}
    
    def _save_manifest(self):
        """マニフェストファイルを保存"""
        try:
            import json
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(self._manifest, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"マニフェストファイルの保存に失敗: {e}")
    
    def _get_current_timestamp(self) -> str:
        """現在のタイムスタンプを取得"""
        from datetime import datetime
        return datetime.now().isoformat() 