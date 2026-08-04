"""SEL-LOGIN-xx — browser-driven tests for the /login page.

See tests/selenium/TEST_PLAN.md for the full test case list with steps.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def test_sel_login_01_valid_credentials_redirect_to_main_page(driver, live_server):
    driver.get(f"{live_server}/login")

    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("admin")
    driver.find_element(By.CSS_SELECTOR, "#loginForm button[type=submit]").click()

    WebDriverWait(driver, 5).until(EC.url_to_be(f"{live_server}/"))
    assert driver.current_url == f"{live_server}/"


def test_sel_login_02_invalid_credentials_show_inline_error(driver, live_server):
    driver.get(f"{live_server}/login")

    driver.find_element(By.ID, "username").send_keys("admin")
    driver.find_element(By.ID, "password").send_keys("wrong")
    driver.find_element(By.CSS_SELECTOR, "#loginForm button[type=submit]").click()

    error_box = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "errorBox"))
    )
    assert error_box.text
    assert driver.current_url == f"{live_server}/login"


def test_sel_login_03_main_page_redirects_to_login_without_session(driver, live_server):
    driver.get(f"{live_server}/")

    WebDriverWait(driver, 5).until(EC.url_to_be(f"{live_server}/login"))


def test_sel_login_04_theme_toggle_persists_across_reload(driver, live_server):
    driver.get(f"{live_server}/login")

    initial_class = driver.find_element(By.TAG_NAME, "body").get_attribute("class")

    driver.find_element(By.CSS_SELECTOR, "button.theme-toggle").click()

    WebDriverWait(driver, 5).until(
        lambda d: (
            d.find_element(By.TAG_NAME, "body").get_attribute("class") != initial_class
        )
    )
    toggled_class = driver.find_element(By.TAG_NAME, "body").get_attribute("class")

    driver.refresh()

    assert (
        driver.find_element(By.TAG_NAME, "body").get_attribute("class") == toggled_class
    )
