import pytest
import os
from unittest.mock import patch, MagicMock
from middlewares.DB_connector.connect import handle_db_connection


@pytest.fixture(scope="function")
def mock_load_dotenv():
    """Mocking load_dotenv to avoid actual environment variable loading."""
    with patch.dict(os.environ, {"MONGO_CONNECTION_STRING": "mock_connection_string"}):
        yield


@pytest.mark.asyncio
async def test_handle_db_connection_success(mock_load_dotenv):
    """Test case for successful database connection."""
    # Mocking MongoClient and its methods
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_client.__getitem__.return_value = mock_db
    mock_db.command.return_value = {
        "version": "4.4.5",
        "ok": 1,
        "$clusterTime": {"signature": {"keyId": 12345}},
        "operationTime": "2024-06-30",
    }

    with patch(
        "middlewares.DB_connector.connect.asyncio.to_thread", return_value=mock_client
    ):
        result = await handle_db_connection(connect=True)

    assert result == mock_db
    assert mock_client.__getitem__.called_once_with("spiders-db")
    assert mock_db.command.called_once_with("serverStatus")


@pytest.mark.asyncio
async def test_handle_db_connection_disabled(mock_load_dotenv, caplog):
    """Test case for database connection disabled."""
    with patch("builtins.print") as mock_print:
        result = await handle_db_connection(connect=False)

    assert result is None
    assert "Connection to database is disabled!" in mock_print.call_args[0][0]


@pytest.mark.asyncio
async def test_handle_db_connection_missing_connection_string(caplog):
    """Test case for missing MongoDB connection string."""
    with pytest.raises(ValueError, match="MongoDB connection string not found"):
        await handle_db_connection(connect=True)

    assert (
        "MongoDB connection string not found in environment variables." in caplog.text
    )


@pytest.mark.asyncio
async def test_handle_db_connection_exception(caplog):
    """Test case for unexpected exception during database connection."""
    with patch(
        "middlewares.DB_connector.connect.asyncio.to_thread",
        side_effect=Exception("Connection error"),
    ), pytest.raises(Exception, match="An unexpected error occurred: Connection error"):
        await handle_db_connection(connect=True)

    assert "An unexpected error occurred: Connection error" in caplog.text
    assert "Connection failed: Connection error" in caplog.text
