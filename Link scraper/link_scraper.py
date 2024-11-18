from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def initialize_driver():
    print("Initializing driver...\n")

    with open("Link scraper/initial_links.txt", "r") as links:

        for link in links:
            options = Options()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)
            driver.get(link)

            time.sleep(5)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(2)

            page_source = driver.page_source

            initialize_soup(page_source)

            print(f"Scraped links for {link}.\n")
        
        driver.quit()

def initialize_soup(page_source):
    soup = BeautifulSoup(page_source, "html.parser")

    links = soup.find_all("div", class_="calendar-day")
    links_table = [
        f"https://web.archive.org{link.find("a").get("href")}" for link in links
    ]

    for link in links_table:
        with open("Link scraper/links_to_scrape_posts.txt", "a") as file:
            file.write(f"{link}\n")
    print(f"Information for {link} was sucessfully saved. {len(links_table)} links added to the file.")    

initialize_driver()