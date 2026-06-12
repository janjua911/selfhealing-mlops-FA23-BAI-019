"""
Selenium headless UI test for the Sentiment Analyzer frontend.
Run with: pytest tests/test_ui.py
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_URL = "http://localhost:5000"


def test_frontend_sentiment():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(BASE_URL)

        text_input = driver.find_element(By.ID, "text-input")
        submit_btn = driver.find_element(By.ID, "submit-btn")

        text_input.send_keys("This product is absolutely amazing and wonderful")
        submit_btn.click()

        # Wait for the async fetch/predict call to complete
        time.sleep(3)

        result = driver.find_element(By.ID, "result-output")
        result_text = result.text.strip()

        assert result_text != ""
        assert (
            "POSITIVE" in result_text
            or "NEGATIVE" in result_text
            or "Confidence" in result_text
        )
    finally:
        driver.quit()
