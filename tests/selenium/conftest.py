"""Fixtures specific to tests/selenium.

Unlike tests/functional (which calls the API directly with `requests`),
these tests drive a real, headless browser against the live server and
exercise the actual login/main-page JavaScript — real form fills, real
button clicks, real DOM updates driven by the app's own fetch calls. See
tests/conftest.py for the shared `live_server` fixture that boots the app.

Requires a Chrome/Chromium install on PATH. Selenium 4's built-in Selenium
Manager downloads a matching chromedriver automatically, so no separate
driver install is needed — GitHub Actions' `ubuntu-latest` runners ship
Chrome preinstalled, which is what CI relies on here.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _build_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    return webdriver.Chrome(options=options)


@pytest.fixture
def driver():
    """A fresh headless Chrome instance, quit after the test regardless of outcome."""
    browser = _build_driver()
    browser.implicitly_wait(2)
    try:
        yield browser
    finally:
        browser.quit()


def _login(driver, live_server, username="admin", password="admin"):
    driver.get(f"{live_server}/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "#loginForm button[type=submit]").click()
    WebDriverWait(driver, 5).until(EC.url_to_be(f"{live_server}/"))


@pytest.fixture
def logged_in_driver(driver, live_server):
    """A driver that has logged in through the real UI and landed on the main page."""
    _login(driver, live_server)
    return driver
