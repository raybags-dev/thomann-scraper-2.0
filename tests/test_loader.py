import pytest
from unittest.mock import patch
from datetime import datetime
from utils.utilities.loader import LoadingEmulator, emulator


@pytest.fixture
def loading_emulator():
    return LoadingEmulator()


def test_emulate_loading_start_loading(loading_emulator):
    with patch("builtins.print") as mock_print, patch(
        "threading.Thread"
    ) as mock_thread:
        loading_emulator.emulate_loading(message="Start", start_loading=True)

        assert loading_emulator.start_time is not None
        assert not loading_emulator.stopped
        mock_thread.assert_called_once()
        mock_print.assert_called_with("\x1b[35mStart\x1b[39m")


def test_emulate_loading_stop_loading(loading_emulator):
    with patch("builtins.print") as mock_print, patch(
        "threading.Thread"
    ) as mock_thread:
        loading_emulator.emulate_loading(message="Start", start_loading=True)
        loading_emulator.emulate_loading(start_loading=False)

        assert loading_emulator.stopped
        assert loading_emulator.end_time is not None
        mock_print.assert_any_call("\x1b[32m.........\x1b[39m")


def test_update_progress(loading_emulator):
    with patch("builtins.print") as mock_print, patch(
        "time.sleep", return_value=None
    ) as mock_time_sleep:
        loading_emulator.start_time = datetime.now()
        loading_emulator.stopped = False

        def stop_loading_after_some_iterations(*args, **kwargs):
            loading_emulator.stopped = True

        mock_time_sleep.side_effect = stop_loading_after_some_iterations

        loading_emulator.update_progress()

        assert mock_print.call_count > 0
        mock_print.assert_any_call(
            f"\r> 100% - (start_time: {loading_emulator.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}+0000, end_time: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}+0000): ",
            end="",
        )


def test_print_completion_message(loading_emulator):
    with patch("builtins.print") as mock_print:
        loading_emulator.start_time = datetime.now()
        loading_emulator.end_time = datetime.now()

        loading_emulator.print_completion_message()

        mock_print.assert_called_once_with(
            f"\r> 100% - (start_timestamp: {loading_emulator.start_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}+0000, end_timestamp: {loading_emulator.end_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}+0000): \x1b[32m> Current process completed.\x1b[39m"
        )


def test_emulator_start(loading_emulator):
    assert loading_emulator.start_time is None
    assert not loading_emulator.stopped
