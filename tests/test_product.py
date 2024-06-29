import asyncio
from unittest.mock import MagicMock, patch
import pytest
from spiders.product import ProductProcessorApp


@pytest.fixture
def mock_data_dir(tmp_path):
    return tmp_path / "data"


@pytest.fixture
def mock_product_processor_app(mock_data_dir):
    app = ProductProcessorApp()
    app.data_dir = mock_data_dir
    return app


@pytest.fixture
def mock_endpoints():
    return ["https://example.com/product1", "https://example.com/product2"]


@pytest.fixture
def mock_page():
    return MagicMock()


@pytest.mark.asyncio
async def test_load_products_endpoints_csv_files(
    mock_product_processor_app, mock_data_dir, mock_endpoints
):
    # Create a mock CSV file
    csv_content = (
        "endpoint\nhttps://example.com/product1\nhttps://example.com/product2\n"
    )
    csv_path = mock_data_dir / "test.csv"
    csv_path.write_text(csv_content)

    with patch("spiders.product.custom_logger") as mock_logger:
        endpoints = await mock_product_processor_app.load_products_endpoints_csv_files()

        assert len(endpoints) == 2
        assert (
            mock_logger.call_count == 2
        )  # Check how many times custom_logger was called


@pytest.mark.asyncio
async def test_download_and_process_page_success(
    mock_product_processor_app, mock_page, mock_endpoints
):
    mock_page.goto.return_value = asyncio.Future()
    mock_page.goto.return_value.set_result(None)  # Simulate successful navigation

    with patch("spiders.product.custom_logger") as mock_logger:
        product_data = await mock_product_processor_app.download_and_process_page(
            mock_page, "https://example.com/product1"
        )

        assert product_data
        assert (
            mock_logger.call_count >= 2
        )  # Check how many times custom_logger was called


@pytest.mark.asyncio
async def test_download_and_process_page_error(
    mock_product_processor_app, mock_page, mock_endpoints
):
    mock_page.goto.side_effect = Exception("Page navigation failed")

    with patch("spiders.product.custom_logger") as mock_logger:
        product_data = await mock_product_processor_app.download_and_process_page(
            mock_page, "https://example.com/product1"
        )

        assert not product_data
        assert (
            mock_logger.call_count >= 2
        )  # Check how many times custom_logger was called


@pytest.mark.asyncio
async def test_process_product_endpoints(mock_product_processor_app, mock_endpoints):
    with patch("spiders.product.async_playwright") as mock_playwright:
        mock_browser = MagicMock()
        mock_context = MagicMock()
        mock_page = MagicMock()
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value.chromium.launch.return_value = mock_browser
        mock_playwright.return_value.chromium.launch.return_value.new_context.return_value = mock_context

        await mock_product_processor_app.process_product_endpoints(
            mock_endpoints, concurrency=3
        )

        assert mock_browser.close.called
        assert mock_context.close.called


@pytest.mark.asyncio
async def test_get_prod_data(mock_product_processor_app):
    with patch.object(
        ProductProcessorApp,
        "load_products_endpoints_csv_files",
        return_value=["https://example.com/product1", "https://example.com/product2"],
    ) as mock_load_endpoints:
        with patch.object(
            ProductProcessorApp, "process_product_endpoints", return_value=True
        ) as mock_process_endpoints:
            await mock_product_processor_app.get_prod_data()

            assert mock_load_endpoints.called
            assert mock_process_endpoints.called
