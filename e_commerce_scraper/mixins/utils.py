import html

from selenium.webdriver.support.expected_conditions import visibility_of_all_elements_located, \
    visibility_of_element_located
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_element_to_be_clickable(driver, locator, timeout=3):
    try:
        clickable_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        driver.execute_script("arguments[0].click();", clickable_element)
    except Exception:
        print(f"Element not clickable with JS after {timeout} seconds.")
def get_text_by_javascript(driver, element):
    return driver.execute_script("return arguments[0].textContent;", element)


def wait_for_element_to_be_present(driver, locator, timeout=10):
    """
    Wait for a single element to be present in the DOM.

    :param driver: WebDriver instance
    :param locator: locator
    :param timeout: Maximum wait time in seconds (default is 10)
    :return: WebElement if found
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located(locator)
    )


def wait_for_all_elements_to_be_present(driver, locator, timeout=10):
    """
    Wait for all elements to be present in the DOM.

    :param driver: WebDriver instance
    :param locator: locator
    :param timeout: Maximum wait time in seconds (default is 10)
    :return: List of WebElements if found
    """
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located(locator)
    )
def wait_for_all_elements_to_be_visible(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(visibility_of_all_elements_located(locator))

def wait_for_element_to_be_visible(driver, locator, timeout=10):
    return WebDriverWait(driver, timeout).until(visibility_of_element_located(locator))