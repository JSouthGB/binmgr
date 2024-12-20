import os
import json
from pathlib import Path
from typing import Dict, Optional


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = self._find_config(config_path)
        self.config_data = self._load_config()
        self.bin_dir = Path.home() / '.local' / 'bin'
        self.temp_dir = self.bin_dir / '.binmgr_temp'
        self.version_file = self.bin_dir / 'binmgr_versions.json'

    @staticmethod
    def _find_config(provided_path: Optional[str]) -> Path:
        # Check command line argument
        if provided_path and os.path.exists(provided_path):
            return Path(provided_path)

        # Check environment variable, possible future use
        env_path = os.getenv('BINMGR_CONFIG')
        if env_path and os.path.exists(env_path):
            return Path(env_path)

        # Check default locations
        default_locations = [
            Path.cwd() / 'binmgr_config.json',
            Path.home() / '.config' / 'binmgr' / 'config.json',
            Path('/etc/binmgr/config.json')  # possible future use
        ]

        for path in default_locations:
            if path.exists():
                return path

        raise FileNotFoundError("No valid configuration file found")

    def _load_config(self) -> Dict:
        with open(self.config_path) as f:
            return json.load(f)

    def get_programs(self):
        return self.config_data.get('programs', {})

    def ensure_directories(self):
        """Verify directories exist."""
        self.bin_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def cleanup(self):
        """Clean up temp directory"""
        if self.temp_dir.exists():
            import shutil
            shutil.rmtree(self.temp_dir)
