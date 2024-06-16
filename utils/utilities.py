
import random
from pathlib import Path
from middlewares.errors.error_handler import handle_exceptions


@handle_exceptions
def randomize_timeout(min_timeout, max_timeout):
    increments = 5000
    possible_timeouts = list(range(min_timeout, max_timeout + increments, increments))
    return random.choice(possible_timeouts)

@handle_exceptions
async def click_consent_button(page):
    consent_button_selector = 'button.spicy-consent-bar__action.spicy-consent-bar__action--as-text.consent-button'

    try:
        consent_button = await page.wait_for_selector(consent_button_selector, timeout=5000)
        if consent_button:
            await consent_button.click()
            return True
        else:
            return False
    except Exception as e:
        err_message = f"{e}"
        return False
