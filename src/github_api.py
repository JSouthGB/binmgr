import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests


class GitHubAPI:
    def __init__(self, logger):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'BinMgr-Binary-Manager'
        })
        self._logger = logger
        self._arch = self._get_system_arch()

    def get_latest_release(self, repo: str) -> Dict:
        """Get latest release version"""
        url = f'https://api.github.com/repos/{repo}/releases/latest'
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def _get_system_arch(self) -> str:
        """Get system architecture"""
        try:
            return subprocess.check_output(['uname', '-m']).decode().strip()
        except subprocess.SubprocessError:
            self._logger.error("Failed to detect system architecture, assuming x86_64")
            return 'x86_64'

    def is_compatible_binary(self, asset_name: str) -> Tuple[bool, str]:
        """
        Check if an asset is compatible with the current system
        Returns a tuple of (is_compatible, reason).
        """
        name = asset_name.lower()

        # Explicitly reject Windows
        if any(win in name for win in ['windows', '-pc-', '.exe']):
            return False, "Windows binary detected"

        # Check archive type
        if not any(ext in name for ext in ['.tar.gz', '.tgz', '.zip']):
            return False, "Not a supported archive format"

        # Check architecture
        if self._arch == 'x86_64':
            if not ('x86_64' in name or 'amd64' in name):
                return False, "Architecture doesn't match x86_64/amd64"
            if any(a in name for a in ['386', 'arm64', 'aarch64', 'arm']):
                return False, (f"Found incompatible architecture indicator:"
                               f" {[a for a in ['386', 'arm64', 'aarch64', 'arm'] if a in name][0]}")

        # Check designated binary platform
        if not any(p in name for p in ['linux', 'unknown-linux']):
            return False, "Not a Linux binary"

        # Check it's not a package
        if any(fmt in name for fmt in ['.deb', '.rpm', '.apk', '.pkg.tar.', '.pacman']):
            return False, (f"Package format detected:"
                           f" {[fmt for fmt in ['.deb', '.rpm', '.apk', '.pkg.tar.', '.pacman'] if fmt in name][0]}")

        return True, "Compatible binary found"

    def find_linux_binary(self, assets: list, program_name: str) -> Tuple[Optional[Dict], Optional[str]]:
        """Find the most appropriate Linux binary from archive file"""
        self._logger.debug(f"Searching for Linux binary among {len(assets)} assets", program_name)

        compatible_assets = []
        for asset in assets:
            name = asset['name']
            is_compatible, reason = self.is_compatible_binary(name)

            self._logger.debug(f"Checking asset: {name}", program_name)
            self._logger.debug(f"Compatibility: {reason}", program_name)

            if is_compatible:
                compatible_assets.append((asset, self._get_archive_type(name)))

        if not compatible_assets:
            self._logger.debug("Available assets:", program_name)
            for asset in assets:
                self._logger.debug(f"- {asset['name']}", program_name)
            return None, None

        # If multiple compatible assets, prefer the one with the program name
        for asset, archive_type in compatible_assets:
            if program_name.lower() in asset['name'].lower():
                self._logger.info(f"Selected asset: {asset['name']}", program_name)
                return asset, archive_type

        # If no asset with program name, take the first compatible one
        self._logger.info(f"Selected asset: {compatible_assets[0][0]['name']}", program_name)
        return compatible_assets[0]

    @staticmethod
    def _get_archive_type(filename: str) -> Optional[str]:
        """Determine archive type from filename."""
        if filename.endswith(('.tar.gz', '.tgz')):
            return 'tar'
        elif filename.endswith('.zip'):
            return 'zip'
        return None

    def download_file(self, url: str, dest_path: Path) -> None:
        """Download archive file"""
        response = self.session.get(url, stream=True)
        response.raise_for_status()

        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
