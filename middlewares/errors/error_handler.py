from functools import wraps
from middlewares.logger.logger import initialize_logging, custom_logger

# Initialize logging once
initialize_logging()


def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            custom_logger(f"Exception in {func.__name__}: {e}", log_type="error")
            return None
    return wrapper
