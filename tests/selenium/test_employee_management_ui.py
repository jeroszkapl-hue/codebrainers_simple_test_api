"""SEL-EMP-xx — browser-driven tests for the main Employee Manager page.

See tests/selenium/TEST_PLAN.md for the full test case list with steps.
"""

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


def _fill_employee_form(
    driver, name="Jan Kowalski", salary="5000", age="30", position="Mid QA"
):
    name_input = driver.find_element(By.ID, "name")
    name_input.clear()
    name_input.send_keys(name)

    salary_input = driver.find_element(By.ID, "salary")
    salary_input.clear()
    salary_input.send_keys(salary)

    age_input = driver.find_element(By.ID, "age")
    age_input.clear()
    age_input.send_keys(age)

    Select(driver.find_element(By.ID, "position")).select_by_visible_text(position)


def _employee_rows(driver):
    return driver.find_elements(By.CSS_SELECTOR, "#employees tr")


def test_sel_emp_01_add_employee_appears_in_table(logged_in_driver):
    driver = logged_in_driver

    _fill_employee_form(driver)
    driver.find_element(By.ID, "submitBtn").click()

    WebDriverWait(driver, 5).until(lambda d: len(_employee_rows(d)) == 1)
    assert "Jan Kowalski" in _employee_rows(driver)[0].text


def test_sel_emp_02_edit_employee_updates_row(logged_in_driver):
    driver = logged_in_driver

    _fill_employee_form(driver)
    driver.find_element(By.ID, "submitBtn").click()
    WebDriverWait(driver, 5).until(lambda d: len(_employee_rows(d)) == 1)

    driver.find_element(By.CSS_SELECTOR, "#employees .btn-edit").click()

    salary_input = driver.find_element(By.ID, "salary")
    salary_input.clear()
    salary_input.send_keys("9999")

    driver.find_element(By.ID, "submitBtn").click()

    # The table re-renders (DOM nodes get swapped, not just updated) after a
    # successful edit, so a row fetched by _employee_rows() can go stale
    # between that fetch and reading .text off it a moment later. Ignoring
    # StaleElementReferenceException here just makes WebDriverWait retry on
    # the next poll instead of failing the test on that race.
    WebDriverWait(
        driver, 5, ignored_exceptions=(StaleElementReferenceException,)
    ).until(lambda d: "9999" in _employee_rows(d)[0].text)


def test_sel_emp_03_delete_employee_removes_row(logged_in_driver):
    driver = logged_in_driver

    _fill_employee_form(driver)
    driver.find_element(By.ID, "submitBtn").click()
    WebDriverWait(driver, 5).until(lambda d: len(_employee_rows(d)) == 1)

    driver.find_element(By.CSS_SELECTOR, "#employees .btn-delete").click()

    WebDriverWait(driver, 5).until(lambda d: len(_employee_rows(d)) == 0)


def test_sel_emp_04_invalid_age_shows_inline_error_and_no_row_added(logged_in_driver):
    driver = logged_in_driver

    _fill_employee_form(driver, age="10")
    driver.find_element(By.ID, "submitBtn").click()

    error_box = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "errorBox"))
    )
    assert error_box.text
    assert len(_employee_rows(driver)) == 0


def test_sel_emp_05_reset_modal_cancel_keeps_data(logged_in_driver):
    driver = logged_in_driver

    _fill_employee_form(driver)
    driver.find_element(By.ID, "submitBtn").click()
    WebDriverWait(driver, 5).until(lambda d: len(_employee_rows(d)) == 1)

    driver.find_element(By.CSS_SELECTOR, 'button[onclick="resetData()"]').click()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "resetModal"))
    )

    driver.find_element(By.CSS_SELECTOR, ".btn-cancel").click()

    assert len(_employee_rows(driver)) == 1


def test_sel_emp_06_reset_confirm_clears_table(logged_in_driver):
    driver = logged_in_driver

    _fill_employee_form(driver)
    driver.find_element(By.ID, "submitBtn").click()
    WebDriverWait(driver, 5).until(lambda d: len(_employee_rows(d)) == 1)

    driver.find_element(By.CSS_SELECTOR, 'button[onclick="resetData()"]').click()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "resetModal"))
    )
    driver.find_element(By.CSS_SELECTOR, ".btn-confirm-danger").click()

    WebDriverWait(driver, 5).until(lambda d: len(_employee_rows(d)) == 0)


def test_sel_emp_07_logout_returns_to_login_page(logged_in_driver, live_server):
    driver = logged_in_driver

    driver.find_element(By.CSS_SELECTOR, 'button[onclick="logout()"]').click()

    WebDriverWait(driver, 5).until(EC.url_to_be(f"{live_server}/login"))
