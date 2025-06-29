import os
import json
from app.common import resource_path
from logging import getLogger
from typing import Any, Optional, Dict
logger = getLogger(__name__)


class ConfigManager:
    def __init__(self, config_path: str, default_config_path: str):
        self.config_path = config_path
        self.default_config_path = default_config_path
        
    def _get_default_config(self) -> dict:
        """デフォルト設定を読み込み"""
        with open(self.default_config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _verify_config(self, config: dict, default_config: dict = None) -> bool:
        """設定の構造が正しいかを検証"""
        if default_config is None:
            default_config = self._get_default_config()
        if not isinstance(config, dict) or not isinstance(default_config, dict):
            return False
        for key, value in default_config.items():
            if key not in config:
                return False
            if isinstance(value, dict):
                if not self._verify_config(config[key], value):
                    return False
        return True
    
    def _merge_with_default(self, config: dict) -> dict:
        """設定をデフォルト値でマージ（欠損値を補填）"""
        default_config = self._get_default_config()
        return self._deep_merge(default_config, config)
    
    def _deep_merge(self, default: dict, config: dict) -> dict:
        """辞書を再帰的にマージ"""
        result = default.copy()
        for key, value in config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def _get_changed_items(self, new_config: dict, old_config: dict) -> dict:
        """変更された項目を抽出（古い値を返す）"""
        result = {}
        for key in new_config:
            if key not in old_config:
                result[key] = None if not isinstance(new_config[key], dict) else {}
            elif isinstance(new_config[key], dict) and isinstance(old_config[key], dict):
                nested = self._get_changed_items(new_config[key], old_config[key])
                if nested:
                    result[key] = nested
            elif new_config[key] != old_config[key]:
                result[key] = old_config[key]
        return result
    
    def load(self) -> dict:
        """設定を読み込み（エラー時はデフォルト値で補填）"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Config file not found or corrupted, using default: {e}")
            config = self._get_default_config()
            self.save(config)
            return config
        
        # 構造検証し、不正な場合はデフォルトとマージ
        if not self._verify_config(config):
            logger.warning("Config structure invalid, merging with default")
            config = self._merge_with_default(config)
            self.save(config)
        
        return config
    
    def save(self, config: dict, on_change_callback=None) -> dict:
        """設定を保存（変更点のコールバック付き）"""
        # 既存の設定を読み込み
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                old_config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            old_config = self._get_default_config()
        
        # 変更点を抽出
        changed_items = self._get_changed_items(config, old_config)
        
        # 構造検証
        if not self._verify_config(config):
            raise ValueError("Config missing required keys or invalid structure.")
        
        # 保存
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        # 変更点があればコールバック実行
        if changed_items and on_change_callback:
            on_change_callback(changed_items, old_config, config)
        
        return changed_items
    
    def get_attribute(self, key: str) -> Optional[Any]:
        """属性を取得"""
        config = self.load()
        keys = key.split('.')
        current = config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            logger.warning(f"Requested non-existent attribute '{key}'")
            return None
    
    def set_attribute(self, key: str, value: Any, on_change_callback=None):
        """属性を設定"""
        config = self.load()
        keys = key.split('.')
        current = config
        
        # ネストした辞書を作成
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self.save(config, on_change_callback)


# Host設定用のコールバック関数
def _on_host_config_change(changed_items: dict, old_config: dict, new_config: dict):
    """Host設定変更時のコールバック"""
    if "run_on_startup" in changed_items.get("system", {}):
        from app.host.startup import update_run_on_startup
        update_run_on_startup(new_config.get("system", {}).get("run_on_startup", False))


# インスタンス作成
client_config_manager = ConfigManager(
    config_path=resource_path("client_config.json"),
    default_config_path=resource_path("app/resources/client_config_default.json")
)

host_config_manager = ConfigManager(
    config_path=resource_path("host_config.json"),
    default_config_path=resource_path("app/resources/host_config_default.json")
)


# 便利関数（後方互換性のため）
def load_client_config() -> dict:
    return client_config_manager.load()

def save_client_config(config: dict):
    return client_config_manager.save(config)

def get_client_attribute(key: str) -> Optional[Any]:
    return client_config_manager.get_attribute(key)

def set_client_attribute(key: str, value: Any):
    return client_config_manager.set_attribute(key, value)

def load_host_config() -> dict:
    return host_config_manager.load()

def save_host_config(config: dict):
    return host_config_manager.save(config, _on_host_config_change)

def get_host_attribute(key: str) -> Optional[Any]:
    return host_config_manager.get_attribute(key)

def set_host_attribute(key: str, value: Any):
    return host_config_manager.set_attribute(key, value, _on_host_config_change)


if __name__ == "__main__":
    # Example usage
    client_config = load_client_config()
    print("Client Config:", client_config, end="\n------------------\n")
    
    host_config = load_host_config()
    print("Host Config:", host_config, end="\n------------------\n")

    # ネストした属性のテスト
    startup_setting = get_host_attribute("system.run_on_startup")
    print("Startup Setting:", startup_setting, end="\n------------------\n")

    set_host_attribute("system.run_on_startup", True)
    print("Updated Host Config:", load_host_config(), end="\n------------------\n")