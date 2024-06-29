from bs4 import BeautifulSoup
from middlewares.errors.error_handler import handle_exceptions
from middlewares.logger.logger import custom_logger, initialize_logging

initialize_logging()


@handle_exceptions
def extract_product_data(page_content):
    try:
        soup = BeautifulSoup(page_content, "html.parser")
        main_container = soup.select_one(
            ".product-main-content.fx-content-product-grid__col"
        )
        if not main_container:
            raise ValueError("Main container not found")
            # ===================================================
            # ===================================================
        # Select the grid container within the main container
        fx_grid = main_container.select_one(".fx-grid--prod")
        if not fx_grid:
            raise ValueError("Grid container not found")

        left_container = fx_grid.select_one(".fx-grid__col.fx-col--lg-8")
        right_container = fx_grid.select_one(".fx-grid__col.fx-col--lg-4")
        # ===================================================
        # ===================================================
        product_data = {}

        if left_container:
            product_title_element = left_container.select_one(
                ".product-title h1.product-title__title"
            )
            product_title = (
                product_title_element.text.strip() if product_title_element else None
            )
            # ===================================================
            # ===================================================
            review_count_anchor = left_container.select_one(
                "a .fx-rating-stars .product-title__rating-description"
            )
            review_count = (
                review_count_anchor.text.strip() if review_count_anchor else None
            )
            # ===================================================
            # ===================================================
            product_description_element = left_container.select_one(
                '.product-text[itemprop="description"]'
            )
            if product_description_element:
                product_text_title_ele = product_description_element.select_one(
                    ".text-original h2.fx-headline"
                )
                product_text_title = (
                    product_text_title_ele.text.strip()
                    if product_text_title_ele
                    else None
                )
                # ===================================================
                # ===================================================
                product_description_list = product_description_element.select_one(
                    "ul.product-text__list"
                )
                main_description_text = ""
                if product_description_list:
                    list_items = product_description_list.find_all("li")
                    for li in list_items:
                        span = li.find("span")
                        if span:
                            main_description_text += span.text.strip() + ". "
                # ===================================================
                # ===================================================
                important_note = product_description_element.select_one(
                    "p.fx-text--plus"
                )
                important_note_text = (
                    important_note.text.strip() if important_note else None
                )
                # ===================================================
                # ===================================================
                # Extract badges
                badges_list = []
                badges_container = product_description_element.select_one("div.badges")
                if badges_container:
                    for badge_item in badges_container.select(".badges__item a"):
                        badge_text = badge_item.get_text(strip=True)
                        badges_list.append(badge_text)
                # ===================================================
                # ===================================================
                # features and extra text
                key_features = {}
                key_features_container = product_description_element.select_one(
                    "div.keyfeatures"
                )
                if key_features_container:
                    for feature in key_features_container.select(".keyfeature"):
                        label_element = feature.select_one(".keyfeature__label")
                        value_element = feature.select_one(".fx-text--bold")
                        if label_element and value_element:
                            label = label_element.get_text(strip=True)
                            value = value_element.get_text(strip=True)
                            key_features[label] = value

                    # Remove "Show more"
                    if "Show more" in key_features:
                        del key_features["Show more"]

                    # Rename "Item number" to "item_id"
                    if "Item number" in key_features:
                        key_features["item_id"] = key_features.pop("Item number")
                # ===================================================
                # ===================================================
                # Combine all extracted data into a dictionary
                product_data.update(
                    {
                        "product_title": product_title,
                        "review_count": review_count,
                        "description_title": product_text_title,
                        "description_text": main_description_text,
                        "product_note": important_note_text,
                        "badges_list": badges_list,
                        "key_features": key_features,
                    }
                )
        # ===================================================
        # ===================================================
        if right_container:
            product_price_element = right_container.select_one(
                "div.fx-position-sticky .product-price-box .price-and-availability"
            )

            if product_price_element:
                price_value_element = product_price_element.select_one(
                    ".price-wrapper .price"
                )
                if price_value_element:
                    price_value = price_value_element.text.strip()
                    # custom_logger(f"price_value available {bool(price_value)}", "warn")
                    # print(price_value)

                # ===================================================
                # ===================================================
                url_element = product_price_element.select_one(".price-wrapper")
                if url_element:
                    url_meat = url_element.select_one('meta[itemprop="url"]')
                    url = url_meat.get("content") if url_meat else None

                    review_url = url.replace(
                        ".htm", "_reviews.htm?page=1&order=latest&reviewlang%5B%5D=all"
                    )

                # ===================================================
                # ===================================================
                disclaimer_container = product_price_element.select_one(".meta")
                if disclaimer_container:
                    disclaimer_meat = disclaimer_container.select_one(
                        ".meta__disclaimer"
                    )
                    disclaimer = (
                        disclaimer_meat.text.strip() if disclaimer_meat else None
                    )

                # ===================================================
                # ===================================================
                ship_container = product_price_element.select_one(
                    ".price-and-availability__tooltip-wrapper div["
                    'aria-label="tooltip"]'
                )
                if ship_container:
                    ship_ele = ship_container.select_one(
                        "span span span.fx-availability"
                    )
                    shipping = ship_ele.text.strip() if ship_ele else None

                # ===================================================
                # ===================================================
                ship_prediction = product_price_element.select_one(
                    ".shipping-prediction"
                )
                if ship_prediction:
                    pred_text = ""
                    predic_text = (
                        ship_prediction.select_one("a").text.strip()
                        if ship_prediction.select_one("a")
                        else ""
                    )
                    if predic_text:
                        pred_text += predic_text

                    date_elements = (
                        ship_prediction.select_one("strong").find_all("span")
                        if ship_prediction.select_one("strong")
                        else []
                    )
                    if date_elements:
                        dates = [span.text.strip() for span in date_elements]
                        if len(dates) == 2:
                            pred_text += (
                                f", expected between: {dates[0]} and {dates[1]}"
                            )
                else:
                    pred_text = None

                product_data["shipping_prediction"] = pred_text
            # ===================================================
            # ===================================================
            ranking_container = right_container.select_one("div.fx-position-sticky")
            if ranking_container:
                ranking_obj = {}
                ranking_container.select_one(
                    ".product-rank-and-visitors a.meta-box--link"
                )

                rank_value = (
                    ranking_container.select_one(".meta-box__value").text.strip()
                    if ranking_container
                    else None
                )
                rank_descript = (
                    (
                        ranking_container.select_one(
                            ".meta-box__texts .meta-box__description"
                        ).text.strip()
                    )
                    if ranking_container
                    else None
                )
                rank_sub_category = (
                    (
                        ranking_container.select_one(
                            ".meta-box__texts .meta-box__subtext"
                        ).text.strip()
                    )
                    if ranking_container
                    else None
                )

                rank_url = (
                    (
                        ranking_container.select_one(
                            ".product-rank-and-visitors a.meta-box--link"
                        ).get("href")
                    )
                    if ranking_container
                    else None
                )

                ranking_obj["rank_value"] = rank_value
                ranking_obj["rank_description"] = rank_descript
                ranking_obj["rank_category"] = rank_sub_category
                ranking_obj["rank_link"] = rank_url

                product_data.update(
                    {
                        "price": price_value,
                        "product_url": url,
                        "disclaimer": disclaimer,
                        "shipping": shipping,
                        "shipping_prediction": pred_text,
                        "rank_details": ranking_obj,
                        "reviews_url": review_url,
                    }
                )

        return product_data

    except Exception as e:
        custom_logger(f"Error parsing page content: {e}", log_type="error")
        return None
