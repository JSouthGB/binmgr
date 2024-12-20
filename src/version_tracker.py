import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class VersionTracker:
    def __init__(self, version_file: Path):
        self.version_file = version_file
        self.versions = self._load_versions()

    def _load_versions(self) -> Dict:
        if self.version_file.exists():
            with open(self.version_file) as f:
                return json.load(f)
        return {}

    def save_versions(self) -> None:
        """Save versions to file"""
        with open(self.version_file, 'w') as f:
            # jetbrains bug requires `# type: ignore` (https://youtrack.jetbrains.com/issue/PY-76945)
            json.dump(self.versions, f, indent=2)  # type: ignore

    def get_version(self, program: str) -> Optional[str]:
        """Get the current version"""
        return self.versions.get(program, {}).get('version')

    def update_version(self, program: str, version: str, release_data: Dict) -> None:
        """Update version information"""
        self.versions[program] = {
            'version': version,
            'installation_date': datetime.now().isoformat(),
            'release_date': release_data.get('published_at'),
            'source_url': release_data.get('html_url'),
            'checksum': release_data.get('body', '').find('SHA256')
        }
        self.save_versions()
