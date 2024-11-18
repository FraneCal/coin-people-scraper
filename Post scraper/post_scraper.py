from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

def initialize_driver():
    print("Initializing driver...\n")

    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get("https://web.archive.org/web/20230130184517/https://www.coinpeople.com/")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '/html/body/table/tbody/tr[3]/td/center/b/div[2]/table/tbody/tr/td/h1/i/font/b/a'))
        )
        enter_the_page_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/table/tbody/tr[3]/td/center/b/div[2]/table/tbody/tr/td/h1/i/font/b/a')))
        enter_the_page_button.click()
    except TimeoutException:
        pass

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '/html/body/table[2]/tbody/tr/td[2]/p/a'))
        )
        enter_forum = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '/html/body/table[2]/tbody/tr/td[2]/p/a')))
        enter_forum.click()
    except TimeoutException:
        pass

    time.sleep(5)

    driver.quit()

initialize_driver()
