from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import sqlite3

def initialize_database():
    connection = sqlite3.connect("coin_forum_posts.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            author TEXT,
            author_profile TEXT,
            date TEXT,
            replies TEXT,
            views TEXT
        )
    """)
    connection.commit()
    connection.close()

def save_to_database(data):
    connection = sqlite3.connect("coin_forum_posts.db")
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO posts (title, link, author, author_profile, date, replies, views)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)
        connection.commit()
        # print(f"Saved: {data[0]}")

    except sqlite3.IntegrityError:
        # Handle the case where a duplicate link is found
        print(f"Duplicate found for link: {data[1]}")

    connection.close()

def initialize_driver():
    print("Initializing driver...\n")

    initialize_database()

    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get("https://web.archive.org/web/20180705012324/http://www.coinpeople.com/forum/4-coin-forum/?page=150")

    time.sleep(5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(2)

    counter = 1

    # Loop to go through all pages
    while True:
        print(f"\nCurrently scraping page {counter}.\n")

        # Get the page source for the current page
        page_source = driver.page_source
        
        # Call the basic post scraper to process the current page
        basic_post_scraper(page_source)

        # Try to find the 'next page' button and click it
        try:
            # next_page = WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, '//*[@id="elPagination_30a5535a7a65933469c1ef7e81dc96e0_806040338"]/li[9]/a'))
            # )
            # next_page.click()
          
            driver.execute_script('document.querySelector("[title=\\"Previous page\\"]").click();')

            counter += 1

            time.sleep(5)  # Wait for the page to load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll to the bottom
            time.sleep(2)  # Wait a bit before continuing

        except TimeoutException:
            print("No more pages to click.")
            break  # Break the loop if there's no 'next page' button (i.e., we're on the last page)

    driver.quit()

def basic_post_scraper(page_source):
    soup = BeautifulSoup(page_source, "html.parser")

    # Find all posts on the page
    posts = soup.find_all("div", class_="ipsDataItem_main")

    # Remove the first 3 elements if the list contains 28 items
    if len(posts) == 28:
        posts = posts[3:]  # Slice the list to exclude the first 3 elements
    elif len(posts) == 26:
        posts = posts[1:]
    elif len(posts) == 24:
        posts = posts[3:]
    else:
        pass

    print(f"Posts after filtering: {len(posts)}")

    replies = []
    views = []

    # Locate stats blocks
    stat_blocks = soup.find_all("ul", class_="ipsDataItem_stats")
    print(f"Stat blocks found: {len(stat_blocks)}")

    for block in stat_blocks:
        try:
            # Extract replies
            reply_stat = block.find("span", class_="ipsDataItem_stats_type")
            if reply_stat and ("reply" in reply_stat.getText().strip().lower()):
                reply_count = reply_stat.find_previous_sibling("span").getText().strip()
                replies.append(reply_count)
            else:
                replies.append("0")  # Default if no reply data found

            # Extract views
            view_stat = block.find("span", string=" views")
            if view_stat:
                view_count = view_stat.find_previous_sibling("span").getText().strip()
                views.append(view_count)
            else:
                views.append("0")  # Default if no view data found

        except AttributeError:
            # Handle missing or unexpected structure gracefully
            replies.append("0")
            views.append("0")

    print(f"Replies after processing: {len(replies)}")
    print(f"Views after processing: {len(views)}")

    # Ensure replies and views align with posts
    while len(replies) < len(posts):
        replies.append("0")

    while len(views) < len(posts):
        views.append("0")

    archive_prefix = "https://web.archive.org/web/20230506212637/"

    for post, number_of_replies, number_of_views in zip(posts, replies, views):
        try:
            # Extract details for each post
            post_title = post.find("span", class_="ipsType_break ipsContained").getText().strip()
            link = post.find("span", class_="ipsType_break ipsContained").find("a").get("href")
            author = post.find("div", class_="ipsDataItem_meta ipsType_reset ipsType_light ipsType_blendLinks").find("a", class_="ipsType_break").getText().strip()
            author_profile_link = post.find("div", class_="ipsDataItem_meta ipsType_reset ipsType_light ipsType_blendLinks").find("a", class_="ipsType_break").get("href")
            date_of_post = post.find("div", class_="ipsDataItem_meta ipsType_reset ipsType_light ipsType_blendLinks").find("time").getText()

            # Add archive prefix
            archived_link = f"{archive_prefix}{link}"
            archived_author_profile_link = f"{archive_prefix}{author_profile_link}"

            # Save to database
            post_data = (
                post_title,
                archived_link,
                author,
                archived_author_profile_link,
                date_of_post,
                number_of_replies,
                number_of_views
            )

            save_to_database(post_data)
            # print(f"Saved: {post_title}")

        except AttributeError as e:
            print("Error parsing post data:", e)

initialize_driver()

