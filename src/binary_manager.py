import os
import tarfile
import zipfile
import stat
from pathlib import Path
from typing import Optional, List
from logger import Logger


class BinaryManager:
    def __init__(self, bin_dir: Path, temp_dir: Path, logger: Logger):
        self.bin_dir = bin_dir
        self.temp_dir = temp_dir
        self.logger = logger

    def find_binary(self, files: List[Path], program_name: str) -> Optional[Path]:
        """Find the most probable binary file from extracted files."""
        self.logger.debug(f"Searching for binary '{program_name}' among {len(files)} files", program_name)
        candidates = []

        for file_path in files:
            self.logger.debug(f"Examining file: {file_path}", program_name)

            if not file_path.is_file():
                self.logger.debug(f"Skipping {file_path} (not a file)", program_name)
                continue

            # Log file permissions
            perms = oct(file_path.stat().st_mode)[-3:]
            self.logger.debug(f"File permissions for {file_path}: {perms}", program_name)

            # Consider file executable if it has any execute bits set or if it's named exactly as program
            is_executable = os.access(file_path, os.X_OK) or file_path.name == program_name
            if is_executable:
                self.logger.debug(f"Found executable file: {file_path}", program_name)
                # for exact match or program name match
                if (file_path.name == program_name or
                        program_name.lower() in file_path.name.lower()):
                    self.logger.debug(f"Adding candidate (name match): {file_path}", program_name)
                    candidates.append(file_path)
                # for nested binaries
                elif file_path.parent.name.startswith(program_name):
                    self.logger.debug(f"Adding candidate (parent dir match): {file_path}", program_name)
                    candidates.append(file_path)
            else:
                self.logger.debug(f"File not executable: {file_path}", program_name)

        if not candidates:
            self.logger.debug("No candidates found", program_name)
            return None

        # Prefer exact name match
        exact_matches = [c for c in candidates if c.name == program_name]
        if exact_matches:
            self.logger.debug(f"Found exact match: {exact_matches[0]}", program_name)
            return exact_matches[0]

        # Then prefer the shortest name (this should hopefully be the proper binary)
        selected = min(candidates, key=lambda x: len(x.name))
        self.logger.debug(f"Selected shortest name: {selected}", program_name)
        return selected

    def extract_archive(self, archive_path: Path, archive_type: str) -> List[Path]:
        """Extract archive"""
        extract_dir = self.temp_dir / archive_path.stem
        extract_dir.mkdir(exist_ok=True)

        if archive_type == 'tar':
            return self._extract_tar(archive_path, extract_dir)
        elif archive_type == 'zip':
            return self._extract_zip(archive_path, extract_dir)
        raise ValueError(f"Unsupported archive type: {archive_type}")

    @staticmethod
    def _extract_tar(archive_path: Path, extract_dir: Path) -> List[Path]:
        with tarfile.open(archive_path) as tar_archive:
            def is_within_directory(directory: Path, target: Path):
                abs_directory = directory.resolve()
                abs_target = target.resolve()
                prefix = os.path.commonpath([abs_directory, abs_target])
                return prefix == str(abs_directory)

            def safe_extract(tar, path: Path):
                for member in tar.getmembers():
                    member_path = path / member.name
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted path traversal in tar file")
                tar.extractall(path)

            safe_extract(tar_archive, extract_dir)

        return list(extract_dir.rglob('*'))

    @staticmethod
    def _extract_zip(archive_path: Path, extract_dir: Path) -> List[Path]:
        with zipfile.ZipFile(archive_path) as zip_ref:
            zip_ref.extractall(path=extract_dir)

        return list(extract_dir.rglob('*'))

    def install_binary(self, binary_path: Path, program_name: str) -> None:
        """Install binary to bin (~/.local/bin/)"""
        dest_path = self.bin_dir / program_name

        # Copy binary and set permissions
        import shutil
        shutil.copy2(binary_path, dest_path)
        # Ensure the binary is executable
        dest_path.chmod(dest_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        self.logger.debug(f"Installed binary to {dest_path} with permissions: {oct(dest_path.stat().st_mode)[-3:]}",
                          program_name)
