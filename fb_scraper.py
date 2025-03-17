import time
import csv
import random
import logging
from turtle import pos
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import json 
from helper import load_json, extract_group_name, add_urls_to_json, get_expected_url, get_facebook_html, extract_facebook_username_id, extract_all_text, parse_contact_info, append_to_csv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FaceookScrapper:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        logger.info("Facebook Scraper initialized successfully")

    def is_private_group(self, driver, url):
        try:
            wait = WebDriverWait(driver, 5)

            # Locate the "Private group" label
            private_group_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Private group')]"))
            )

            if private_group_element:
                print(f"URL: {url}, Private group detected. Skipping...")
                return True

        except Exception as e:
            print(f"URL: {url}, Public group detected. Proceeding...")

        return False  # If "Private group" text is not found, assume it's public
    
    def extract_members_from_groups(self, driver, group_dir, group_file, max_members=50000, max_retries=5, output_directoy=None):
        group_path = f"{group_dir}/{group_file}"
        group_urls = load_json(group_path)

        # Iterate through the group urls we extrated ealier
        for group_url in group_urls:
            # Visit the group url page 
            driver.get(group_url)
            time.sleep(3)
            
            # Check if the gorup is private. If private, we can't do anything with it
            if self.is_private_group(driver, group_url):
                continue
            
            # Now, if it a public group, we can visit the members tab
            members_url = f"{group_url}/members"
            driver.get(members_url)
            time.sleep(5)
            print(f"📌 Extracting members from: {members_url}")
            
            members_list = set()  # We initilize an empty list to store all the members in this group
            last_count = 0
            retry_count = 0
            scroll_attempts = 0

            while len(members_list) < max_members:
                scroll_attempts += 1
                print(f"🔄 Scrolling attempt {scroll_attempts}...")

                member_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/') and contains(@href, '/user/')]")
                for element in member_elements:
                    profile_url = element.get_attribute("href")

                    # Clean up profile URLs (remove tracking parameters)
                    profile_url = profile_url.split("?")[0]
                    members_list.add(profile_url)

                print(f"✅ Extracted {len(members_list)} members so far.")

                # Stop scrolling if no new members are loaded
                if len(members_list) == last_count:
                    retry_count += 1
                    print(f"No new members found. Retry {retry_count}/{max_retries}...")
                    if retry_count >= max_retries:
                        print("🚫 Stopping due to repeated failures.")
                        break
                    time.sleep(3)
                else:
                    retry_count = 0  # Reset retry counter

                last_count = len(members_list)

                # Scroll to load more members
                scroll_step = random.randint(800, 1200) 
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                time.sleep(random.uniform(2, 4))  # Mimic human scrolling

            group_name = extract_group_name(group_url=group_url)
            add_urls_to_json(list(members_list), output_dir=output_directoy, output_file=group_name)
            logger.info(f"Members urls saved for group: {group_name}")
        

    def extract_member_profiles(self, member_directory, output_directory, output_filename):
        """
        Extracts Facebook member profile details.
        
        Args:
            member_directory: Directory containing JSON files with member profile URLs.
            output_directory: Directory to store the extracted profile data.
        """
        member_files = [f for f in os.listdir(member_directory) if f.endswith(".json")]
        for member_file in member_files:
            member_file_path = os.path.join(member_directory, member_file)
            with open(member_file_path, "r") as f:
                member_urls = json.load(f)

            for member_url in member_urls:
                self.driver.get(member_url)
                time.sleep(5)  # Allow page to load

                print(f"📌 Scraping profile: {member_url}")

                # Step 1: Click "View Profile" Button
                try:
                    view_profile_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='View profile']"))
                    )
                    raw_profile_url = view_profile_button.get_attribute("href")
                    self.driver.get(raw_profile_url)
                    time.sleep(5)  # Wait for profile to load
                    print(f"✅ Navigated to raw Profile: {raw_profile_url}")
                except Exception as e:
                    print(f"❌ Unable to click 'View Profile': {e}")
                    continue  # Skip to the next user if failed

                profile_data = {"raw_profile_url": raw_profile_url, "username": None, "user_id": None}
                # 3/15/2025/ 7:00 pm. It works uptil here. 

                current_url = self.driver.current_url
                profile_data["profile_url"] = current_url
                logger.info(f"Current url: {current_url}")

                # Fetch profile HTML
                html_content = get_facebook_html(self.driver, current_url)
                if html_content:
                    user_id, username = extract_facebook_username_id(html_content)
                    if username:
                        print(f"🔹 Extracted Username: {username}, ID: {user_id}")
                        profile_data["username"] = username
                        profile_data["user_id"] = user_id
                    else:
                        print("❌ Username not found.")
                else:
                    print("❌ Failed to retrieve profile page.")

                # Profile information
                case, expected_base_url = get_expected_url(current_url)
                if case == 1:
                    overview = f"{expected_base_url}about"
                    work_and_education = f"{current_url}about_work_and_education"
                    place_lived = f"{expected_base_url}about_places"
                    contact = f"{expected_base_url}about_contact_and_basic_info"
                else:
                    overview = f"{expected_base_url}about"
                    work_and_education = f"{expected_base_url}about_work_and_education"
                    place_lived = f"{expected_base_url}about_places"
                    contact = f"{expected_base_url}about_contact_and_basic_info"
                    

                logger.info(f"overview: {overview}")
                logger.info(f"work_and_education: {work_and_education}")
                logger.info(f"place_lived: {place_lived}")
                logger.info(f"contact: {contact}")

                # Navigate driver to the contact page
                self.driver.get(contact)
                contact_raw_info = extract_all_text(self.driver) # From contact page, extract infomation
                contact_info_text, social_link_text, basic_info_text, categories_info_text = parse_contact_info(contact_raw_info)

                logger.info(f"Contact Info: {contact_info_text}")
                logger.info(f"Social Link: {social_link_text}")
                logger.info(f"Basic Info: {basic_info_text}")
                logger.info(f"Categories Info: {categories_info_text}")

                profile_data["contact_info"] = contact_info_text
                profile_data["social_link"] = social_link_text
                profile_data["basic_info"] = basic_info_text
                profile_data["categories_info"] = categories_info_text

                logger.info(f"Current Profile:/n {profile_data}")

                # Append this user's profile data to our csv
                append_to_csv(profile_data, output_directory, output_filename)









            

            

            





    