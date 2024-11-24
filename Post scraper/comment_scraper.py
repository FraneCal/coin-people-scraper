from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sqlite3

# Initialize database and create table for comments
def initialize_database():
    connection = sqlite3.connect("scraped_comments.db")
    cursor = connection.cursor()

    # Create a table for storing comments
    cursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_name TEXT,
                        post_link TEXT,
                        author_name TEXT,
                        profile_link TEXT,
                        comment_date TEXT,
                        comment TEXT,
                        image_url TEXT)''')  # Added image_url column

    connection.commit()
    return connection, cursor

# Fetch post data from posts_data.db
def get_posts_from_db():
    # Default starting line (adjust as needed)
    default_start_line = 194  # Start fetching from the 195th row (zero-based index)

    posts_connection = sqlite3.connect("coin_forum_posts.db")
    posts_cursor = posts_connection.cursor()

    # Fetch rows starting from the default line
    posts_cursor.execute(
        "SELECT title, link FROM posts WHERE title IS NOT NULL AND link IS NOT NULL LIMIT -1 OFFSET ?",
        (default_start_line,)
    )
    posts = posts_cursor.fetchall()

    posts_connection.close()
    return posts

# Initialize WebDriver
def initialize_driver():
    # https://web.archive.org/web/20210307115650/https://www.coinpeople.com/topic/11213-commerce-industries-coin/page/2/#comments

    print("Initializing driver...\n")

    options = Options()
    # Uncomment the next line for headless mode
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    # --- Main Functionality: Process Posts from Database ---
    posts = get_posts_from_db() 
    for post_name, post_link in posts:
        try:
            print(f"Processing link: {post_link}")
            driver.get(post_link)
            time.sleep(5)

            repeated_count = 0
            last_page_source = None

            while True:
                # Scroll to the bottom to ensure all content is loaded
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                # Scrape the current page
                page_source = driver.page_source

                # Check if the page is the same as the last one
                if page_source == last_page_source:
                    repeated_count += 1
                    print(f"Repeated page detected ({repeated_count}/3) for '{post_name}'.")
                    if repeated_count >= 3:
                        print(f"Skipping to the next link after detecting 3 repeated pages for '{post_name}'.")
                        break
                else:
                    repeated_count = 0  # Reset counter if the page is new
                    last_page_source = page_source  # Update last seen page content

                # Process the current page content
                scraper(page_source, post_name, post_link)

                # Check and click "Next page" if available
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, '[title="Next page"]')
                    next_button.click()
                    time.sleep(3)  # Wait for the next page to load
                except Exception:
                    print(f"No more pages to scrape for '{post_name}'.")
                    break  # Exit the loop if the "Next page" button is not found

        except Exception as e:
            print(f"Error scraping '{post_name}' at {post_link}: {e}")

    # --- Testing a Single Link ---
    # Uncomment this block to test a single link
    # test_post_name = "Test Post"
    # test_post_link = ("https://web.archive.org/web/20220704143917/https://www.coinpeople.com/topic/40449-1982-d-small-date-finnally/")
    # try:
    #     driver.get(test_post_link)
    #     time.sleep(5)

    #     while True:
    #         # Scroll to the bottom to ensure all content is loaded
    #         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #         time.sleep(2)

    #         # Scrape the current page
    #         page_source = driver.page_source
    #         scraper(page_source, test_post_name, test_post_link)

    #         # Check and click "Next page" if available
    #         try:
    #             driver.execute_script('document.querySelector("[title=\\"Next page\\"]").click();')
    #             time.sleep(3)  # Wait for the next page to load
    #         except Exception:
    #             print(f"No more pages to scrape for '{test_post_name}'.")
    #             break  # Exit the loop if the "Next page" button is not found

    # except Exception as e:
    #     print(f"Error testing single link: {e}")

    driver.quit()

# Scraper function
def scraper(page_source, post_name, post_link):
    soup = BeautifulSoup(page_source, "html.parser")
    connection, cursor = initialize_database()

    archive_prefix = "https://web.archive.org/web/20230506212637/"

    # Extract data
    names = soup.find_all("h3", class_="ipsType_sectionHead cAuthorPane_author ipsType_blendLinks ipsType_break")
    profile_links = soup.find_all("h3", class_="ipsType_sectionHead cAuthorPane_author ipsType_blendLinks ipsType_break")
    comment_dates = soup.find_all("div", class_="ipsType_reset ipsResponsive_hidePhone")
    comments = soup.find_all("div", class_="ipsType_normal ipsType_richText ipsPadding_bottom ipsContained")
    images = soup.find_all("div", class_="ipsType_normal ipsType_richText ipsPadding_bottom ipsContained")

    for name, profile_link, comment_date, comment, image in zip(names, profile_links, comment_dates, comments, images):
        try:
            # Extract and clean data
            user_name = name.getText().strip()
            user_profile_link = f"{archive_prefix}{profile_link.find('a').get('href')}"
            comment_date_text = comment_date.find("time").getText().strip()
            comment_text = comment.getText().strip()

            # Try to extract the image URL
            try:
                image_tag = image.find("img")
                image_url = image_tag['src'] if image_tag else None
            except Exception as e:
                image_url = None  # Set to None if no image is found or any error occurs

            # Skip saving images starting with "https://content.invisioncic.com"
            # if image_url and image_url.startswith("https://content.invisioncic.com"):
            #     image_url = None

            # Insert data into the database
            cursor.execute('''INSERT INTO comments (post_name, post_link, author_name, profile_link, comment_date, comment, image_url)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (post_name, post_link, user_name, user_profile_link, comment_date_text, comment_text, image_url))
            connection.commit()

        except Exception as e:
            print(f"Error processing comment: {e}")
            continue

    connection.close()
    print(f"Scraped data for post '{post_name}' saved to database.")

initialize_driver()
