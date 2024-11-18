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

    # WebDriverWait(driver, 10).until(
    #     EC.presence_of_all_elements_located((By.XPATH, '//*[@id="ipsLayout_contentWrapper"]/nav[2]/ul[2]/li/a'))
    # )

    time.sleep(5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(2)

    page_source = driver.page_source

    initialize_soup(page_source)

    driver.quit()

def initialize_soup(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    box = soup.find("ol", class_="ipsList_reset cForumList")

    links = box.find_all("li", class_="cForumRow ipsDataItem ipsDataItem_responsivePhoto  ipsClearfix")
    links_list = [
        f"{link.get("href")}" for link in links
    ]
    # Should be a total of 24 links.
    print(links_list)

    # for link in links_table:
    #     print(f"{link}\n")

initialize_driver()
