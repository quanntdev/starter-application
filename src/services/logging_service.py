"""Logging service for application logs."""
import logging
import os
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


class LoggingService:
    """Service for managing application logs."""
    
    def __init__(self):
        # Get log directory in APPDATA
        appdata = os.getenv("APPDATA")
        if not appdata:
            appdata = os.path.expanduser("~")
        self.log_dir = Path(appdata).resolve() / "StarterAppLauncher" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file path
        self.log_file = self.log_dir / "app.log"
        
        # Setup logger
        self.logger = logging.getLogger("StarterAppLauncher")
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # File handler with rotation (max 5MB, keep 5 backups)
        self.file_handler = RotatingFileHandler(
            self.log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_handler)
        
        # Also log to console in development
        if not getattr(__import__('sys'), 'frozen', False):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def exception(self, message: str):
        """Log exception with traceback."""
        self.logger.exception(message)
    
    def get_logs(self, lines: int = 1000) -> list:
        """
        Get recent log lines from file.
        
        Args:
            lines: Number of lines to retrieve (default: 1000)
        
        Returns:
            List of log lines (most recent first)
        """
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                # Return last N lines, reversed so most recent is first
                return list(reversed(all_lines[-lines:]))
        except Exception as e:
            return [f"Error reading logs: {e}"]
    
    def clear_logs(self):
        """Clear all logs."""
        try:
            # Close all handlers first to release file locks
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)
            
            # Now we can safely delete the log files
            if self.log_file.exists():
                self.log_file.unlink()
            
            # Also clear rotated logs
            for i in range(1, 6):
                rotated_file = Path(f"{self.log_file}.{i}")
                if rotated_file.exists():
                    rotated_file.unlink()
            
            # Recreate handlers
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            self.file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=5 * 1024 * 1024,  # 5MB
                backupCount=5,
                encoding='utf-8'
            )
            self.file_handler.setLevel(logging.DEBUG)
            self.file_handler.setFormatter(formatter)
            self.logger.addHandler(self.file_handler)
            
            # Also recreate console handler if needed
            if not getattr(__import__('sys'), 'frozen', False):
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
            
            self.info("Logs cleared by user")
        except Exception as e:
            self.error(f"Error clearing logs: {e}")
            # Try to recreate handlers even if deletion failed
            try:
                formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                if not any(isinstance(h, RotatingFileHandler) for h in self.logger.handlers):
                    self.file_handler = RotatingFileHandler(
                        self.log_file,
                        maxBytes=5 * 1024 * 1024,
                        backupCount=5,
                        encoding='utf-8'
                    )
                    self.file_handler.setLevel(logging.DEBUG)
                    self.file_handler.setFormatter(formatter)
                    self.logger.addHandler(self.file_handler)
            except:
                pass
    
    def export_logs(self, output_path: Path) -> bool:
        """
        Export logs to a file.
        
        Args:
            output_path: Path to export logs to
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.log_file.exists():
                return False
            
            import shutil
            shutil.copy2(self.log_file, output_path)
            self.info(f"Logs exported to {output_path}")
            return True
        except Exception as e:
            self.error(f"Error exporting logs: {e}")
            return False


# Global logging service instance
_logging_service = None


def get_logging_service() -> LoggingService:
    """Get global logging service instance."""
    global _logging_service
    if _logging_service is None:
        _logging_service = LoggingService()
    return _logging_service

