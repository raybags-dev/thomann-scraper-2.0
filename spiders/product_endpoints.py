from pathlib import Path
from bs4 import BeautifulSoup
from utils.loader import emulator
from auth_creds.headers import Headers
import requests, time, random, csv, os, re
from utils.utilities import randomize_timeout
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from concurrent.futures import ThreadPoolExecutor, as_completed
from middlewares.errors.error_handler import handle_exceptions
from middlewares.logger.logger import custom_logger, initialize_logging


initialize_logging()

@handle_exceptions
def load_base_urls(file_path):
    base_url_constructs = []
    if not file_path.exists() or not file_path.is_file():
        custom_logger(f"The file {file_path} does not exist or is not a file.", log_type="error")
        return base_url_constructs

    with file_path.open(mode='r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                base_url_constructs.append(line)

    return base_url_constructs

@handle_exceptions
def parse_endpoints(page_content, endpoints_set):
    soup = BeautifulSoup(page_content, 'html.parser')
    article_links = soup.select('a.js-item')
    for link in article_links:
        url = link.get('href')
        if url:
            endpoints_set.add(urljoin('https://www.thomann.de/gb/', url))

@handle_exceptions
def extract_endpoint_name(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    return path_parts[-1] if path_parts else 'unknown'

@handle_exceptions
def save_endpoints_to_csv(endpoints, output_dir, file_name):
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_file_path = output_dir / f"{file_name}.csv"

    existing_endpoints = set()
    if csv_file_path.exists():
        with csv_file_path.open(mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            existing_endpoints = {row[0] for row in reader}

    new_endpoints = endpoints - existing_endpoints
    if not new_endpoints:
        custom_logger("No new endpoints to save.", log_type="info")
        return

    with csv_file_path.open(mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not existing_endpoints:  # Write header if file is new
            writer.writerow(['endpoint'])
        for endpoint in new_endpoints:
            writer.writerow([endpoint])

    custom_logger(f"New endpoints saved to {csv_file_path}", log_type="info")

@handle_exceptions
def wait_for_overlay_disappearance(page):
    emulator(message="Calling next page...", is_in_progress=True)

    overlay_selector = ('div.js-content-wrapper.fx-overlay-loading.fx-overlay-loading--vanilla.fx-overlay-loading'
                        '--bottom')
    image_selector = 'img.fx-overlay-loading__indicator'
    try:
        # Remove the image if it exists
        page.evaluate(f"""
            const img = document.querySelector('{image_selector}');
            if (img) {{
                img.remove();
            }}
        """)
        custom_logger("Overlay loading indicator removed.", log_type="info")

        # Wait for the overlay to disappear
        page.wait_for_selector(overlay_selector, state='hidden', timeout=10000)
        custom_logger("Overlay disappeared.", log_type="info")
        emulator(is_in_progress=False)

    except PlaywrightTimeoutError:
        custom_logger("Overlay did not disappear within the timeout.", log_type="warn")

@handle_exceptions
def click_button_with_retry(page, button_selector):
    try:
        button = page.query_selector(button_selector)
        if button:
            page.evaluate("button => button.scrollIntoViewIfNeeded()", button)
            page.wait_for_timeout(1000)  # Wait a bit to mimic human behavior

            try:
                button.click()
            except PlaywrightError as e:
                custom_logger(f"PlaywrightError: {e}", log_type="warn")
                return False

            # Wait for the overlay to appear and disappear
            wait_for_overlay_disappearance(page)

            time.sleep(2)  # Give time for new elements to load

            return True
        else:
            custom_logger("No more button found.", log_type="info")
            return False
    except PlaywrightError as e:
        custom_logger(f"PlaywrightError: {e}", log_type="warn")
        return False

@handle_exceptions
def download_category_endpoints(base_urls, output_dir, max_retries=3):
    with sync_playwright() as p:
        for base_url in base_urls:
            endpoint_name = extract_endpoint_name(base_url)
            endpoints = set()
            attempts = 0

            while attempts < max_retries:
                attempts += 1
                try:
                    custom_logger(f'> Extracting endpoints for {base_url} (Attempt {attempts})...', log_type="info")
                    emulator(is_in_progress=True)
                    browser = p.chromium.launch(headless=True, args=["--disable-web-security",
                                                                     "--disable-features=IsolateOrigins,"
                                                                     "site-per-process"])
                    page = browser.new_page()
                    # Capture console errors and log them
                    page.on("console", lambda msg: custom_logger(f"Console: {msg.text}", log_type="warn"))
                    # Log page load event
                    page.on("load", lambda page: custom_logger(f"Page loaded: {page.url}", log_type="info"))

                    # Increase timeout for page load
                    page.goto(base_url, timeout=randomize_timeout(60000, 80000))

                    # Look for and handle the consent button
                    consent_button_selector = ('button.spicy-consent-bar__action.spicy-consent-bar__action--as-text'
                                               '.consent-button')
                    try:
                        consent_button = page.query_selector(consent_button_selector)
                        if consent_button:
                            consent_button.click()
                            custom_logger("Consent banner dismissed.", log_type="info")
                            # Wait for the banner to be removed
                            page.wait_for_timeout(2000)
                    except PlaywrightError as e:
                        custom_logger(f"Error interacting with consent banner: {e}", log_type="warn")

                    try:
                        # Increase timeout for selector
                        page.wait_for_selector('div.js-content-wrapper div div.js-articles', state='visible',
                                               timeout=randomize_timeout(30000, 50000))
                    except PlaywrightTimeoutError:
                        custom_logger(f"TimeoutError: .js-content-wrapper not visible (Attempt {attempts}).",
                                      log_type="error")
                        continue

                    # Parse initial page load
                    parse_endpoints(page.content(), endpoints)
                    custom_logger(f"Initial endpoints collected: {len(endpoints)}", log_type="info")
                    emulator(is_in_progress=False)
                    save_endpoints_to_csv(endpoints, output_dir, endpoint_name)  # Save after initial collection

                    button_selector = 'button.fx-product-grid__button.js-button-more'
                    initial_element_count = len(
                        page.query_selector_all('div.js-content-wrapper div.js-articles a.js-item'))

                    while True:
                        success = click_button_with_retry(page, button_selector)
                        if not success:
                            break

                        current_element_count = len(
                            page.query_selector_all('div.js-content-wrapper div.js-articles a.js-item'))
                        if current_element_count > initial_element_count:
                            emulator(is_in_progress=True)
                            new_endpoints = set()
                            parse_endpoints(page.content(), new_endpoints)
                            new_endpoints -= endpoints  # Exclude already collected endpoints
                            if new_endpoints:
                                endpoints.update(new_endpoints)
                                save_endpoints_to_csv(endpoints, output_dir, endpoint_name)
                                custom_logger(f"Additional endpoints collected: {len(new_endpoints)}", log_type="info")
                                emulator(is_in_progress=False)
                            else:
                                custom_logger("No new endpoints found after button click.", log_type="info")
                                emulator(is_in_progress=False)

                                break
                            initial_element_count = current_element_count  # Update initial count
                        else:
                            custom_logger("No new elements added after button click.", log_type="info")
                            break

                except PlaywrightTimeoutError as e:
                    custom_logger(f"TimeoutError: {e} (Attempt {attempts})", log_type="error")
                    continue
                except Exception as e:
                    custom_logger(f"PlaywrightError: {e} (Attempt {attempts})", log_type="error")
                    continue
                finally:
                    if 'browser' in locals() and browser:
                        browser.close()
                        emulator(is_in_progress=False)

            # Final save to ensure all endpoints are written
            if endpoints:
                save_endpoints_to_csv(endpoints, output_dir, endpoint_name)
            else:
                custom_logger(f"No endpoints found for {base_url}", log_type="info")

@handle_exceptions
def collect_product_endpoints(can_run=False) -> bool:
    if not can_run:
        custom_logger("Product endpoint collection disabled!.", log_type="info")
        return False

    product_endpoints_dir = Path(__file__).resolve().parent.parent / 'product_endpoints'
    base_urls_file = product_endpoints_dir.parent / 'base_urls' / 'base_urls.txt'
    output_dir = product_endpoints_dir

    base_urls = load_base_urls(base_urls_file)
    if base_urls:
        download_category_endpoints(base_urls, output_dir)
        custom_logger("Endpoints extraction complete.")
        return True
    else:
        custom_logger("No valid base URLs to process.", log_type="info")
        return False
