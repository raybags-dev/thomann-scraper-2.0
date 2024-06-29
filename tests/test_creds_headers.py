import pytest
from auth_creds.headers import Headers
import random


def mock_random_choice(values):
    return values[0]


@pytest.fixture(autouse=True)
def mock_random_choice_patch(monkeypatch):
    monkeypatch.setattr(random, "choice", mock_random_choice)


@pytest.fixture
def headers_instance():
    additional_headers = {
        "custom-header1": "value1",
        "custom-header2": "value2",
        # Add more headers as defined in Headers class
    }
    return Headers(additional_headers=additional_headers)


def test_headers_initialization(headers_instance):
    assert isinstance(headers_instance, Headers)


def test_default_headers(headers_instance):
    default_headers = headers_instance.get_headers()
    assert "accept" in default_headers
    assert "accept-language" in default_headers
    assert "user-agent" in default_headers
    assert default_headers["sec-fetch-site"] == "none"


def test_default_product_headers(headers_instance):
    product_headers = headers_instance.get_product_headers()
    assert "accept" in product_headers
    assert "accept-language" in product_headers
    assert "user-agent" in product_headers
    assert product_headers["sec-fetch-site"] == "same-origin"


def test_user_agent_randomization(headers_instance):
    headers_instance.get_headers()
    user_agent_first_call = headers_instance.base_headers["user-agent"]

    headers_instance.get_headers()
    user_agent_second_call = headers_instance.base_headers["user-agent"]


def test_additional_headers():
    additional_headers = {
        "authorization": "Bearer token123",
        "x-custom-header": "value",
    }
    headers_instance = Headers(additional_headers)
    base_headers = headers_instance.get_headers()

    assert "authorization" in base_headers
    assert base_headers["authorization"] == "Bearer token123"
    assert "x-custom-header" in base_headers
    assert base_headers["x-custom-header"] == "value"
