import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class LogLevel(Enum):
    SUCCESS = '\033[92m'    # Green
    INFO =    '\033[94m'    # Blue
    WARNING = '\033[93m'    # Yellow
    ERROR =   '\033[91m'    # Red
    DEBUG =   '\033[90m'    # Gray
    RESET =   '\033[0m'     # Reset


class Logger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_file = log_dir / f"binmgr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self._setup_logger()

    def _setup_logger(self):
        """Setup file logging"""
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configure logger with detailed output
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))

        self.logger = logging.getLogger('binmgr')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)

    def log(self, message: str, level: LogLevel, program: Optional[str] = None, terminal_only: bool = False,
            file_only: bool = False):
        """Log to file and/or terminal based on flags"""
        prefix = f"[{program}] " if program else ""

        # detailed file logging
        if not terminal_only:
            if level == LogLevel.DEBUG:
                self.logger.debug(f"{prefix}{message}")
            elif level == LogLevel.INFO:
                self.logger.info(f"{prefix}{message}")
            elif level == LogLevel.WARNING:
                self.logger.warning(f"{prefix}{message}")
            elif level == LogLevel.ERROR:
                self.logger.error(f"{prefix}{message}")
            elif level == LogLevel.SUCCESS:
                self.logger.info(f"{prefix}SUCCESS: {message}")

        # minimal terminal logging
        if not file_only:
            print(f"{level.value}{prefix}{message}{LogLevel.RESET.value}")

    def success(self, message: str, program: Optional[str] = None):
        self.log(message, LogLevel.SUCCESS, program)

    def info(self, message: str, program: Optional[str] = None, file_only: bool = False):
        self.log(message, LogLevel.INFO, program, file_only=file_only)

    def warning(self, message: str, program: Optional[str] = None):
        self.log(message, LogLevel.WARNING, program)

    def error(self, message: str, program: Optional[str] = None):
        self.log(message, LogLevel.ERROR, program)

    def debug(self, message: str, program: Optional[str] = None):
        """Debug messages default to file only"""
        self.log(message, LogLevel.DEBUG, program, file_only=True)
