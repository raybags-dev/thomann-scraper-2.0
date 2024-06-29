import asyncio
from utils.utilities.loader import emulator
from spiders.product import ProductProcessorApp
from spiders.base_url_spider import scrape_thomann_base_urls
from spiders.product_endpoints import collect_product_endpoints
from middlewares.DB_connector.connect import handle_db_connection


async def main():
    prod_data = ProductProcessorApp()
    try:
        await handle_db_connection(connect=False)

        base_urls = await scrape_thomann_base_urls(can_run=True)
        if base_urls:
            prod_urls = await collect_product_endpoints(can_run=True)
            if prod_urls:
                is_data_ready = await prod_data.get_prod_data(can_process=True)
                if is_data_ready:
                    print("All done!")

    except Exception as e:
        print(f"An error occurred during execution: {e}")
        emulator(is_in_progress=False)


if __name__ == "__main__":
    asyncio.run(main())
