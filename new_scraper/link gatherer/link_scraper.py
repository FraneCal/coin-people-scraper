from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

URL = "https://web.archive.org/web/*/coinpeople.com/forum/256-numismatic-resources-forums*"

# Initialize the web driver
driver = webdriver.Chrome()
driver.get(URL)

# Wait for the page to load
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="resultsUrl"]/tbody/tr[1]/td[1]/a')))

all_links = []
previous_page_source = None  # To track if we are stuck on the same page

try:
    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow time for page to load additional data

        # Parse the page source
        current_page_source = driver.page_source  # Capture current page source
        if previous_page_source == current_page_source:
            # If page source hasn't changed, assume we're stuck
            print("Reached the last page or stuck on the same page.")
            break
        previous_page_source = current_page_source  # Update previous_page_source

        soup = BeautifulSoup(current_page_source, "html.parser")

        # Find all relevant links
        links = soup.find_all("td", class_="url sorting_1")
        links_list = [link.find("a").get("href") for link in links]
        all_links.extend(links_list)

        print(f"Scraped {len(links_list)} links from the current page.")

        # Try to click the "Next" button
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "[data-dt-idx='next']")
            if "disabled" in next_button.get_attribute("class"):
                print("No more pages to scrape.")
                break
            next_button.click()
        except Exception as e:
            print("No 'Next' button found or an error occurred:", e)
            break

        time.sleep(5)  # Wait for the next page to load

finally:
    driver.quit()

# Save the links to a CSV file
output_file = "scraped_links.csv"
with open(output_file, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    # writer.writerow(["Link"])  # Write header
    for link in all_links:
        writer.writerow([link])

print(f"Scraping completed. {len(all_links)} links saved to {output_file}.")