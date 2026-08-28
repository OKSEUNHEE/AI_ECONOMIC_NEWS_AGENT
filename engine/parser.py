import os
import yaml
from typing import Dict, Any, List

class ConfigParser:
    """YAML crawler config loader and validator"""
    
    @staticmethod
    def load_config(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Config file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        ConfigParser.validate_config(config, file_path)
        return config

    @staticmethod
    def validate_config(config: Dict[str, Any], file_path: str):
        required_keys = ['site_id', 'site_name', 'target_url', 'selectors']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"[{file_path}] Missing required key: '{key}'")
                
        if 'container' not in config['selectors']:
            raise ValueError(f"[{file_path}] 'selectors' must contain 'container'")
            
        if 'fields' not in config['selectors'] or not isinstance(config['selectors']['fields'], dict):
            raise ValueError(f"[{file_path}] 'selectors' must contain 'fields' dictionary")

    @staticmethod
    def load_all_configs(configs_dir: str) -> List[Dict[str, Any]]:
        configs = []
        if not os.path.exists(configs_dir):
            return configs
            
        for file_name in sorted(os.listdir(configs_dir)):
            if file_name.endswith('.yml') or file_name.endswith('.yaml'):
                full_path = os.path.join(configs_dir, file_name)
                try:
                    cfg = ConfigParser.load_config(full_path)
                    cfg['_file_path'] = full_path
                    configs.append(cfg)
                except Exception as e:
                    print(f"⚠️ [{file_name}] Config load failed: {e}")
        return configs