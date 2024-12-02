import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# File names
input_file = "page_links.csv"
output_file = "page_links_cleaned.csv"

# Selenium WebDriver setup
driver = webdriver.Chrome()


# Function to check if either XPath exists on the page
def check_link(link):
    try:
        time.sleep(3)
        driver.get(link)

        # Define the two XPaths
        first_xpath = '//*[@id="react-wayback-search"]/div[4]/div[2]/div[4]/div[2]/div[1]/div[7]/div'
        second_xpath = '//*[@id="ips_uid_2746_7"]'

        # Check for the presence of either XPath
        xpath_found = False
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, first_xpath))
            )
            xpath_found = True
        except:
            print(f"First XPath not found for link: {link}")

        if not xpath_found:  # Check the second XPath only if the first one is not found
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, second_xpath))
                )
                xpath_found = True
            except:
                print(f"Second XPath not found for link: {link}")

        if not xpath_found:
            return False  # Invalid if neither XPath exists

        # Check page source for the error message
        if "The file you were looking for could not be found" in driver.page_source:
            print(f"Invalid link detected: {link}")
            return False  # Link is invalid if the error message is present

    except Exception as e:
        print(f"Error processing {link}: {e}")
        return False  # Treat as invalid if an error occurs


    return True  # Link is valid


# Open the CSV and process links
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", newline="", encoding="utf-8") as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    header = next(reader)  # Read header
    writer.writerow(header)  # Write header to output file

    for row in reader:
        link = row[0]
        if check_link(link):  # Check if the link is valid
            writer.writerow(row)  # Write valid link to the output file

# Cleanup
driver.quit()
print(f"Cleaned CSV file saved as {output_file}")
