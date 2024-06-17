import asyncio
from utils.loader import emulator
from spiders.product import ProductProcessorApp
from spiders.base_url_spider import scrape_thomann_base_urls
from spiders.product_endpoints import collect_product_endpoints
from middlewares.DB_connector.connect import handle_db_connection


async def main():
    process_product_data = ProductProcessorApp()
    try:
        await handle_db_connection(connect=False)
        await scrape_thomann_base_urls(can_run=True)
        await collect_product_endpoints(can_run=False)
        await process_product_data.products_main_worker(enable_processing=False)
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        emulator(is_in_progress=False)


if __name__ == "__main__":
    asyncio.run(main())
