import pytest
from unittest.mock import AsyncMock, patch

from utils.utilities.utilities import (
    randomize_timeout,
    random_small_timeout,
    click_consent_button,
)


def test_randomize_timeout():
    min_timeout = 10000
    max_timeout = 20000
    result = randomize_timeout(min_timeout, max_timeout)
    assert min_timeout <= result <= max_timeout
    assert (result - min_timeout) % 5000 == 0


def test_random_small_timeout():
    min_timeout = 1000
    max_timeout = 3000
    result = random_small_timeout(min_timeout, max_timeout)
    assert min_timeout <= result <= max_timeout
    assert (result - min_timeout) % 150 == 0


@pytest.mark.asyncio
async def test_click_consent_button():
    # Mocking the page object and its methods
    mock_page = AsyncMock()
    mock_button = AsyncMock()
    mock_page.wait_for_selector.return_value = mock_button

    # Mock the logger
    with patch("middlewares.logger.logger.custom_logger") as mock_logger:
        result = await click_consent_button(mock_page)
        mock_page.wait_for_selector.assert_called_once_with(
            ".consent-button:has-text('Alright')", timeout=5000
        )
        mock_button.click.assert_called_once()
        mock_logger.assert_called_with(message="cookies accepted", log_type="info")
        assert result is True


@pytest.mark.asyncio
async def test_click_consent_button_no_button():
    # Mocking the page object and its methods
    mock_page = AsyncMock()
    mock_page.wait_for_selector.return_value = None

    # Mock the logger
    with patch("middlewares.logger.logger.custom_logger") as mock_logger:
        result = await click_consent_button(mock_page)
        mock_page.wait_for_selector.assert_called_once_with(
            ".consent-button:has-text('Alright')", timeout=5000
        )
        mock_logger.assert_not_called()
        assert result is False


@pytest.mark.asyncio
async def test_click_consent_button_exception():
    # Mocking the page object and its methods
    mock_page = AsyncMock()
    mock_page.wait_for_selector.side_effect = Exception("Test exception")

    # Mock the logger
    with patch("middlewares.logger.logger.custom_logger") as mock_logger:
        result = await click_consent_button(mock_page)
        mock_page.wait_for_selector.assert_called_once_with(
            ".consent-button:has-text('Alright')", timeout=5000
        )
        mock_logger.assert_called_with(
            message="Error occured in <click_consent_button>: Test exception",
            log_type="warn",
        )
        assert result is False
