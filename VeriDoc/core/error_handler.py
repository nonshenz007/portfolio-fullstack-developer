"""
Production-Ready Error Handling System for VeriDoc

This module provides comprehensive error handling, logging, and recovery
mechanisms for the VeriDoc application.
"""

import logging
import traceback
import sys
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json
import time
from datetime import datetime


class ErrorSeverity(Enum):
    """Error severity levels for classification and handling."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization and handling."""
    SYSTEM = "system"
    VALIDATION = "validation"
    PROCESSING = "processing"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    NETWORK = "network"
    USER_INPUT = "user_input"
    DEPENDENCY = "dependency"


@dataclass
class VeriDocError:
    """Structured error information for VeriDoc."""
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    error_code: str
    user_message: str
    technical_details: Dict[str, Any]
    timestamp: datetime
    traceback: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    recoverable: bool = True
    suggested_actions: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'error_code': self.error_code,
            'user_message': self.user_message,
            'technical_details': self.technical_details,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback,
            'context': self.context or {},
            'recoverable': self.recoverable,
            'suggested_actions': self.suggested_actions or []
        }

    @classmethod
    def from_exception(cls, exc: Exception, category: ErrorCategory = ErrorCategory.SYSTEM,
                      severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                      user_message: str = None, context: Dict[str, Any] = None) -> 'VeriDocError':
        """Create VeriDocError from a Python exception."""
        return cls(
            message=str(exc),
            category=category,
            severity=severity,
            error_code=f"{category.value.upper()}_{type(exc).__name__.upper()}",
            user_message=user_message or f"An error occurred: {str(exc)}",
            technical_details={
                'exception_type': type(exc).__name__,
                'module': getattr(exc, '__module__', 'unknown'),
                'args': getattr(exc, 'args', [])
            },
            timestamp=datetime.now(),
            traceback=traceback.format_exc(),
            context=context or {},
            recoverable=severity != ErrorSeverity.CRITICAL
        )


class ErrorHandler:
    """Centralized error handling and logging system."""

    def __init__(self, log_dir: str = "logs", enable_audit: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.enable_audit = enable_audit

        # Setup logging
        self._setup_logging()

        # Error recovery strategies
        self.recovery_strategies: Dict[str, Callable] = {}

        # Error statistics
        self.error_stats = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_severity': {},
            'recovery_attempts': 0,
            'successful_recoveries': 0
        }

    def _setup_logging(self):
        """Setup comprehensive logging system."""
        # Main application logger
        self.logger = logging.getLogger('veridoc')
        self.logger.setLevel(logging.DEBUG)

        # Remove existing handlers to avoid duplicates
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Console handler for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)

        # File handler for production logging
        log_file = self.log_dir / f"veridoc_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # Error-specific file handler
        error_log_file = self.log_dir / f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)

        # Audit logger for security events
        if self.enable_audit:
            audit_log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.log"
            audit_handler = logging.FileHandler(audit_log_file, encoding='utf-8')
            audit_handler.setLevel(logging.INFO)
            audit_formatter = logging.Formatter(
                '%(asctime)s - AUDIT - %(message)s'
            )
            audit_handler.setFormatter(audit_formatter)

            self.audit_logger = logging.getLogger('veridoc_audit')
            self.audit_logger.addHandler(audit_handler)
            self.audit_logger.setLevel(logging.INFO)

    def handle_error(self, error: VeriDocError, attempt_recovery: bool = True) -> bool:
        """
        Handle an error with appropriate logging and recovery attempts.

        Args:
            error: The VeriDocError to handle
            attempt_recovery: Whether to attempt automatic recovery

        Returns:
            True if error was handled/recovered, False otherwise
        """
        # Update statistics
        self.error_stats['total_errors'] += 1
        self.error_stats['errors_by_category'][error.category.value] = \
            self.error_stats['errors_by_category'].get(error.category.value, 0) + 1
        self.error_stats['errors_by_severity'][error.severity.value] = \
            self.error_stats['errors_by_severity'].get(error.severity.value, 0) + 1

        # Log the error
        log_method = {
            ErrorSeverity.LOW: self.logger.info,
            ErrorSeverity.MEDIUM: self.logger.warning,
            ErrorSeverity.HIGH: self.logger.error,
            ErrorSeverity.CRITICAL: self.logger.critical
        }[error.severity]

        log_message = f"[{error.category.value}] {error.error_code}: {error.message}"
        if error.context:
            log_message += f" | Context: {json.dumps(error.context, default=str)}"

        log_method(log_message)

        if error.traceback:
            self.logger.debug(f"Traceback for {error.error_code}:\n{error.traceback}")

        # Attempt recovery if enabled and recoverable
        if attempt_recovery and error.recoverable:
            return self._attempt_recovery(error)

        return False

    def _attempt_recovery(self, error: VeriDocError) -> bool:
        """Attempt to recover from an error using registered strategies."""
        self.error_stats['recovery_attempts'] += 1

        strategy_key = f"{error.category.value}_{error.error_code}"

        if strategy_key in self.recovery_strategies:
            try:
                self.logger.info(f"Attempting recovery for {error.error_code}")
                success = self.recovery_strategies[strategy_key](error)
                if success:
                    self.error_stats['successful_recoveries'] += 1
                    self.logger.info(f"Successfully recovered from {error.error_code}")
                    return True
                else:
                    self.logger.warning(f"Recovery failed for {error.error_code}")
            except Exception as e:
                self.logger.error(f"Recovery strategy failed for {error.error_code}: {e}")

        return False

    def register_recovery_strategy(self, error_pattern: str, strategy: Callable) -> None:
        """Register a recovery strategy for specific error patterns."""
        self.recovery_strategies[error_pattern] = strategy
        self.logger.debug(f"Registered recovery strategy for {error_pattern}")

    def create_error(self, message: str, category: ErrorCategory = ErrorCategory.SYSTEM,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    error_code: str = None, user_message: str = None,
                    technical_details: Dict[str, Any] = None,
                    context: Dict[str, Any] = None) -> VeriDocError:
        """Create a new VeriDocError with proper structure."""
        if error_code is None:
            error_code = f"{category.value.upper()}_{severity.value.upper()}"

        return VeriDocError(
            message=message,
            category=category,
            severity=severity,
            error_code=error_code,
            user_message=user_message or message,
            technical_details=technical_details or {},
            timestamp=datetime.now(),
            context=context or {}
        )

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        stats = self.error_stats.copy()
        stats['recovery_rate'] = (
            stats['successful_recoveries'] / max(stats['recovery_attempts'], 1)
        )
        return stats

    def log_audit_event(self, event_type: str, user: str = "SYSTEM",
                       resource: str = None, action: str = None,
                       details: Dict[str, Any] = None) -> None:
        """Log security and audit events."""
        if not self.enable_audit:
            return

        audit_message = f"{event_type} | User: {user}"
        if resource:
            audit_message += f" | Resource: {resource}"
        if action:
            audit_message += f" | Action: {action}"
        if details:
            audit_message += f" | Details: {json.dumps(details, default=str)}"

        self.audit_logger.info(audit_message)


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_exception(exc: Exception, category: ErrorCategory = ErrorCategory.SYSTEM,
                    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                    user_message: str = None, context: Dict[str, Any] = None) -> bool:
    """Convenience function to handle exceptions."""
    error = VeriDocError.from_exception(exc, category, severity, user_message, context)
    return get_error_handler().handle_error(error)


# Common error recovery strategies
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying operations with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        raise e

                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)

            return None
        return wrapper
    return decorator


def safe_operation(operation_name: str, category: ErrorCategory = ErrorCategory.SYSTEM):
    """Decorator for safe operation execution with error handling."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler = get_error_handler()
                error = error_handler.create_error(
                    message=f"Operation '{operation_name}' failed: {str(e)}",
                    category=category,
                    severity=ErrorSeverity.MEDIUM,
                    user_message=f"Failed to complete {operation_name}. Please try again."
                )
                error_handler.handle_error(error)
                return None
        return wrapper
    return decorator
