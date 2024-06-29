import logging
import pytest
import shutil
from pathlib import Path
from middlewares.logger.logger import initialize_logging, custom_logger

root_dir = Path(__file__).resolve().parent
LOG_FOLDER = root_dir / "test_logs"
LOG_FILENAMES = {"info": "info.log", "error": "error.log", "warn": "warn.log"}


@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    initialize_logging()


@pytest.fixture
def clear_log_files():
    log_folder = Path(__file__).resolve().parent / "test_logs"
    if not log_folder.exists():
        log_folder.mkdir(parents=True, exist_ok=True)
    for filename in LOG_FILENAMES.values():
        with open(log_folder / filename, "w"):
            pass

    yield

    # Clean up after test run
    if log_folder.exists():
        shutil.rmtree(log_folder)


@pytest.mark.parametrize("log_type", ["info", "error", "warn"])
def test_custom_logger(caplog, log_type, clear_log_files):
    message = f"Testing {log_type} logging"

    with caplog.at_level(logging.DEBUG):
        custom_logger(message, log_type=log_type)

    # Check log file content
    log_file_path = LOG_FOLDER / LOG_FILENAMES[log_type]
    assert log_file_path.exists(), f"{log_file_path} does not exist"
