from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


# Set up Chrome options
options = Options()
options.add_argument("--headless")  # run in background
options.add_argument("--disable-gpu")

# Update path to your chromedriver
service = Service(r"D:\path\to\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

url = "https://economictimes.indiatimes.com/commoditysummary/symbol-SILVER.cms"
driver.get(url)

# Wait a few seconds for JavaScript to load
time.sleep(5)

# Inspect element to find the correct CSS selector
# Example: On ET, silver price may be inside <div class="price"> or similar
try:
    price_element = driver.find_element(By.CSS_SELECTOR, ".value")  # adjust selector
    silver_price = price_element.text
    print(f"Current Silver Price: {silver_price}")
except:
    print("Price not found")

driver.quit()