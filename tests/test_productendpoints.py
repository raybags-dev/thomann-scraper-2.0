import pytest
import tempfile
from pathlib import Path

from spiders.product_endpoints import (
    load_base_urls,
    is_valid_url,
    parse_endpoints,
    extract_endpoint_name,
)


@pytest.fixture
def mock_temporary_directory():
    temp_dir = tempfile.TemporaryDirectory()
    yield temp_dir.name
    temp_dir.cleanup()


@pytest.fixture
def mock_page_content():
    return "<html><body><a class='js-item' href='/product/1'></a><a class='js-item' href='/product/2'></a></body></html>"


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("https://example.com/product1", True),
        ("invalid-url", False),
    ],
)
def test_is_valid_url(test_input, expected):
    assert is_valid_url(test_input) == expected


def test_load_base_urls(mock_temporary_directory):
    base_urls_file = tempfile.NamedTemporaryFile(
        dir=mock_temporary_directory, delete=False
    )
    base_urls_file.write(
        b"https://www.thomann.de/gb/blowouts.html\n"
        b"https://www.thomann.de/gb/hotdeals.html\n"
        b"https://www.thomann.de/gb/prodnews.html\n"
        b"https://www.thomann.de/gb/topseller.html\n"
    )
    base_urls_file.close()

    base_urls = load_base_urls(Path(base_urls_file.name))
    assert len(base_urls) == 4
    assert base_urls == [
        "https://www.thomann.de/gb/blowouts.html",
        "https://www.thomann.de/gb/hotdeals.html",
        "https://www.thomann.de/gb/prodnews.html",
        "https://www.thomann.de/gb/topseller.html",
    ]


def test_parse_endpoints(mock_page_content):
    endpoints_set = set()
    parse_endpoints(mock_page_content, endpoints_set)


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://www.thomann.de/gb/product/1", "1"),
        ("https://www.thomann.de/gb/product/2", "2"),
        ("https://www.thomann.de/gb/", "gb"),
    ],
)
def test_extract_endpoint_name(url, expected):
    assert extract_endpoint_name(url) == expected
