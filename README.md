# Thomann Scraper 2.0

## Overview
Thomann Scraper 2.0 is a Python-based web scraping application designed to extract product data from Thomann, a popular online music instrument store. It allows users to collect detailed information about products listed on Thomann's website, such as product titles, descriptions, prices, reviews, and more.


## Features

- **Web Scraping**: Automatically fetches product information from Thomann's website.
- **Data Storage**: Supports storing scraped data either locally or in a MongoDB database.
- **Concurrency**: Uses asyncio to process multiple product pages concurrently.
- **Error Handling**: Implements error handling for various exceptions during scraping and data processing.
- **Logging**: Includes logging to track the scraping process and any encountered issues.
- **Configuration**: Flexible configuration via a settings file (`config.ini`) for easy customization.

## Functionality

### 1. Collecting Base URLs

The application starts by collecting base URLs from a specified CSV file (`base_urls.csv`). These base URLs typically represent different product categories or sections on Thomann's website.

- **Implementation**:
    - Visist the target website and collects target base_urls.
    - Reads the `base_urls.csv` file to fetch base URLs.
    - Stores these URLs in memory or loads them into a data structure for further processing.

### 2. Collecting Individual Product Endpoints

Once the base URLs are collected, the scraper proceeds to gather individual product endpoints from each base URL. These endpoints point to specific product pages on Thomann's website.

- **Implementation**:
    - Iterates through each base URL.
    - Visits each base URL and extracts product endpoints (e.g., `/product12345.html`).
    - Stores these endpoints for subsequent scraping and data extraction.

### 3. Scraping, Parsing, Validating, and Storing Data

After collecting product endpoints, the scraper begins the core process of scraping, parsing, validating, and storing product data.

- **Scraping**:
    - Uses Playwright to automate browser interactions.
    - Downloads HTML content from each product page.
    - Extracts relevant product information (e.g., title, description, price, reviews) using XPath or CSS selectors.

- **Parsing**:
    - Cleans and formats scraped data to ensure consistency.
    - Converts data types and handles special characters.

- **Validating**:
    - Validates scraped data against predefined rules (e.g., data completeness, format validation).
    - Logs validation errors or discrepancies encountered during the process.

- **Storing Collected Data**:
    - Supports two modes:
        - **Local Storage**: Saves data as JSON files (`products_data.txt`) in a specified directory (`data/`).
        - **Database Storage**: Inserts data into a MongoDB database.
    - Logs successful data storage operations and any errors encountered.
    - Collected data object example:

   ```{
    "budges": [
    "3030-Day Money-Back Guarantee",
    "33-Year Thomann Warranty"
    ],
    "description_text": "Closed-back. Circumaural design. Dynamic. Diffuse-field equalised. Impedance: 80 Ohm. Sensitivity SPL (sound pressure level): 96 dB. Frequency response: 5 - 35,000 Hz. 3 m straight single-sided cable with 3.5 mm connector. Screw-on adapter to 6.3 mm stereo jack. Weight with cable: 346 g. Weight without cable: 284 g.",
    "description_title": "Studio Headphones",
    "disclaimer": "Including VAT; Excluding \\u00a310 shipping",
    "features": {
    "Adaptor": "Yes",
    "Available since": "October 2004",
    "Colour": "Black",
    "Design": "Over-Ear",
    "Frequency range": "5 Hz \\u2013 35000 Hz",
    "Impedance": "80 Ohms",
    "Max. SPL": "96 dB",
    "Replaceable Cable": "No",
    "Sales Unit": "1 piece(s)",
    "System": "Closed Back",
    "Type Of Connector": "Jack, mini-jack",
    "Weight": "284 g",
    "item_id": "174334"
    },
    "good_to_know": "",
    "prediction": ", expected between: Friday, 21.06. and Monday, 24.06.",
    "price": "\\u00a3119",
    "product_title": "beyerdynamic DT-770 Pro 80 Ohm",
    "product_url": "https://www.thomann.de/gb/beyerdynamic_dt770_pro80_ohm.htm",
    "ranking": {
    "rank_category": "are looking at this product",
    "rank_description": "Visitors",
    "rank_link": "https://www.thomann.de/gb/cat_rank.html?ar=174334&gk=ZUKOSK&ref=prp_ran",
    "rank_value": "249"
    },
    "review_count": "4564",
    "reviews_url": "https://www.thomann.de/gb/beyerdynamic_dt770_pro80_ohm_reviews.htm?page=1&order=latest&reviewlang%5B%5D=all",
    "shipping": "In stock"
    }
  ```

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
   ```bash
   - git clone https://github.com/raybags-dev/thomann-scraper-2.0.git
   - cd thomann-scraper-2.0
   - create your environment and activate it.
   - pip install -r requirements.txt
