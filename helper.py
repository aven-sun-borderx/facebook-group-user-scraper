import json
import os
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from bs4 import BeautifulSoup
import csv

def get_chrome_driver(user_data_dir=None):
    """
    Sets up a full browser mode undetected Chrome WebDriver.

    Args:
        user_data_dir (str, optional): Path to the Chrome user data directory for maintaining sessions.

    Returns:
        WebDriver: Configured Selenium WebDriver instance.
    """
    options = uc.ChromeOptions()
    options.add_argument("--disable-notifications")  # Disable unnecessary notifications

    if user_data_dir:
        options.add_argument(f"--user-data-dir={user_data_dir}")  # Load user session
        print(f"Using Chrome user data directory: {user_data_dir}")

    # Use undetected ChromeDriver
    print("Running Selenium in undetected full browser mode.")
    return uc.Chrome(options=options)


def search_query(driver, user_input: str, max_retries=3):
    """
    Searches for a query on Facebook after logging in.

    Args:
        driver: Selenium WebDriver instance.
        user_input: The search term to query on Facebook.
        max_retries: Number of retries if the search bar is not found.

    Returns:
        None
    """
    try:
        wait = WebDriverWait(driver, 10)
        retries = 0

        while retries < max_retries:
            try:
                # Locate the search bar using a more resilient XPath
                search_box = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//input[contains(@aria-label, 'Search Facebook')]")
                ))

                # Click the search bar to ensure focus
                search_box.click()
                time.sleep(1)

                # Clear any pre-existing text (if needed)
                search_box.clear()

                # Enter the search query
                search_box.send_keys(user_input)
                print(f"Entered search query: {user_input}")

                # Press ENTER to initiate the search
                search_box.send_keys(Keys.RETURN)
                print("Submitted search query.")
                
                # Wait for search results to load
                time.sleep(5)

                print("Search completed successfully!")
                return  # Exit function on success

            except Exception as e:
                print(f"Error during search attempt {retries+1}: {e}")
                retries += 1
                if retries < max_retries:
                    print("Retrying search...")
                    driver.refresh()  # Refresh to load elements again
                    time.sleep(5)

        print("Failed to perform search after multiple attempts.")

    except Exception as e:
        print(f"Critical error during search: {e}")


def click_groups_tab(driver):
    """
    Clicks on the 'Groups' tab in the Facebook search results.

    Args:
        driver: Selenium WebDriver instance.

    Returns:
        None
    """
    try:
        wait = WebDriverWait(driver, 10)

        # Wait for the 'Groups' tab to be present
        groups_tab = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/search/groups/')]")))

        # Click the 'Groups' tab
        groups_tab.click()
        print("Clicked on the 'Groups' tab successfully!")

        # Wait for groups results to load
        time.sleep(5)

    except Exception as e:
        print(f"Error clicking 'Groups' tab: {e}")

def clean_url(url):
    """
    Cleans Facebook group URLs by:
    - Removing query parameters
    - Removing user-specific paths if the base group exists

    Args:
        url (str): The original URL.

    Returns:
        str: The cleaned URL.
    """
    url = re.sub(r"\?.*", "", url)  # Remove everything after `?`
    url = re.sub(r"/user/\d+", "", url)  # Remove /user/xxxxx paths
    url = re.sub(r"/posts/\d+", "", url)  # Remove /posts/xxxxx paths
    return url.rstrip("/")  # Remove trailing slashes


def append_urls_to_json(new_urls, output_dir, output_file):
    """
    Cleans and appends unique Facebook group URLs to a JSON file.
    Creates the directory and file if they do not exist.

    Args:
        new_urls (list): The list of new URLs to append.
        output_dir (str): The directory where the JSON file is stored.
        output_file (str): Name of the JSON file.

    Returns:
        None
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    # Full path to the JSON file
    file_path = os.path.join(output_dir, output_file)

    # Load existing URLs if the file exists
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            try:
                existing_urls = json.load(f)
                if not isinstance(existing_urls, list):  # Handle unexpected file format
                    print(f"Warning: {file_path} is not a valid JSON list. Resetting file.")
                    existing_urls = []
            except json.JSONDecodeError:
                print(f"Warning: {file_path} contains invalid JSON. Resetting file.")
                existing_urls = []
    else:
        existing_urls = []

    # Clean and deduplicate URLs
    cleaned_new_urls = {clean_url(url) for url in new_urls}
    cleaned_existing_urls = {clean_url(url) for url in existing_urls}

    # Combine and remove duplicates
    all_urls = list(cleaned_existing_urls.union(cleaned_new_urls))

    # Save back to the JSON file
    with open(file_path, "w") as f:
        json.dump(all_urls, f, indent=4)

    print(f"Updated {file_path} with {len(all_urls)} unique, cleaned URLs.")


def add_urls_to_json(urls, output_dir, output_file):
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Full path to the JSON file
    file_path = os.path.join(output_dir, f"{output_file}.json")
    # Save back to the JSON file

    with open(file_path, "w") as f:
        json.dump(urls, f, indent=4)



def load_json(json_file):
    with open(json_file, "r") as f:
        video_urls = json.load(f)
    return video_urls


def extract_group_name(group_url):
    """
    Extracts the group name or ID from a Facebook group URL.

    Args:
        group_url (str): The Facebook group URL.

    Returns:
        str: Extracted group name or ID.
    """
    return group_url.split("/groups/")[-1].split("/")[0]


def get_expected_url(profile_url):
    if "profile.php?id=" in profile_url:
        return 1, f"{profile_url}&sk="  # Append parameter for ID-based profiles
    else:
        return 2, f"{profile_url}"  # Append path for username-based profiles
    

def get_facebook_html(driver, url):
    try:
        # Open the profile page
        driver.get(url)

        # Wait until the page loads
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(5)  # Allow extra time for dynamic content to load

        # Get HTML source
        page_html = driver.page_source
        return page_html

    except Exception as e:
        print(f"❌ Error fetching page HTML: {e}")
        return None
    
    
def extract_facebook_username_id(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Search for JSON data inside <script> tags
    scripts = soup.find_all("script", type="application/json")

    for script in scripts:
        if '"profile_owner"' in script.text:
            id_match = re.search(r'"id":"(\d+)"', script.text)  # Extract user ID
            name_match = re.search(r'"name":"(.*?)"', script.text)  # Extract name

            if id_match and name_match:
                user_id = id_match.group(1)
                name = name_match.group(1)
                return user_id, name  # Return both ID and Name

    return None, None 


def extract_section_data(driver, section_name):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    contact_section = soup.find("span", string=section_name)
    contact_info_text = "Not available"

    if contact_section:
        print(f"Found this section: {contact_section}")
        # Step 3: Locate the parent div containing the actual contact information
        parent_div = contact_section.find_parent("div")
        if parent_div:
            contact_data_div = parent_div.find_next_sibling("div")
            if contact_data_div:
                contact_info_text = contact_data_div.get_text(strip=True)

    return contact_info_text


def extract_all_text(driver):
    # Load the HTML content
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extract all text and clean it up
    all_text = soup.get_text(separator=" ", strip=True)

    return all_text


def parse_contact_info(raw_text):
    contact_info_text = extract_section_text(raw_text, "Contact info", "Websites and social links")
    social_link_text = extract_section_text(raw_text, "Websites and social links", "Basic info")
    basic_info_text = extract_section_text(raw_text, "Basic info", "Categories")
    categories_info_text = extract_section_text(raw_text, "Categories", "Friends")
    return contact_info_text, social_link_text, basic_info_text, categories_info_text


def extract_section_text(raw_text, start_section, end_section):
    # Normalize spaces and remove non-breaking spaces
    cleaned_text = re.sub(r'\s+', ' ', raw_text.replace("\xa0", " ")).strip()

    # Convert text into a list of words
    words = cleaned_text.split(" ")

    # Tokenize start_section and end_section into separate words
    start_words = start_section.split()
    end_words = end_section.split()

    # Find the start index by checking if all words in start_section appear consecutively
    start_index = next(
        (i for i in range(len(words) - len(start_words) + 1) 
         if words[i:i + len(start_words)] == start_words),
        None
    )

    # Find the end index by checking if all words in end_section appear consecutively
    end_index = next(
        (i for i in range(len(words) - len(end_words) + 1) 
         if words[i:i + len(end_words)] == end_words),
        None
    )

    # Ensure valid indices and extract text between them
    if start_index is not None and end_index is not None and start_index < end_index:
        extracted_text = " ".join(words[start_index + len(start_words):end_index]).strip()
        return extracted_text if extracted_text else "Not available"

    return "Not available"  # Return if section not found

def append_to_csv(profile_data, directory, file_name):
    # Ensure the output directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"📁 Created directory: {directory}")

    file_path = os.path.join(directory, file_name)

    # Define CSV column headers
    fieldnames = [
        "raw_profile_url", "profile_url", "username", "user_id", 
        "contact_info", "social_link", "basic_info", "categories_info"
    ]

    # Check if file exists to determine whether to write headers
    file_exists = os.path.exists(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header if the file is new
        if not file_exists:
            writer.writeheader()

        # Write profile data row
        writer.writerow(profile_data)

    print(f"✅ Profile data appended to {file_path}")

# if __name__ == "__main__":
#     raw_text = """
#     More Posts About Friends Photos Videos Check-ins More Mujeeb Malik About Overview 
#     Work and education Places lived Contact and basic info Family and relationships 
#     Details About Mujeeb Life events Places lived No places to show Friends All friends
#     """

#     # Extract Places Lived (ensuring it's the one after Contact and Basic Info)
#     places_lived_text = extract_section_text_places_lived(raw_text, "Contact and basic info", "Places lived", "Family and relationships")
#     print("Extracted Places Lived:", places_lived_text)