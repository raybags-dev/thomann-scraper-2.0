import random
from middlewares.errors.error_handler import handle_exceptions
from middlewares.logger.logger import custom_logger, initialize_logging

initialize_logging()


@handle_exceptions
def randomize_timeout(min_timeout, max_timeout):
    increments = 5000
    possible_timeouts = list(range(min_timeout, max_timeout + increments, increments))
    return random.choice(possible_timeouts)


@handle_exceptions
def random_small_timeout(min_timeout, max_timeout):
    increments = 150
    possible_timeouts = list(range(min_timeout, max_timeout + increments, increments))
    return random.choice(possible_timeouts)


@handle_exceptions
async def click_consent_button(page):
    consent_btn_selector = ".consent-button:has-text('Alright')"

    try:
        consent_button = await page.wait_for_selector(
            consent_btn_selector, timeout=5000
        )
        if consent_button:
            await consent_button.click()
            custom_logger(message="cookies accepted", log_type="info")
            return True
        else:
            return False
    except Exception as e:
        err = f"Error occured in <click_consent_button>: {e}"
        custom_logger(message=err, log_type="warn")
        return False
