import os
import asyncio
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus
from utils.utilities.loader import emulator
from middlewares.errors.error_handler import handle_exceptions
from middlewares.logger.logger import custom_logger, initialize_logging


initialize_logging()


@handle_exceptions
async def handle_db_connection(connect=False):
    if not connect:
        print("Connection to database is disabled!")
        return None

    load_dotenv()
    mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")

    if not mongo_connection_string:
        raise ValueError(
            "MongoDB connection string not found in environment variables."
        )

    emulator(message="Connecting to database...", is_in_progress=True)

    # Extract username and password from the connection string and escape them
    start = mongo_connection_string.find("//") + 2
    end = mongo_connection_string.find("@")
    credentials = mongo_connection_string[start:end]
    username, password = credentials.split(":")
    escaped_username = quote_plus(username)
    escaped_password = quote_plus(password)

    connection_string = mongo_connection_string.replace(
        credentials, f"{escaped_username}:{escaped_password}"
    )

    try:
        # Connect with TLS and allow invalid certificates
        client = await asyncio.to_thread(
            MongoClient, connection_string, tls=True, tlsAllowInvalidCertificates=True
        )
        db = client["spiders-db"]

        if db is not None:
            server_info = await asyncio.to_thread(db.command, "serverStatus")
            emulator(is_in_progress=False)
            custom_logger("> Database connection established", log_type="info")
            custom_logger("> MongoDB Server Info:\n", log_type="info")
            custom_logger(f"- Version: {server_info['version']}", log_type="info")
            custom_logger(f"- Status: {server_info.get('ok', 'N/A')}", log_type="info")
            custom_logger(
                f"- keyId: {server_info['$clusterTime']['signature']['keyId']}",
                log_type="info",
            )
            custom_logger(f"\n- Timestamp: {server_info.get('operationTime', 'N/A')}")

        return db

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        emulator(message=f"Connection failed: {e}", is_in_progress=False)
        raise
