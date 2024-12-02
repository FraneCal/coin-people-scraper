import csv

# Input and output file names
input_file = "cleaned_links.csv"  # Replace with your input file

page_links_file = "../working/page_links.csv"
image_links_file = "../working/image_links.csv"
other_links_file = "../working/other_links.csv"

# Read links from the CSV file
with open(input_file, "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    next(reader)  # Skip header if there is one
    links = [row[0] for row in reader]

# Categorize links
page_links = [link for link in links if "page" in link.lower()]
image_links = [link for link in links if link.lower().endswith((".jpg", ".jpeg", ".png"))]
other_links = [link for link in links if link not in page_links and link not in image_links]

# Function to save links to a CSV file
def save_to_csv(file_name, links):
    with open(file_name, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Link"])  # Add header
        writer.writerows([[link] for link in links])
    print(f"Saved {len(links)} links to {file_name}.")

# Save categorized links
save_to_csv(page_links_file, page_links)
save_to_csv(image_links_file, image_links)
save_to_csv(other_links_file, other_links)
