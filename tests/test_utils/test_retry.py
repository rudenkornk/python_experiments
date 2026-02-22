# ruff: noqa: PLR2004
import time
from unittest.mock import Mock

import pytest

from python_experiments.utils import retry


def test_retry_success_on_first_try() -> None:
    """Test that retry decorator works when function succeeds on first try."""
    mock_func = Mock(return_value=42)
    decorated = retry(mock_func)

    result = decorated()

    assert result == 42
    assert mock_func.call_count == 1


def test_retry_success_on_second_try() -> None:
    """Test that retry decorator retries once and succeeds on second try."""
    error_msg = "error"
    mock_func = Mock(side_effect=[ValueError(error_msg), 42], __name__="mock_func")
    decorated = retry(mock_func, delay=0.01)

    result = decorated()

    assert result == 42
    assert mock_func.call_count == 2


def test_retry_exhausts_all_tries() -> None:
    """Test that retry decorator exhausts all tries and raises exception."""
    error_msg = "error"
    mock_func = Mock(side_effect=ValueError(error_msg), __name__="mock_func")
    decorated = retry(mock_func, delay=0.01, max_tries=3)

    with pytest.raises(ValueError, match=error_msg):
        decorated()

    assert mock_func.call_count == 3


def test_retry_with_delay() -> None:
    """Test that retry decorator waits between retries."""
    error_msg = "error"
    mock_func = Mock(side_effect=[ValueError(error_msg), 42], __name__="mock_func")
    delay_time = 0.1
    decorated = retry(mock_func, delay=delay_time)

    start = time.time()
    result = decorated()
    elapsed = time.time() - start

    assert result == 42
    assert elapsed >= delay_time
    assert mock_func.call_count == 2


def test_retry_as_decorator_with_args() -> None:
    """Test retry used as decorator with arguments."""
    error_msg = "always fails"

    @retry(delay=0.01, max_tries=3)
    def failing_func() -> int:
        raise ValueError(error_msg)

    with pytest.raises(ValueError, match=error_msg):
        failing_func()


def test_retry_as_decorator_without_parens() -> None:
    """Test retry used as decorator without parentheses."""
    call_count = 0
    error_msg = "first call fails"

    @retry
    def func_with_retry() -> int:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError(error_msg)
        return 42

    result = func_with_retry()

    assert result == 42
    assert call_count == 2


def test_retry_with_args_and_kwargs() -> None:
    """Test that retry decorator preserves function arguments."""
    error_msg = "error"
    expected_result = "result"
    mock_func = Mock(side_effect=[ValueError(error_msg), expected_result], __name__="mock_func")
    decorated = retry(mock_func, delay=0.01)

    result = decorated("arg1", "arg2", kwarg1="value1", kwarg2="value2")

    assert result == expected_result
    assert mock_func.call_count == 2
    mock_func.assert_called_with("arg1", "arg2", kwarg1="value1", kwarg2="value2")


def test_retry_preserves_function_name() -> None:
    """Test that retry decorator preserves the function name."""

    @retry(delay=0.01)
    def my_function() -> int:
        return 42

    assert my_function.__name__ == "my_function"


def test_retry_current_try_attribute() -> None:
    """Test that retry decorator sets current_try attribute."""
    tries = []
    error_msg = "not yet"

    @retry(delay=0.01, max_tries=3)
    def track_tries() -> int:
        tries.append(track_tries.current_try)  # type: ignore[attr-defined]
        if len(tries) < 3:
            raise ValueError(error_msg)
        return 42

    result = track_tries()

    assert result == 42
    assert tries == [0, 1, 2]


def test_retry_suppress_logger() -> None:
    """Test that retry decorator can suppress logging."""
    error_msg = "error"
    mock_func = Mock(side_effect=[ValueError(error_msg), 42])
    decorated = retry(mock_func, delay=0.01, suppress_logger=True)

    result = decorated()

    assert result == 42
    assert mock_func.call_count == 2


def test_retry_max_tries_validation() -> None:
    """Test that retry decorator validates max_tries parameter."""
    with pytest.raises(ValueError, match="max_tries must be greater than 0"):
        retry(max_tries=0)

    with pytest.raises(ValueError, match="max_tries must be greater than 0"):
        retry(max_tries=-1)


def test_retry_different_exception_types() -> None:
    """Test retry with different exception types."""
    first_error = "first error"
    second_error = "second error"
    success_msg = "success"

    @retry(delay=0.01, max_tries=3)
    def func_multiple_exceptions() -> str:
        if func_multiple_exceptions.current_try == 0:  # type: ignore[attr-defined]
            raise ValueError(first_error)
        if func_multiple_exceptions.current_try == 1:  # type: ignore[attr-defined]
            raise RuntimeError(second_error)
        return success_msg

    result = func_multiple_exceptions()
    assert result == success_msg


def test_retry_with_return_none() -> None:
    """Test retry decorator when function returns None."""
    call_count = 0
    error_msg = "error"

    @retry(delay=0.01, max_tries=2)
    def func_returns_none() -> None:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ValueError(error_msg)

    result = func_returns_none()

    assert result is None
    assert call_count == 2
