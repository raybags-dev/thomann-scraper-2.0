import pytest
from unittest.mock import MagicMock
from spiders.base_url_spider import scrape_thomann_base_urls, is_valid_url


@pytest.fixture
def mock_page_content():
    return """
    <html>
        <body>
            <div class="thomann-page-content-wrapper">
                <div class="link-list__item"><a class="link-list__text" href="/product/1"></a></div>
                <div class="link-list__item"><a class="link-list__text" href="/product/2"></a></div>
            </div>
        </body>
    </html>
    """


@pytest.mark.asyncio
async def test_scrape_thomann_base_urls_success(mock_page_content, monkeypatch):
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_page.content.return_value = mock_page_content

    monkeypatch.setattr(
        "spiders.base_url_spider.async_playwright",
        MagicMock(
            return_value=MagicMock(
                chromium=MagicMock(launch=MagicMock(return_value=mock_browser))
            )
        ),
    )

    result = await scrape_thomann_base_urls(can_run=True)

    assert result is True


@pytest.mark.asyncio
async def test_scrape_thomann_base_urls_no_urls_found(monkeypatch):
    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_page.content.return_value = """
    <html>
        <body>
            <div class="thomann-page-content-wrapper">
                <!-- No link items -->
            </div>
        </body>
    </html>
    """

    monkeypatch.setattr(
        "spiders.base_url_spider.async_playwright",
        MagicMock(
            return_value=MagicMock(
                chromium=MagicMock(launch=MagicMock(return_value=mock_browser))
            )
        ),
    )

    result = await scrape_thomann_base_urls(can_run=True)

    assert result is False


@pytest.mark.asyncio
async def test_scrape_thomann_base_urls_exception(monkeypatch):
    monkeypatch.setattr(
        "spiders.base_url_spider.async_playwright",
        MagicMock(side_effect=Exception("Test exception")),
    )

    result = await scrape_thomann_base_urls(can_run=True)

    assert result is False
