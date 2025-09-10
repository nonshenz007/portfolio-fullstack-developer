import logging
from logging.handlers import RotatingFileHandler
import os

class DiagnosticsLogger:
    """
    Captures errors, warnings, and info logs for LedgerFlow. Provides human-readable reporting and log retrieval.
    """
    LOG_FILE = 'app/logs/diagnostics.log'
    MAX_BYTES = 1024 * 1024  # 1MB
    BACKUP_COUNT = 3

    @staticmethod
    def get_logger():
        logger = logging.getLogger('LedgerFlowDiagnostics')
        if not logger.handlers:
            handler = RotatingFileHandler(DiagnosticsLogger.LOG_FILE, maxBytes=DiagnosticsLogger.MAX_BYTES, backupCount=DiagnosticsLogger.BACKUP_COUNT)
            formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @staticmethod
    def error(msg):
        DiagnosticsLogger.get_logger().error(msg)

    @staticmethod
    def warning(msg):
        DiagnosticsLogger.get_logger().warning(msg)

    @staticmethod
    def info(msg):
        DiagnosticsLogger.get_logger().info(msg)

    @staticmethod
    def get_recent_logs(lines=50):
        if not os.path.exists(DiagnosticsLogger.LOG_FILE):
            return []
        with open(DiagnosticsLogger.LOG_FILE, 'r') as f:
            return f.readlines()[-lines:] 