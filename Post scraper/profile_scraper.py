from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sqlite3

# Initialize profile_database.db
def initialize_database():
    connection = sqlite3.connect("profile_database.db")
    cursor = connection.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS profile_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_name TEXT UNIQUE, 
                        role TEXT,
                        number_of_posts TEXT,
                        member_since TEXT,
                        last_visited TEXT,
                        website TEXT,
                        gender TEXT,
                        location TEXT,
                        omnicoin TEXT,
                        banknotebank TEXT,
                        profile_views TEXT,
                        author_profile_id INTEGER)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS visitors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_name TEXT,  
                        visitor_name TEXT,
                        visitor_profile_link TEXT,
                        time_of_visit TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_name TEXT,  
                        post_name TEXT,
                        post_link TEXT,
                        content TEXT,
                        time_of_reply TEXT)''')

    connection.commit()
    return connection, cursor

# Add author_profile_id column to profile_info table (if it doesn't exist)
def add_author_profile_id_column(cursor):
    cursor.execute("PRAGMA table_info(profile_info)")
    columns = [col[1] for col in cursor.fetchall()]
    if "author_profile_id" not in columns:
        cursor.execute("ALTER TABLE profile_info ADD COLUMN author_profile_id INTEGER")

# Initialize WebDriver
def initialize_driver():
    print("Initializing driver...\n")

    options = Options()
    # options.add_argument('--headless')  # Uncomment for headless mode
    driver = webdriver.Chrome(options=options)

    # Fetch all profile URLs from posts_data.db
    posts_conn = sqlite3.connect("posts_data.db")
    posts_cursor = posts_conn.cursor()

    posts_cursor.execute("SELECT id, author_profile FROM posts")  # Assuming posts table has 'id' and 'author_profile'
    profile_links = posts_cursor.fetchall()

    for author_profile_id, profile_link in profile_links:
        driver.get(profile_link)  # Access each profile link
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        page_source = driver.page_source
        profile_scraper(page_source, profile_link, author_profile_id)  # Pass author_profile_id for linkage

    driver.quit()
    posts_conn.close()

# Scraper function
def profile_scraper(page_source, profile_link, author_profile_id):
    soup = BeautifulSoup(page_source, "html.parser")
    connection, cursor = initialize_database()
    add_author_profile_id_column(cursor)

    try:
        profile_name = soup.find("h1", class_="ipsType_reset ipsPageHead_barText").getText().strip()
    except Exception as e:
        profile_name = "N/A"
        print(f"Error scraping profile_name: {e}")

    # Check if profile already exists in the database
    cursor.execute('''SELECT COUNT(*) FROM profile_info WHERE profile_name = ?''', (profile_name,))
    result = cursor.fetchone()
    if result[0] > 0:
        print(f"Profile '{profile_name}' already exists in the database. Skipping.")
        connection.close()
        return

    # Extract profile details
    try:
        role = soup.find("span", class_="ipsPageHead_barText").getText().strip()
    except Exception:
        role = "N/A"

    try:
        number_of_posts = soup.find('h4', string='Posts').find_next_sibling(string=True).strip()
    except Exception:
        number_of_posts = "N/A"

    try:
        member_since = soup.find('h4', string='Joined').find_next('time').text.strip()
    except Exception:
        member_since = "N/A"

    try:
        last_visited = soup.find('h4', string='Last visited').find_next('time')['title']
    except Exception:
        last_visited = "N/A"

    try:
        website = soup.find("div", class_="ipsType_break ipsContained").getText().strip()
    except Exception:
        website = "N/A"

    try:
        gender = soup.find('span', string='Gender').find_next('div').text.strip()
    except Exception:
        gender = "N/A"

    try:
        location = soup.find('span', string='Location').find_next('div').text.strip()
    except Exception:
        location = "N/A"

    try:
        omnicoin = soup.find('span', string='OmniCoin').find_next('div').text.strip()
    except Exception:
        omnicoin = "N/A"

    try:
        banknotebank = soup.find('span', string='BanknoteBank').find_next('div').text.strip()
    except Exception:
        banknotebank = "N/A"

    try:
        profile_views = soup.select_one('span.ipsType_light').text.strip()
    except Exception:
        profile_views = "N/A"

    # Insert profile data into profile_info table
    cursor.execute('''INSERT INTO profile_info (profile_name, role, number_of_posts, member_since, last_visited, website, 
                      gender, location, omnicoin, banknotebank, profile_views, author_profile_id) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (profile_name, role, number_of_posts, member_since, last_visited, website, gender, location,
                    omnicoin, banknotebank, profile_views, author_profile_id))
    connection.commit()

    # Scrape visitor information
    try:
        visitor_box = soup.find("ul", class_="ipsDataList ipsDataList_reducedSpacing ipsSpacer_top")
        names = visitor_box.find_all("h3", class_="ipsDataItem_title")
        profile_links = visitor_box.find_all("h3", class_="ipsDataItem_title")
        time_of_visits = visitor_box.find_all("p", class_="ipsDataItem_meta ipsType_light")

        for name, profile_link, time_of_visit in zip(names, profile_links, time_of_visits):
            cursor.execute('''INSERT INTO visitors (profile_name, visitor_name, visitor_profile_link, time_of_visit) 
                              VALUES (?, ?, ?, ?)''',
                           (profile_name, name.getText().strip(),
                            profile_link.find("a", class_="ipsType_break").get("href"), time_of_visit.getText()))
        connection.commit()
    except Exception as e:
        print(f"Error scraping visitor information: {e}")

    # Scrape activity information
    try:
        activity_box = soup.find("ol", id="elProfileActivityOverview")
        post_names = activity_box.find_all("span", class_="ipsType_break ipsContained")
        post_links = activity_box.find_all("span", class_="ipsType_break ipsContained")
        contents = activity_box.find_all("div", class_="ipsType_richText ipsContained ipsType_medium")
        time_of_replys = activity_box.find_all("a", class_="ipsType_blendLinks")

        for post_name, post_link, content, time_of_reply in zip(post_names, post_links, contents, time_of_replys):
            cursor.execute('''INSERT INTO activity (profile_name, post_name, post_link, content, time_of_reply) 
                              VALUES (?, ?, ?, ?, ?)''',
                           (profile_name, post_name.getText().strip(),
                            post_link.find("a").get("href"), content.getText().strip(), time_of_reply.getText().strip()))
        connection.commit()
    except Exception as e:
        print(f"Error scraping activity information: {e}")

    connection.close()

# Fetch and display profiles with linked posts
def fetch_profiles_with_posts():
    profile_conn = sqlite3.connect("profile_database.db")
    profile_conn.execute("ATTACH DATABASE 'posts_data.db' AS posts_db")
    cursor = profile_conn.cursor()

    # Query to join profile_info with posts using author_profile_id
    cursor.execute('''
        SELECT p.id, p.profile_name, p.role, po.title, po.content
        FROM profile_info p
        LEFT JOIN posts_db.posts po
        ON p.author_profile_id = po.id
    ''')

    results = cursor.fetchall()
    for row in results:
        print(row)

    profile_conn.close()

# Run the scraper
initialize_driver()
<<<<<<< HEAD
fetch_profiles_with_posts()
=======
fetch_profiles_with_posts()
>>>>>>> 653af61ecc8be1f07a4d63800ab573cec9fc2827
