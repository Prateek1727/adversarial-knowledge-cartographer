"""
Error handling utilities for the Adversarial Knowledge Cartographer.

This module provides comprehensive error handling including exponential backoff,
graceful degradation, and state recovery mechanisms.
"""

import logging
import time
import json
import pickle
from typing import Optional, Callable, Any, TypeVar
from functools import wraps
from pathlib import Path

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryableError(Exception):
    """Exception that indicates an operation should be retried."""
    pass


class NonRetryableError(Exception):
    """Exception that indicates an operation should not be retried."""
    pass


class StateRecoveryError(Exception):
    """Exception raised when state recovery fails."""
    pass


def exponential_backoff_retry(
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    max_backoff: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        max_backoff: Maximum backoff time in seconds
        backoff_factor: Multiplier for backoff time on each retry
        jitter: Whether to add random jitter to backoff time
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            backoff_time = initial_backoff
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                    
                except NonRetryableError:
                    # Don't retry non-retryable errors
                    raise
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        # Last attempt failed
                        logger.error(
                            f"Function {func.__name__} failed after {max_retries} attempts: {e}"
                        )
                        raise
                    
                    # Calculate backoff time with optional jitter
                    if jitter:
                        import random
                        jitter_factor = random.uniform(0.5, 1.5)
                        actual_backoff = min(backoff_time * jitter_factor, max_backoff)
                    else:
                        actual_backoff = min(backoff_time, max_backoff)
                    
                    logger.warning(
                        f"Function {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {e}. "
                        f"Retrying in {actual_backoff:.2f}s"
                    )
                    
                    time.sleep(actual_backoff)
                    backoff_time *= backoff_factor
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def graceful_degradation(
    default_value: Any = None,
    log_error: bool = True
):
    """
    Decorator for graceful degradation with partial data.
    
    If the function fails, returns the default value instead of raising an exception.
    
    Args:
        default_value: Value to return on failure
        log_error: Whether to log the error
        
    Returns:
        Decorated function with graceful degradation
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"Function {func.__name__} failed, using default value: {e}"
                    )
                return default_value
        
        return wrapper
    return decorator


class StateCheckpoint:
    """
    Manages state checkpoints for recovery.
    
    Provides functionality to save and restore workflow state to/from disk.
    """
    
    def __init__(self, checkpoint_dir: str = ".checkpoints"):
        """
        Initialize state checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoint files
        """
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        logger.info(f"StateCheckpoint initialized with directory: {self.checkpoint_dir}")
    
    def save_checkpoint(
        self,
        state: Any,
        checkpoint_id: str,
        format: str = "json"
    ) -> Path:
        """
        Save a state checkpoint to disk.
        
        Args:
            state: State object to save
            checkpoint_id: Unique identifier for this checkpoint
            format: Format to use ('json' or 'pickle')
            
        Returns:
            Path to the saved checkpoint file
            
        Raises:
            StateRecoveryError: If checkpoint save fails
        """
        try:
            if format == "json":
                checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
                
                # Convert state to dict if it has model_dump method (Pydantic)
                if hasattr(state, 'model_dump'):
                    state_dict = state.model_dump()
                elif hasattr(state, 'dict'):
                    state_dict = state.dict()
                else:
                    state_dict = state
                
                with open(checkpoint_path, 'w', encoding='utf-8') as f:
                    json.dump(state_dict, f, indent=2, default=str)
                
            elif format == "pickle":
                checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.pkl"
                
                with open(checkpoint_path, 'wb') as f:
                    pickle.dump(state, f)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Checkpoint saved: {checkpoint_path}")
            return checkpoint_path
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint '{checkpoint_id}': {e}")
            raise StateRecoveryError(f"Checkpoint save failed: {e}")
    
    def load_checkpoint(
        self,
        checkpoint_id: str,
        format: str = "json",
        state_class: Optional[type] = None
    ) -> Any:
        """
        Load a state checkpoint from disk.
        
        Args:
            checkpoint_id: Unique identifier for the checkpoint
            format: Format to use ('json' or 'pickle')
            state_class: Optional class to reconstruct state object (for JSON)
            
        Returns:
            Loaded state object
            
        Raises:
            StateRecoveryError: If checkpoint load fails
        """
        try:
            if format == "json":
                checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.json"
                
                if not checkpoint_path.exists():
                    raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
                
                with open(checkpoint_path, 'r', encoding='utf-8') as f:
                    state_dict = json.load(f)
                
                # Reconstruct state object if class provided
                if state_class is not None:
                    state = state_class(**state_dict)
                else:
                    state = state_dict
                
            elif format == "pickle":
                checkpoint_path = self.checkpoint_dir / f"{checkpoint_id}.pkl"
                
                if not checkpoint_path.exists():
                    raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")
                
                with open(checkpoint_path, 'rb') as f:
                    state = pickle.load(f)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Checkpoint loaded: {checkpoint_path}")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load checkpoint '{checkpoint_id}': {e}")
            raise StateRecoveryError(f"Checkpoint load failed: {e}")
    
    def list_checkpoints(self) -> list[str]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint IDs
        """
        checkpoints = []
        
        for path in self.checkpoint_dir.glob("*.json"):
            checkpoints.append(path.stem)
        
        for path in self.checkpoint_dir.glob("*.pkl"):
            if path.stem not in checkpoints:
                checkpoints.append(path.stem)
        
        logger.debug(f"Found {len(checkpoints)} checkpoints")
        return checkpoints
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: Unique identifier for the checkpoint
            
        Returns:
            True if checkpoint was deleted, False if not found
        """
        deleted = False
        
        json_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        if json_path.exists():
            json_path.unlink()
            deleted = True
        
        pkl_path = self.checkpoint_dir / f"{checkpoint_id}.pkl"
        if pkl_path.exists():
            pkl_path.unlink()
            deleted = True
        
        if deleted:
            logger.info(f"Checkpoint deleted: {checkpoint_id}")
        else:
            logger.warning(f"Checkpoint not found: {checkpoint_id}")
        
        return deleted


def validate_partial_data(
    data: Any,
    required_fields: list[str],
    min_completeness: float = 0.5
) -> tuple[bool, float]:
    """
    Validate partial data and determine if it's sufficient to continue.
    
    Args:
        data: Data object to validate
        required_fields: List of required field names
        min_completeness: Minimum completeness ratio (0-1) to consider valid
        
    Returns:
        Tuple of (is_valid, completeness_ratio)
    """
    if not required_fields:
        return True, 1.0
    
    present_fields = 0
    
    for field in required_fields:
        if hasattr(data, field):
            value = getattr(data, field)
            # Check if field has a meaningful value
            if value is not None and value != "" and value != []:
                present_fields += 1
        elif isinstance(data, dict) and field in data:
            value = data[field]
            if value is not None and value != "" and value != []:
                present_fields += 1
    
    completeness = present_fields / len(required_fields)
    is_valid = completeness >= min_completeness
    
    logger.debug(
        f"Data validation: {present_fields}/{len(required_fields)} fields present "
        f"(completeness: {completeness:.2%}, valid: {is_valid})"
    )
    
    return is_valid, completeness


def handle_api_error(error: Exception) -> tuple[bool, Optional[float]]:
    """
    Analyze an API error and determine if it's retryable and what backoff to use.
    
    Args:
        error: Exception from API call
        
    Returns:
        Tuple of (is_retryable, suggested_backoff_seconds)
    """
    error_str = str(error).lower()
    
    # Rate limit errors - retryable with backoff
    if "rate limit" in error_str or "429" in error_str:
        logger.warning("Rate limit error detected")
        return True, 60.0  # Wait 1 minute for rate limits
    
    # Timeout errors - retryable with shorter backoff
    if "timeout" in error_str or "timed out" in error_str:
        logger.warning("Timeout error detected")
        return True, 5.0
    
    # Server errors (5xx) - retryable
    if "500" in error_str or "502" in error_str or "503" in error_str:
        logger.warning("Server error detected")
        return True, 10.0
    
    # Authentication errors - not retryable
    if "auth" in error_str or "401" in error_str or "403" in error_str:
        logger.error("Authentication error detected - not retryable")
        return False, None
    
    # Client errors (4xx except 429) - not retryable
    if "400" in error_str or "404" in error_str:
        logger.error("Client error detected - not retryable")
        return False, None
    
    # Unknown error - retryable with default backoff
    logger.warning("Unknown error type - will retry with default backoff")
    return True, 5.0
