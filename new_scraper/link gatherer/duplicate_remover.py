import pandas as pd

# Input and output file names
input_file = "scraped_links.csv"  # Replace with your file name
output_file = "cleaned_links.csv"

# Read the CSV file
df = pd.read_csv(input_file)

# Remove duplicates based on the 'Link' column
df_unique = df.drop_duplicates(subset="Link")

# Save the unique entries back to a new CSV file
df_unique.to_csv(output_file, index=False)

print(f"Duplicates removed. Unique entries saved to '{output_file}'.")
