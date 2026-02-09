"""
Enhanced error handling and recovery mechanisms
Provides retry logic, circuit breaker, and graceful degradation
"""
import time
from typing import Callable, Any, Optional, TypeVar, Dict
from functools import wraps
from .logger import logger

T = TypeVar('T')


class CircuitBreaker:
    """Circuit breaker pattern for API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None if circuit is open
        """
        if self.state == 'OPEN':
            if time.time() - self.last_failure_time > self.timeout:
                self.state = 'HALF_OPEN'
                logger.warning("Circuit breaker: Entering HALF_OPEN state")
            else:
                logger.error("Circuit breaker: OPEN - Request blocked")
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        if self.state == 'HALF_OPEN':
            self.state = 'CLOSED'
            logger.info("Circuit breaker: Entering CLOSED state")
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.error(f"Circuit breaker: OPEN (after {self.failure_count} failures)")


class RetryPolicy:
    """Retry policy for failed API calls"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0, initial_delay: float = 1.0):
        """
        Initialize retry policy
        
        Args:
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff factor
            initial_delay: Initial delay in seconds
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.initial_delay = initial_delay
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = self.initial_delay * (self.backoff_factor ** (attempt - 1))
                    logger.warning(f"Retry attempt {attempt}/{self.max_retries} after {delay:.1f}s")
                    time.sleep(delay)
                
                return func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                logger.error(f"Attempt {attempt + 1}/{self.max_retries + 1} failed: {str(e)}")
                
                if attempt == self.max_retries:
                    logger.error(f"All {self.max_retries + 1} retry attempts failed")
                    break
        
        raise last_exception


def retry(max_retries: int = 3, backoff_factor: float = 2.0, initial_delay: float = 1.0):
    """
    Decorator for automatic retry logic
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff factor
        initial_delay: Initial delay in seconds
    """
    def decorator(func: Callable) -> Callable:
        retry_policy = RetryPolicy(max_retries, backoff_factor, initial_delay)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return retry_policy.execute(func, *args, **kwargs)
        
        return wrapper
    return decorator


def handle_errors(func: Callable) -> Callable:
    """
    Decorator for graceful error handling
    Logs errors and returns None instead of raising
    
    Args:
        func: Function to wrap
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    
    return wrapper


class ErrorRecoveryManager:
    """Manage error recovery and fallback strategies"""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.retry_policy = RetryPolicy()
        self.error_log: Dict[str, int] = {}
    
    def log_error(self, error_key: str) -> None:
        """
        Log an error occurrence
        
        Args:
            error_key: Key to identify error type
        """
        self.error_log[error_key] = self.error_log.get(error_key, 0) + 1
        logger.debug(f"Error logged: {error_key} (count: {self.error_log[error_key]})")
    
    def get_error_summary(self) -> Dict[str, int]:
        """
        Get summary of logged errors
        
        Returns:
            Dictionary of error counts
        """
        return self.error_log.copy()
    
    def clear_error_log(self) -> None:
        """Clear error log"""
        self.error_log.clear()
        logger.debug("Error log cleared")
    
    def is_error_spike(self, error_key: str, threshold: int = 10) -> bool:
        """
        Check if error spike is occurring
        
        Args:
            error_key: Error type to check
            threshold: Threshold for spike detection
            
        Returns:
            True if error count exceeds threshold
        """
        return self.error_log.get(error_key, 0) >= threshold


# Global recovery manager instance
recovery_manager = ErrorRecoveryManager()
