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
                        author_name  TEXT,
                        profile_link TEXT,
                        comment_date TEXT,
                        comment TEXT)''')

    connection.commit()
    return connection, cursor

# Fetch post data from posts_data.db
def get_posts_from_db():
    posts_connection = sqlite3.connect("posts_data.db")
    posts_cursor = posts_connection.cursor()

    # Fetch all rows from the posts table
    posts_cursor.execute("SELECT title, link FROM posts WHERE title IS NOT NULL AND link IS NOT NULL")
    posts = posts_cursor.fetchall()

    posts_connection.close()
    return posts

# Initialize WebDriver
def initialize_driver():
    print("Initializing driver...\n")

    options = Options()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(options=options)

    # Get post data from the posts_data.db database
    posts = get_posts_from_db()

    # Loop through each post and scrape its data
    for post_name, post_link in posts:
        driver.get(post_link)
        time.sleep(5)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Scrape the page source
        page_source = driver.page_source
        scraper(page_source, post_name, post_link)  # Pass post details

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

    for name, profile_link, comment_date, comment in zip(names, profile_links, comment_dates, comments):
        # Extract and clean data
        user_name = name.getText().strip()
        user_profile_link = f"{archive_prefix}{profile_link.find('a').get('href')}"
        comment_date_text = comment_date.find("time").getText().strip()
        comment_text = comment.getText().strip()

        # Insert data into the database
        cursor.execute('''INSERT INTO comments (post_name, post_link, author_name, profile_link, comment_date, comment)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                       (post_name, post_link, user_name, user_profile_link, comment_date_text, comment_text))
        connection.commit()

    connection.close()
    print(f"Scraped data for post '{post_name}' saved to database.")

# Run the scraper
initialize_driver()