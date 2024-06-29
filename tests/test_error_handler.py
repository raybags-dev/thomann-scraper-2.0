import pytest
from middlewares.errors.error_handler import handle_exceptions


@handle_exceptions
def sample_function(divisor):
    return 10 / divisor


def test_handle_exceptions_decorator():
    result = sample_function(2)
    assert result == 5

    result = sample_function(0)
    assert result is None


def test_handle_exceptions_decorator_exception_handling(caplog):
    with caplog.at_level("ERROR"):
        result = sample_function(0)
        assert result is None
        # Check that an error message was logged
        assert "Exception in sample_function" in caplog.text
        assert "division by zero" in caplog.text  # Assuming division by zero exception
