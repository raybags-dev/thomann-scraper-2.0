import os
import csv
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from utils.loader import emulator
from playwright.sync_api import sync_playwright
from concurrent.futures import ThreadPoolExecutor, as_completed
from middlewares.errors.error_handler import handle_exceptions
from middlewares.logger.logger import custom_logger, initialize_logging

initialize_logging()


@handle_exceptions
def is_valid_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])


@handle_exceptions
def scrape_thomann_base_urls(can_run=False):
    if not can_run:
        custom_logger("BaseURL collection disabled!", log_type="info")
        return False

    base_url = 'https://www.thomann.de/gb/index.html'
    base_urls_file = Path('base_urls/base_urls.txt')
    base_urls_file.parent.mkdir(parents=True, exist_ok=True)

    emulator(message="Starting URL scraping process...", is_in_progress=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            custom_logger(f"Navigating to {base_url}", log_type="info")
            page.goto(base_url, timeout=60000)
            page.wait_for_selector('.thomann-page-content-wrapper', state='visible', timeout=30000)

            soup = BeautifulSoup(page.content(), 'html.parser')
            link_items = soup.select('.link-list__item a.link-list__text')
            endpoints = set()

            for link in link_items:
                url = link.get('href', '')
                if is_valid_url(url):
                    endpoints.add(url)

            if endpoints:
                with base_urls_file.open('w', encoding='utf-8') as f:
                    for endpoint in sorted(endpoints):
                        f.write(f"{endpoint}\n")
                custom_logger("Base URLs successfully scraped and saved.", log_type="info")
                emulator(is_in_progress=False)
                return True
            else:
                custom_logger("No valid URLs found.", log_type="warn")
                emulator(is_in_progress=False)
                return False

        except Exception as e:
            custom_logger(f"Error occurred: {str(e)}", log_type="error")
            emulator(is_in_progress=False)
            return False

        finally:
            browser.close()
            emulator(is_in_progress=False)
