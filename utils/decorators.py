"""
Decorator utilities for adding functionality to functions and methods.
Provides decorators for timing, caching, retrying, and logging.
"""

import time
import logging
import functools
from typing import Any, Callable, Dict, Optional, Tuple
from datetime import datetime, timedelta


def timer(func: Callable) -> Callable:
    """
    Decorator to measure and log function execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
    
    return wrapper


def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0, 
          exceptions: Tuple[Exception, ...] = (Exception,)) -> Callable:
    """
    Decorator to retry function execution on failure.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Tuple of exception types to catch and retry
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logging.warning(
                            f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {current_delay:.2f} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logging.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def cache_result(ttl_seconds: Optional[float] = None) -> Callable:
    """
    Decorator to cache function results with optional TTL.
    
    Args:
        ttl_seconds: Time to live for cached results in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[str, Tuple[Any, datetime]] = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Check if result is cached and valid
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                
                if ttl_seconds is None or (datetime.now() - timestamp).total_seconds() < ttl_seconds:
                    logging.debug(f"Cache hit for {func.__name__}")
                    return result
                else:
                    # Remove expired cache entry
                    del cache[cache_key]
                    logging.debug(f"Cache expired for {func.__name__}")
            
            # Execute function and cache result
            logging.debug(f"Cache miss for {func.__name__}")
            result = func(*args, **kwargs)
            cache[cache_key] = (result, datetime.now())
            
            return result
        
        # Add cache management methods
        def clear_cache():
            cache.clear()
            logging.info(f"Cache cleared for {func.__name__}")
        
        def get_cache_info():
            return {
                'size': len(cache),
                'keys': list(cache.keys()),
                'function': func.__name__
            }
        
        wrapper.clear_cache = clear_cache
        wrapper.get_cache_info = get_cache_info
        
        return wrapper
    return decorator


def log_execution(level: int = logging.INFO, include_args: bool = False, 
                 include_result: bool = False) -> Callable:
    """
    Decorator to log function execution.
    
    Args:
        level: Logging level
        include_args: Whether to include function arguments in log
        include_result: Whether to include function result in log
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            
            # Log function entry
            if include_args:
                logger.log(level, f"Executing {func.__name__} with args={args}, kwargs={kwargs}")
            else:
                logger.log(level, f"Executing {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                
                # Log successful completion
                if include_result:
                    logger.log(level, f"{func.__name__} completed successfully with result: {result}")
                else:
                    logger.log(level, f"{func.__name__} completed successfully")
                
                return result
                
            except Exception as e:
                logger.error(f"{func.__name__} failed with error: {e}")
                raise
        
        return wrapper
    return decorator


def validate_types(**type_checks) -> Callable:
    """
    Decorator to validate function argument types.
    
    Args:
        **type_checks: Keyword arguments mapping parameter names to expected types
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate types
            for param_name, expected_type in type_checks.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not isinstance(value, expected_type) and value is not None:
                        raise TypeError(
                            f"Parameter '{param_name}' must be of type {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def deprecated(reason: str = "This function is deprecated") -> Callable:
    """
    Decorator to mark functions as deprecated.
    
    Args:
        reason: Reason for deprecation
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn(
                f"{func.__name__} is deprecated: {reason}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def singleton(cls: type) -> type:
    """
    Decorator to make a class a singleton.
    
    Args:
        cls: Class to make singleton
        
    Returns:
        Singleton class
    """
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


def rate_limit(calls_per_second: float) -> Callable:
    """
    Decorator to rate limit function calls.
    
    Args:
        calls_per_second: Maximum number of calls per second
        
    Returns:
        Decorator function
    """
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        
        return wrapper
    return decorator
