import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, List, Tuple

from binary_manager import BinaryManager
from config import ConfigManager
from github_api import GitHubAPI
from logger import Logger
from version_tracker import VersionTracker


class BinMgr:
    def __init__(self, config_path: Optional[str] = None):
        self.config = ConfigManager(config_path)
        self.logger = Logger(self.config.bin_dir / 'logs')
        self.github = GitHubAPI(self.logger)
        self.binary_manager = BinaryManager(self.config.bin_dir, self.config.temp_dir, self.logger)
        self.version_tracker = VersionTracker(self.config.version_file)
        self.failed_programs: List[Tuple[str, str]] = []
        self.programs: Dict[str, str] = {}

    def run(self):
        """Entry point"""
        try:
            self.config.ensure_directories()
            self.programs = self.config.get_programs()

            for program_name, repo in self.programs.items():
                try:
                    self._process_program(program_name, repo)
                except Exception as e:
                    self.logger.error(f"Failed to process: {str(e)}", program_name)
                    self.failed_programs.append((program_name, str(e)))

            if self.failed_programs:
                self._handle_failures()

        finally:
            self.config.cleanup()

    def _process_program(self, program_name: str, repo: str):
        """Process a single program."""
        self.logger.info(f"Processing {program_name} from {repo}", program_name)

        try:
            # Get latest release
            release_data = self.github.get_latest_release(repo)
            latest_version = release_data['tag_name']
            self.logger.info(f"Latest version: {latest_version}", program_name)

            # Check if update needed
            current_version = self.version_tracker.get_version(program_name)
            if current_version == latest_version:
                self.logger.success(f"Already at latest version {latest_version}", program_name)
                return

            # Find appropriate binary
            asset, archive_type = self.github.find_linux_binary(release_data['assets'], program_name)
            if not asset:
                raise ValueError(f"No suitable binary found in release {latest_version}")
            if not archive_type:
                raise ValueError(f"Unsupported archive type for asset: {asset['name']}")

            # Download and process
            archive_path = self.config.temp_dir / asset['name']
            self.logger.info(f"Downloading from: {asset['browser_download_url']}", program_name)
            self.github.download_file(asset['browser_download_url'], archive_path)

            # Extract and find binary.
            extracted_files = self.binary_manager.extract_archive(archive_path, archive_type)
            binary_path = self.binary_manager.find_binary(extracted_files, program_name)
            if not binary_path:
                raise ValueError("Could not find binary in extracted files")

            # Install
            self.binary_manager.install_binary(binary_path, program_name)
            self.version_tracker.update_version(program_name, latest_version, release_data)
            self.logger.success(f"Successfully updated to version {latest_version}", program_name)

        except Exception as e:
            self.logger.error(f"Failed: {str(e)}", program_name)
            raise

    def _handle_failures(self):
        """Handle failed updates."""
        self.logger.warning("\nThe following programs failed to update:")
        for program, error in self.failed_programs:
            self.logger.error(f"{program}: {error}")

        if input("\nWould you like to retry failed updates? (y/n): ").lower() == 'y':
            failed_programs = [(prog, self.programs[prog]) for prog, _ in self.failed_programs]
            self.failed_programs = []
            for program_name, repo in failed_programs:
                try:
                    self._process_program(program_name, repo)
                except Exception as e:
                    self.logger.error(f"Retry failed: {str(e)}", program_name)


def main():
    parser = argparse.ArgumentParser(description="BinMgr - GitHub Binary Manager")
    parser.add_argument('--config', help='Path to configuration file')
    args = parser.parse_args()

    try:
        bot = BinMgr(args.config)
        bot.run()
    except Exception as e:
        logger = Logger(Path.home() / '.local' / 'bin' / 'logs')
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
