import logging
import time
from dotenv import load_dotenv
import os
from helper import get_chrome_driver, search_query, click_groups_tab, append_urls_to_json
from login import login_facebook
from scrape_url_lists import get_facebook_group_urls
from fb_scraper import FaceookScrapper

load_dotenv(dotenv_path=".env") 
FB_ACCOUNT = os.getenv("FB_ACCOUNT")
FB_PASSWORD = os.getenv("FB_PASSWORD")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Email: {FB_ACCOUNT}, Password: {FB_PASSWORD}")

if __name__ == "__main__":
    try:
        logger.info("Starting Facebook Scraper")
        
        # Get user input
        user_input = input("Enter the Term you want to scrape: ").strip()
        output_directoy = "output"
        output_file = f"FB_scrape_{user_input}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
        group_urls_output_file = f"{user_input}.json"
        group_urls_directory = f"group_urls_lists"
        members_urls_directory = f"member_urls_lists/{user_input}"

        logger.info("Trying to login...")
        driver = get_chrome_driver()

        # Login to Tiktok
        login_facebook(driver, FB_ACCOUNT, FB_PASSWORD)
        print(f"Logged in successfully!")

        # Perform searching
        search_query(driver, user_input)

        # Click on "Groups" tab
        click_groups_tab(driver=driver)

        # Start by sraping the group url list
        group_urls = get_facebook_group_urls(
            driver=driver
        )

        # Append the URLs to the JSON file
        append_urls_to_json(group_urls, group_urls_directory, group_urls_output_file)
        
        # Initialize scraper
        scraper = FaceookScrapper(driver=driver)

        # Scrape members urls from each group and save them
        scraper.extract_members_from_groups(driver=driver, group_dir=group_urls_directory, group_file=group_urls_output_file, output_directoy=members_urls_directory)

        # Scrape each member's profile from the saved files and save to a csv
        scraper.extract_member_profiles(member_directory=members_urls_directory, output_directory=output_directoy, output_filename=output_file)
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        
    finally:
        if 'scraper' in locals():
            scraper.close_driver()