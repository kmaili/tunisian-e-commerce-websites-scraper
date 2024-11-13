from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_element_to_be_clickable(driver, element, timeout=10):

    try:
        clickable_element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(element)
        )
        return clickable_element
    except TimeoutError:
        print(f"Element not clickable after {timeout} seconds.")
        return None
def get_text_by_javascript(driver, element):
    return driver.execute_script("return arguments[0].textContent;", element)