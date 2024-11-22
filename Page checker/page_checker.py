import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Initialize the CSV file for error logging
csv_file = "Page checker/world_coin_forum.csv"
with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["starting_url", "date", "last_url"])  # Write header row

# Read URLs from the file
input_file = "Page checker/world_coin_forum_links.txt"
try:
    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]
except FileNotFoundError:
    print(f"Error: The file {input_file} does not exist.")
    exit()

# Initialize the WebDriver
driver = webdriver.Chrome()
# driver.maximize_window()

try:
    for starting_url in urls:
        print(f"Processing URL: {starting_url}")
        driver.get(starting_url)

        try:
            # Wait for the Next button on the initial page
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'ipsPagination_next'))
            )
            driver.execute_script('document.querySelector("[title=\\"Next page\\"]").click();')

            while True:
                try:
                    # Wait for the presence of the Next button on subsequent pages
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, 'ipsPagination_next'))
                    )
                    # Click the Next page button
                    driver.execute_script('document.querySelector("[title=\\"Next page\\"]").click();')
                except TimeoutException:
                    # Extract date from the URL
                    current_url = driver.current_url
                    date = current_url.split("/")[4]  # Extract the date segment
                    print(f"Timeout reached. Stopping at URL: {current_url}")

                    # Write to CSV
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([starting_url, date, current_url])
                    break
                except NoSuchElementException:
                    # Extract date from the URL
                    current_url = driver.current_url
                    date = current_url.split("/")[4]  # Extract the date segment
                    print(f"No Next button found. Stopping at URL: {current_url}")

                    # Write to CSV
                    with open(csv_file, 'a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([starting_url, date, current_url])
                    break
        except Exception as e:
            current_url = driver.current_url
            date = current_url.split("/")[4] if "/web/" in current_url else "unknown"
            print(f"An error occurred while processing {starting_url}: {e}")
            print(f"Stopping at URL: {current_url}")

            # Write to CSV
            with open(csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([starting_url, date, current_url])
finally:
    driver.quit()