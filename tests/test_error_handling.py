"""
Unit tests for error handling utilities.

Tests exponential backoff logic, graceful degradation, and state recovery.
"""

import pytest
import time
import json
from pathlib import Path
from unittest.mock import Mock, patch
from utils.error_handling import (
    exponential_backoff_retry,
    graceful_degradation,
    StateCheckpoint,
    StateRecoveryError,
    validate_partial_data,
    handle_api_error,
    RetryableError,
    NonRetryableError
)


class TestExponentialBackoff:
    """Test exponential backoff retry logic."""
    
    def test_successful_first_attempt(self):
        """Test that successful operations don't retry."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, initial_backoff=0.1)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        
        assert result == "success"
        assert call_count == 1
    
    def test_retry_on_failure(self):
        """Test that failed operations are retried."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, initial_backoff=0.1, jitter=False)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = failing_function()
        
        assert result == "success"
        assert call_count == 3
    
    def test_max_retries_exceeded(self):
        """Test that max retries limit is respected."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, initial_backoff=0.1)
        def always_failing_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Permanent failure")
        
        with pytest.raises(ValueError, match="Permanent failure"):
            always_failing_function()
        
        assert call_count == 3
    
    def test_non_retryable_error(self):
        """Test that non-retryable errors are not retried."""
        call_count = 0
        
        @exponential_backoff_retry(max_retries=3, initial_backoff=0.1)
        def non_retryable_function():
            nonlocal call_count
            call_count += 1
            raise NonRetryableError("Should not retry")
        
        with pytest.raises(NonRetryableError):
            non_retryable_function()
        
        assert call_count == 1
    
    def test_backoff_timing(self):
        """Test that backoff time increases exponentially."""
        call_times = []
        
        @exponential_backoff_retry(max_retries=3, initial_backoff=0.1, backoff_factor=2.0, jitter=False)
        def timed_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Retry")
            return "success"
        
        result = timed_function()
        
        assert result == "success"
        assert len(call_times) == 3
        
        # Check that delays are approximately correct (with some tolerance)
        delay1 = call_times[1] - call_times[0]
        delay2 = call_times[2] - call_times[1]
        
        assert 0.08 < delay1 < 0.15  # ~0.1s
        assert 0.18 < delay2 < 0.25  # ~0.2s


class TestGracefulDegradation:
    """Test graceful degradation with partial data."""
    
    def test_successful_operation(self):
        """Test that successful operations return normally."""
        @graceful_degradation(default_value="default")
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_failed_operation_returns_default(self):
        """Test that failed operations return default value."""
        @graceful_degradation(default_value="default")
        def failing_function():
            raise ValueError("Operation failed")
        
        result = failing_function()
        assert result == "default"
    
    def test_default_none(self):
        """Test graceful degradation with None as default."""
        @graceful_degradation(default_value=None)
        def failing_function():
            raise ValueError("Operation failed")
        
        result = failing_function()
        assert result is None
    
    def test_default_list(self):
        """Test graceful degradation with list as default."""
        @graceful_degradation(default_value=[])
        def failing_function():
            raise ValueError("Operation failed")
        
        result = failing_function()
        assert result == []


class TestStateCheckpoint:
    """Test state checkpoint functionality."""
    
    @pytest.fixture
    def checkpoint_manager(self, tmp_path):
        """Create a checkpoint manager with temporary directory."""
        return StateCheckpoint(checkpoint_dir=str(tmp_path / "checkpoints"))
    
    def test_save_and_load_json_checkpoint(self, checkpoint_manager):
        """Test saving and loading JSON checkpoints."""
        state = {
            "topic": "test topic",
            "iteration": 1,
            "sources": ["source1", "source2"]
        }
        
        # Save checkpoint
        checkpoint_path = checkpoint_manager.save_checkpoint(
            state,
            checkpoint_id="test_checkpoint",
            format="json"
        )
        
        assert checkpoint_path.exists()
        
        # Load checkpoint
        loaded_state = checkpoint_manager.load_checkpoint(
            checkpoint_id="test_checkpoint",
            format="json"
        )
        
        assert loaded_state == state
    
    def test_save_and_load_pickle_checkpoint(self, checkpoint_manager):
        """Test saving and loading pickle checkpoints."""
        state = {
            "topic": "test topic",
            "iteration": 1,
            "sources": ["source1", "source2"]
        }
        
        # Save checkpoint
        checkpoint_path = checkpoint_manager.save_checkpoint(
            state,
            checkpoint_id="test_checkpoint",
            format="pickle"
        )
        
        assert checkpoint_path.exists()
        
        # Load checkpoint
        loaded_state = checkpoint_manager.load_checkpoint(
            checkpoint_id="test_checkpoint",
            format="pickle"
        )
        
        assert loaded_state == state
    
    def test_list_checkpoints(self, checkpoint_manager):
        """Test listing available checkpoints."""
        # Save multiple checkpoints
        checkpoint_manager.save_checkpoint({"data": 1}, "checkpoint1", format="json")
        checkpoint_manager.save_checkpoint({"data": 2}, "checkpoint2", format="json")
        checkpoint_manager.save_checkpoint({"data": 3}, "checkpoint3", format="pickle")
        
        # List checkpoints
        checkpoints = checkpoint_manager.list_checkpoints()
        
        assert len(checkpoints) == 3
        assert "checkpoint1" in checkpoints
        assert "checkpoint2" in checkpoints
        assert "checkpoint3" in checkpoints
    
    def test_delete_checkpoint(self, checkpoint_manager):
        """Test deleting checkpoints."""
        # Save checkpoint
        checkpoint_manager.save_checkpoint({"data": 1}, "test_checkpoint", format="json")
        
        # Verify it exists
        checkpoints = checkpoint_manager.list_checkpoints()
        assert "test_checkpoint" in checkpoints
        
        # Delete checkpoint
        deleted = checkpoint_manager.delete_checkpoint("test_checkpoint")
        assert deleted is True
        
        # Verify it's gone
        checkpoints = checkpoint_manager.list_checkpoints()
        assert "test_checkpoint" not in checkpoints
    
    def test_delete_nonexistent_checkpoint(self, checkpoint_manager):
        """Test deleting a checkpoint that doesn't exist."""
        deleted = checkpoint_manager.delete_checkpoint("nonexistent")
        assert deleted is False
    
    def test_load_nonexistent_checkpoint(self, checkpoint_manager):
        """Test loading a checkpoint that doesn't exist."""
        with pytest.raises(StateRecoveryError):
            checkpoint_manager.load_checkpoint("nonexistent", format="json")
    
    def test_invalid_format(self, checkpoint_manager):
        """Test using an invalid format."""
        with pytest.raises(StateRecoveryError, match="Checkpoint save failed"):
            checkpoint_manager.save_checkpoint({"data": 1}, "test", format="invalid")


class TestValidatePartialData:
    """Test partial data validation."""
    
    def test_all_fields_present(self):
        """Test validation when all fields are present."""
        data = {
            "field1": "value1",
            "field2": "value2",
            "field3": "value3"
        }
        
        is_valid, completeness = validate_partial_data(
            data,
            required_fields=["field1", "field2", "field3"],
            min_completeness=0.5
        )
        
        assert is_valid is True
        assert completeness == 1.0
    
    def test_partial_fields_above_threshold(self):
        """Test validation when partial fields meet threshold."""
        data = {
            "field1": "value1",
            "field2": "value2",
            "field3": None
        }
        
        is_valid, completeness = validate_partial_data(
            data,
            required_fields=["field1", "field2", "field3"],
            min_completeness=0.5
        )
        
        assert is_valid is True
        assert completeness == 2/3
    
    def test_partial_fields_below_threshold(self):
        """Test validation when partial fields don't meet threshold."""
        data = {
            "field1": "value1",
            "field2": None,
            "field3": None
        }
        
        is_valid, completeness = validate_partial_data(
            data,
            required_fields=["field1", "field2", "field3"],
            min_completeness=0.5
        )
        
        assert is_valid is False
        assert completeness == 1/3
    
    def test_empty_values_not_counted(self):
        """Test that empty values are not counted as present."""
        data = {
            "field1": "value1",
            "field2": "",
            "field3": []
        }
        
        is_valid, completeness = validate_partial_data(
            data,
            required_fields=["field1", "field2", "field3"],
            min_completeness=0.5
        )
        
        assert is_valid is False
        assert completeness == 1/3
    
    def test_object_attributes(self):
        """Test validation with object attributes."""
        class TestObject:
            def __init__(self):
                self.field1 = "value1"
                self.field2 = "value2"
                self.field3 = None
        
        obj = TestObject()
        
        is_valid, completeness = validate_partial_data(
            obj,
            required_fields=["field1", "field2", "field3"],
            min_completeness=0.5
        )
        
        assert is_valid is True
        assert completeness == 2/3
    
    def test_no_required_fields(self):
        """Test validation with no required fields."""
        data = {"field1": "value1"}
        
        is_valid, completeness = validate_partial_data(
            data,
            required_fields=[],
            min_completeness=0.5
        )
        
        assert is_valid is True
        assert completeness == 1.0


class TestHandleAPIError:
    """Test API error handling."""
    
    def test_rate_limit_error(self):
        """Test handling of rate limit errors."""
        error = Exception("Rate limit exceeded (429)")
        
        is_retryable, backoff = handle_api_error(error)
        
        assert is_retryable is True
        assert backoff == 60.0
    
    def test_timeout_error(self):
        """Test handling of timeout errors."""
        error = Exception("Request timed out")
        
        is_retryable, backoff = handle_api_error(error)
        
        assert is_retryable is True
        assert backoff == 5.0
    
    def test_server_error(self):
        """Test handling of server errors (5xx)."""
        error = Exception("Server error (500)")
        
        is_retryable, backoff = handle_api_error(error)
        
        assert is_retryable is True
        assert backoff == 10.0
    
    def test_authentication_error(self):
        """Test handling of authentication errors."""
        error = Exception("Authentication failed (401)")
        
        is_retryable, backoff = handle_api_error(error)
        
        assert is_retryable is False
        assert backoff is None
    
    def test_client_error(self):
        """Test handling of client errors (4xx)."""
        error = Exception("Bad request (400)")
        
        is_retryable, backoff = handle_api_error(error)
        
        assert is_retryable is False
        assert backoff is None
    
    def test_unknown_error(self):
        """Test handling of unknown errors."""
        error = Exception("Something went wrong")
        
        is_retryable, backoff = handle_api_error(error)
        
        assert is_retryable is True
        assert backoff == 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
