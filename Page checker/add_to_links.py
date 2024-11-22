def append_to_links(input_file, output_file, append_path):
    try:
        # Read the input file
        with open(input_file, 'r') as infile:
            links = infile.readlines()

        # Process each link and append the specified path
        modified_links = [link.strip() + append_path for link in links if link.strip()]

        # Write the modified links to the output file
        with open(output_file, 'w') as outfile:
            outfile.write('\n'.join(modified_links))

        print(f"Modified links have been saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Specify the input file, output file, and the path to append
input_file = "Page checker/links_to_modify.txt"
output_file = "Page checker/ancient_coin_forum_links.txt"
append_path = "/forum/245-ancient-coin-forum/page/5/"

# Run the function
append_to_links(input_file, output_file, append_path)