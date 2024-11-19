from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import sqlite3

# Initialize database
def initialize_database():
    connection = sqlite3.connect("profile_database.db")
    cursor = connection.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS profile_info (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        profile_name TEXT,
                        role TEXT,
                        number_of_posts TEXT,
                        member_since TEXT,
                        last_visited TEXT,
                        website TEXT,
                        gender TEXT,
                        location TEXT,
                        omnicoin TEXT,
                        banknotebank TEXT,
                        profile_views TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS visitors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        profile_link TEXT,
                        time_of_visit TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS activity (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        post_name TEXT,
                        post_link TEXT,
                        content TEXT,
                        time_of_reply TEXT)''')

    connection.commit()
    return connection, cursor

# Initialize the WebDriver
def initialize_driver():
    print("Initializing driver...\n")

    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    driver.get("https://web.archive.org/web/20230307163448/https://www.coinpeople.com/profile/3-akdrv/")

    time.sleep(5)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    time.sleep(2)

    page_source = driver.page_source
    profile_scraper(page_source)

    driver.quit()

# Scraper function
def profile_scraper(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    connection, cursor = initialize_database()

    archive_prefix = "https://web.archive.org/web/20230506212637/"

    # Scrape profile information
    profile_name = soup.find("h1", class_="ipsType_reset ipsPageHead_barText").getText().strip()
    role = soup.find("span", class_="ipsPageHead_barText").getText()
    number_of_posts = soup.find('h4', string='Posts').find_next_sibling(string=True).strip()
    member_since = soup.find('h4', string='Joined').find_next('time').text.strip()
    last_visited = soup.find('h4', string='Last visited').find_next('time')['title']
    website = soup.find("div", class_="ipsType_break ipsContained").getText()
    gender = soup.find('span', string='Gender').find_next('div').text.strip()
    location = soup.find('span', string='Location').find_next('div').text.strip()
    omnicoin = soup.find('span', string='OmniCoin').find_next('div').text.strip()
    banknotebank = soup.find('span', string='BanknoteBank').find_next('div').text.strip()
    profile_views = soup.select_one('span.ipsType_light').text.strip()

    # Insert profile data
    cursor.execute('''INSERT INTO profile_info (profile_name, role, number_of_posts, member_since, last_visited, website, gender, location, omnicoin, banknotebank, profile_views) 
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (profile_name, role, number_of_posts, member_since, last_visited, website, gender, location, omnicoin, banknotebank, profile_views))
    connection.commit()

    # Scrape visitor information
    visitor_box = soup.find("ul", class_="ipsDataList ipsDataList_reducedSpacing ipsSpacer_top")
    names = visitor_box.find_all("h3", class_="ipsDataItem_title")
    profile_links = visitor_box.find_all("h3", class_="ipsDataItem_title")
    time_of_visits = visitor_box.find_all("p", class_="ipsDataItem_meta ipsType_light")

    for name, profile_link, time_of_visit in zip(names, profile_links, time_of_visits):
        cursor.execute('''INSERT INTO visitors (name, profile_link, time_of_visit) 
                          VALUES (?, ?, ?)''',
                       (name.getText().strip(), profile_link.find("a", class_="ipsType_break").get("href"), time_of_visit.getText()))
    connection.commit()

    # Scrape activity information
    activity_box = soup.find("ol", id="elProfileActivityOverview")
    post_names = activity_box.find_all("span", class_="ipsType_break ipsContained")
    post_links = activity_box.find_all("span", class_="ipsType_break ipsContained")
    contents = activity_box.find_all("div", class_="ipsType_richText ipsContained ipsType_medium")
    time_of_replys = activity_box.find_all("a", class_="ipsType_blendLinks")

    for post_name, post_link, content, time_of_reply in zip(post_names, post_links, contents, time_of_replys):
        cursor.execute('''INSERT INTO activity (post_name, post_link, content, time_of_reply) 
                          VALUES (?, ?, ?, ?)''',
                       (post_name.getText().strip(), f"{archive_prefix}{post_link.find('a').get('href')}", content.getText().strip(), time_of_reply.getText().strip()))
    connection.commit()

    connection.close()

initialize_driver()
