"""
Structured logging configuration for the Adversarial Knowledge Cartographer.

This module provides structured logging with appropriate levels for different
types of events: DEBUG, INFO, WARNING, and ERROR.
"""

import logging
import sys
from typing import Optional
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that adds structured information to log records.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with structured information.
        
        Args:
            record: Log record to format
            
        Returns:
            Formatted log string
        """
        # Add structured fields if present in extra
        if hasattr(record, 'phase'):
            record.msg = f"[{record.phase}] {record.msg}"
        
        if hasattr(record, 'iteration'):
            record.msg = f"[iter={record.iteration}] {record.msg}"
        
        if hasattr(record, 'agent'):
            record.msg = f"[{record.agent}] {record.msg}"
        
        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Set up structured logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging output
        log_format: Optional custom log format string
    """
    # Default format with timestamp, level, module, and message
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = StructuredFormatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set specific log levels for noisy libraries (but allow DEBUG if explicitly set)
    if numeric_level > logging.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("anthropic").setLevel(logging.WARNING)
    else:
        # In DEBUG mode, show more detail but still suppress the noisiest ones
        logging.getLogger("httpx").setLevel(logging.INFO)
        logging.getLogger("httpcore").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.INFO)
    
    root_logger.info(f"Logging configured: level={log_level}, file={log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """
    Context manager for adding structured context to log messages.
    
    Example:
        with LogContext(phase="scout", iteration=1):
            logger.info("Processing sources")
            # Output: [scout] [iter=1] Processing sources
    """
    
    def __init__(self, **kwargs):
        """
        Initialize log context with structured fields.
        
        Args:
            **kwargs: Structured fields to add to log messages
        """
        self.context = kwargs
        self.old_factory = None
    
    def __enter__(self):
        """Enter the context and modify log record factory."""
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and restore original log record factory."""
        if self.old_factory:
            logging.setLogRecordFactory(self.old_factory)


def log_agent_transition(logger: logging.Logger, from_phase: str, to_phase: str, iteration: int):
    """
    Log an agent transition with structured information.
    
    Args:
        logger: Logger instance
        from_phase: Phase transitioning from
        to_phase: Phase transitioning to
        iteration: Current iteration number
    """
    logger.debug(
        f"Agent transition: {from_phase} -> {to_phase}",
        extra={'phase': to_phase, 'iteration': iteration}
    )


def log_entity_extraction(logger: logging.Logger, entity_count: int, phase: str):
    """
    Log entity extraction with structured information.
    
    Args:
        logger: Logger instance
        entity_count: Number of entities extracted
        phase: Current phase
    """
    logger.debug(
        f"Extracted {entity_count} entities",
        extra={'phase': phase, 'entity_count': entity_count}
    )


def log_phase_completion(logger: logging.Logger, phase: str, iteration: int, **metrics):
    """
    Log phase completion with metrics.
    
    Args:
        logger: Logger instance
        phase: Phase that completed
        iteration: Current iteration number
        **metrics: Additional metrics to log
    """
    metrics_str = ", ".join(f"{k}={v}" for k, v in metrics.items())
    logger.info(
        f"Phase completed: {metrics_str}",
        extra={'phase': phase, 'iteration': iteration, **metrics}
    )


def log_source_collection(logger: logging.Logger, source_count: int, unique_domains: int, phase: str):
    """
    Log source collection with structured information.
    
    Args:
        logger: Logger instance
        source_count: Number of sources collected
        unique_domains: Number of unique domains
        phase: Current phase
    """
    logger.info(
        f"Collected {source_count} sources from {unique_domains} unique domains",
        extra={'phase': phase, 'sources': source_count, 'domains': unique_domains}
    )


def log_data_quality_issue(logger: logging.Logger, issue: str, phase: str, severity: str = "warning"):
    """
    Log data quality issues.
    
    Args:
        logger: Logger instance
        issue: Description of the data quality issue
        phase: Current phase
        severity: Severity level (warning or error)
    """
    if severity == "error":
        logger.error(
            f"Data quality issue: {issue}",
            extra={'phase': phase, 'issue_type': 'data_quality'}
        )
    else:
        logger.warning(
            f"Data quality issue: {issue}",
            extra={'phase': phase, 'issue_type': 'data_quality'}
        )


def log_fallback_activation(logger: logging.Logger, primary: str, fallback: str, reason: str):
    """
    Log fallback mechanism activation.
    
    Args:
        logger: Logger instance
        primary: Primary mechanism that failed
        fallback: Fallback mechanism being used
        reason: Reason for fallback
    """
    logger.warning(
        f"Fallback activated: {primary} -> {fallback} (reason: {reason})",
        extra={'primary': primary, 'fallback': fallback, 'fallback_reason': reason}
    )


def log_unrecoverable_failure(logger: logging.Logger, operation: str, error: Exception, phase: str):
    """
    Log unrecoverable failures.
    
    Args:
        logger: Logger instance
        operation: Operation that failed
        error: Exception that occurred
        phase: Current phase
    """
    logger.error(
        f"Unrecoverable failure in {operation}: {error}",
        extra={'phase': phase, 'operation': operation, 'error_type': type(error).__name__},
        exc_info=True
    )
