from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

URL = "https://web.archive.org/web/20230203123249/https://www.coinpeople.com/forum/64-new-member-information-and-welcome33/"

driver = webdriver.Chrome()
driver.get(URL)

time.sleep(5)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

time.sleep(2)

while True:
    try:
        next_page = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'//*[@id="elPagination_30a5535a7a65933469c1ef7e81dc96e0_806040338"]/li[9]/a'))
        )
        next_page.click()
    except TimeoutException:
            print("No more pages to click.")
            break 


driver.quit()