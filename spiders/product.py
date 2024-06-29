import re
import csv
import json
import asyncio
from pathlib import Path
from utils.utilities.loader import emulator
from auth_creds.headers import Headers
from utils.utilities.utilities import randomize_timeout, click_consent_button
from playwright.async_api import async_playwright, Error as PlaywrightError
from utils.parsers.parse_products import extract_product_data
from middlewares.errors.error_handler import handle_exceptions
from middlewares.logger.logger import custom_logger, initialize_logging

initialize_logging()

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

if not DATA_DIR.exists():
    DATA_DIR.mkdir()


class ProductProcessorApp:
    def __init__(self):
        self.data_dir = DATA_DIR
        self.unique_products = set()
        self.success_count = 0
        self.retries = []

    @handle_exceptions
    async def load_products_endpoints_csv_files(self):
        project_root = Path(__file__).resolve().parent.parent
        base_dir = project_root / "product_endpoints"

        if not base_dir.exists() or not base_dir.is_dir():
            custom_logger(
                f"The directory {base_dir} does not exist or is not a directory.",
                log_type="error",
            )
            return []

        csv_files = list(base_dir.glob("*.csv"))

        if not csv_files:
            custom_logger("No CSV files found in the directory.", log_type="info")
            return []

        products_url_constructs = set()

        for csv_file in csv_files:
            if csv_file.stat().st_size == 0:
                custom_logger(f"The file {csv_file.name} is empty.", log_type="warning")
                continue

            with csv_file.open(mode="r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                custom_logger(f"Processing file: {csv_file.name}", log_type="info")
                for row in reader:
                    url = row.get("endpoint")
                    if url:
                        products_url_constructs.add(url)

        return list(products_url_constructs)

        # ===================================================
        # ===================================================

    @handle_exceptions
    async def download_and_process_page(self, page, url):
        try:
            emulator(message="Downloading page...", is_in_progress=True)

            await page.goto(url, timeout=randomize_timeout(40000, 60000))

            # Look for consent button
            await click_consent_button(page)

            await page.wait_for_selector(".thomann-page-content-wrapper")
            content = await page.content()
            product_data = extract_product_data(content)
            if product_data:
                emulator(message="Page data downloaded...", is_in_progress=False)
                return product_data
            else:
                emulator(is_in_progress=False)
                return False
        except PlaywrightError as e:
            custom_logger(f"Error fetching {url}: {e}", log_type="error")
            return False
        except Exception as e:
            custom_logger(f"Exception processing {url}: {e}", log_type="error")
            return False

    @handle_exceptions
    async def process_product_endpoints(self, endpoints, concurrency=3):
        async with async_playwright() as p:
            products_headers_obj = Headers()
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                extra_http_headers=products_headers_obj.get_product_headers()
            )

            try:

                async def process_batch(batch_urls):
                    tasks = []
                    pages = []

                    for url in batch_urls:
                        page = await context.new_page()
                        pages.append(page)
                        tasks.append(self.download_and_process_page(page, url))

                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for page in pages:
                        await page.close()

                    for idx, result in enumerate(results):
                        url = batch_urls[idx]
                        if isinstance(result, dict):
                            self.save_product_data(result)
                            self.success_count += 1
                        else:
                            self.retries.append(url)

                # Process in batches
                batch_size = concurrency
                for i in range(0, len(endpoints), batch_size):
                    current_batch = endpoints[i : i + batch_size]
                    await process_batch(current_batch)

            finally:
                await context.close()
                await browser.close()

        custom_logger(f"Successfully processed {self.success_count} endpoints.")
        return self.success_count > 0

    # ===================================================

    @handle_exceptions
    def save_product_data(self, product_data):
        # Helper function to clean and strip data
        emulator(
            message=f"Processing data objects: {len(product_data)}...",
            is_in_progress=True,
        )

        def clean_data(data):
            if data is None:
                return ""

            if isinstance(data, list):
                return [re.sub(r"\s+", " ", item).strip() for item in data]
            elif isinstance(data, dict):
                return {k: re.sub(r"\s+", " ", v).strip() for k, v in data.items()}
            else:
                return re.sub(r"\s+", " ", data).strip()

        # Clean the data
        product_title = clean_data(product_data.get("product_title", "null"))
        review_count = clean_data(product_data.get("review_count", "null"))
        product_text_title = clean_data(product_data.get("description_title", "null"))
        main_description_text = clean_data(product_data.get("description_text", "null"))
        important_note_text = clean_data(product_data.get("product_note", "null"))
        product_url = clean_data(product_data.get("product_url", "null"))
        product_note = clean_data(product_data.get("badges_list", "null"))
        key_features = clean_data(product_data.get("key_features", "null"))
        price = clean_data(product_data.get("price", "null"))
        disclaimer = clean_data(product_data.get("disclaimer", "null"))
        shipping = clean_data(product_data.get("shipping", "null"))
        reviews_url = clean_data(product_data.get("reviews_url", "null"))
        prediction = clean_data(product_data.get("shipping_prediction", "null"))
        rank_details = clean_data(product_data.get("rank_details", {}))

        product_data_cleaned = {
            "product_title": product_title,
            "review_count": review_count,
            "description_title": product_text_title,
            "description_text": main_description_text,
            "good_to_know": important_note_text,
            "budges": product_note,
            "features": key_features,
            "price": price,
            "product_url": product_url,
            "disclaimer": disclaimer,
            "shipping": shipping,
            "prediction": prediction,
            "ranking": rank_details,
            "reviews_url": reviews_url,
        }

        # Convert to JSON string to ensure uniqueness
        product_data_json = json.dumps(product_data_cleaned, sort_keys=True)

        if product_data_json not in self.unique_products:
            self.unique_products.add(product_data_json)
            json_file_path = self.data_dir / "products_data.txt"

            with json_file_path.open(mode="a", encoding="utf-8") as f:
                f.write(product_data_json + "\n")
            emulator(is_in_progress=False)
            custom_logger(
                f"Saved product data count: {len(product_data_cleaned)} items",
                log_type="info",
            )
            # ===================================================
            # ===================================================

    @handle_exceptions
    async def get_prod_data(self, can_process=True):
        if not can_process:
            custom_logger("Product processing is disabled.", log_type="info")
            return False

        endpoints = await self.load_products_endpoints_csv_files()
        if not endpoints:
            custom_logger("No product endpoints to process.", log_type="info")
            return False

        await self.process_product_endpoints(endpoints)

        # ===================================================
        # ===================================================
