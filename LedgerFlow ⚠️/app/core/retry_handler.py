"""
Bounded Retry Handler for Master Simulation Engine

This module implements the retry logic with exponential backoff as specified in FR-9.
It provides retryable failures handling for network, PDF, and other transient errors.
"""

import time
import logging
import functools
from typing import Callable, Any, Type, Union, List
from dataclasses import dataclass
from enum import Enum


class RetryableException(Exception):
    """Base exception for retryable errors"""
    pass


class NetworkException(RetryableException):
    """Network-related retryable exception"""
    pass


class PDFGenerationException(RetryableException):
    """PDF generation retryable exception"""
    pass


class InvoiceGenerationException(RetryableException):
    """Invoice generation retryable exception"""
    pass


class RetryExhaustedException(Exception):
    """Exception raised when max retry attempts are exhausted"""
    def __init__(self, message: str, last_exception: Exception, attempt_count: int):
        super().__init__(message)
        self.last_exception = last_exception
        self.attempt_count = attempt_count


@dataclass
class RetryResult:
    """Result of a retry operation"""
    success: bool
    result: Any = None
    error: Exception = None
    attempt_count: int = 0
    total_time: float = 0.0


class BoundedRetryHandler:
    """
    Bounded retry handler with exponential backoff.
    
    Implements the retry logic specified in FR-9:
    - ≤ 3 retries with exponential back-off
    - Mark failed batches with last_error after max retries
    - Allow partial success with per-invoice failure reporting
    """
    
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        """
        Initialize retry handler.
        
        Args:
            max_attempts: Maximum number of retry attempts (≤ 3 as per FR-9)
            base_delay: Base delay in seconds for exponential backoff
            max_delay: Maximum delay between retries
        """
        self.max_attempts = min(max_attempts, 3)  # Enforce FR-9 constraint
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.logger = logging.getLogger(__name__)
    
    def execute_with_retry(
        self, 
        operation: Callable, 
        *args, 
        retryable_exceptions: Union[Type[Exception], List[Type[Exception]]] = None,
        **kwargs
    ) -> RetryResult:
        """
        Execute operation with retry logic.
        
        Args:
            operation: Function to execute
            *args: Arguments for the operation
            retryable_exceptions: Exception types that should trigger retry
            **kwargs: Keyword arguments for the operation
            
        Returns:
            RetryResult with success status and result/error
        """
        if retryable_exceptions is None:
            retryable_exceptions = [RetryableException]
        elif not isinstance(retryable_exceptions, list):
            retryable_exceptions = [retryable_exceptions]
        
        start_time = time.time()
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                self.logger.debug(f"Executing operation, attempt {attempt + 1}/{self.max_attempts}")
                result = operation(*args, **kwargs)
                
                total_time = time.time() - start_time
                self.logger.info(f"Operation succeeded on attempt {attempt + 1}")
                
                return RetryResult(
                    success=True,
                    result=result,
                    attempt_count=attempt + 1,
                    total_time=total_time
                )
                
            except Exception as e:
                last_exception = e
                
                # Check if this exception is retryable
                is_retryable = any(isinstance(e, exc_type) for exc_type in retryable_exceptions)
                
                if not is_retryable or attempt == self.max_attempts - 1:
                    # Either not retryable or last attempt
                    total_time = time.time() - start_time
                    self.logger.error(f"Operation failed after {attempt + 1} attempts: {str(e)}")
                    
                    return RetryResult(
                        success=False,
                        error=e,
                        attempt_count=attempt + 1,
                        total_time=total_time
                    )
                
                # Calculate delay with exponential backoff
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                
                self.logger.warning(
                    f"Attempt {attempt + 1} failed with {type(e).__name__}: {str(e)}. "
                    f"Retrying in {delay:.2f} seconds..."
                )
                
                time.sleep(delay)
        
        # This should never be reached, but just in case
        total_time = time.time() - start_time
        return RetryResult(
            success=False,
            error=last_exception or Exception("Unknown error"),
            attempt_count=self.max_attempts,
            total_time=total_time
        )
    
    def retry_decorator(
        self, 
        retryable_exceptions: Union[Type[Exception], List[Type[Exception]]] = None
    ):
        """
        Decorator for automatic retry functionality.
        
        Args:
            retryable_exceptions: Exception types that should trigger retry
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                result = self.execute_with_retry(
                    func, 
                    *args, 
                    retryable_exceptions=retryable_exceptions,
                    **kwargs
                )
                
                if result.success:
                    return result.result
                else:
                    raise RetryExhaustedException(
                        f"Operation failed after {result.attempt_count} attempts",
                        result.error,
                        result.attempt_count
                    )
            
            return wrapper
        return decorator


class CircuitBreaker:
    """
    Circuit breaker implementation for external service calls.
    
    Implements circuit breaker pattern to prevent cascading failures
    and provide graceful degradation under load.
    """
    
    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"
    
    def __init__(
        self, 
        failure_threshold: int = 5, 
        timeout: int = 60, 
        slo_window: int = 300
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
            slo_window: SLO monitoring window in seconds (5 minutes as per FR-8)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.slo_window = slo_window
        self.failure_count = 0
        self.last_failure_time = None
        self.state = self.State.CLOSED
        self.logger = logging.getLogger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function through circuit breaker.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenException: When circuit is open
        """
        if self.state == self.State.OPEN:
            if time.time() - self.last_failure_time > self.timeout:
                self.state = self.State.HALF_OPEN
                self.logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        if self.state == self.State.HALF_OPEN:
            self.state = self.State.CLOSED
            self.logger.info("Circuit breaker closed after successful operation")
    
    def on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = self.State.OPEN
            self.logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open"""
    pass


# Convenience functions for common retry patterns
def retry_on_network_error(max_attempts: int = 3):
    """Decorator for retrying on network errors"""
    handler = BoundedRetryHandler(max_attempts=max_attempts)
    return handler.retry_decorator([NetworkException, ConnectionError, TimeoutError])


def retry_on_pdf_error(max_attempts: int = 3):
    """Decorator for retrying on PDF generation errors"""
    handler = BoundedRetryHandler(max_attempts=max_attempts)
    return handler.retry_decorator([PDFGenerationException])


def retry_on_invoice_error(max_attempts: int = 3):
    """Decorator for retrying on invoice generation errors"""
    handler = BoundedRetryHandler(max_attempts=max_attempts)
    return handler.retry_decorator([InvoiceGenerationException])