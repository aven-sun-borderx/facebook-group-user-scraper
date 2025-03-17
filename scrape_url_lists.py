import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def random_delay(min_time=1, max_time=3):
    """Introduce a random delay to mimic human behavior."""
    time.sleep(random.uniform(min_time, max_time))

def get_facebook_group_urls(driver, max_groups=2000, batch_size=10, retry_delay=2, max_retries=5):
    """
    Scrolls the full page to load more Facebook group search results and extracts group URLs.

    Args:
        driver: Selenium WebDriver instance.
        max_groups: Maximum number of groups to scrape.
        batch_size: Number of groups to scrape before pausing.
        retry_delay: Delay before retrying when no new groups are found.
        max_retries: Maximum number of retries when no new groups load.

    Returns:
        List of unique group URLs.
    """
    try:
        wait = WebDriverWait(driver, 10)

        group_urls = set()
        last_count = 0
        retry_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 5  # Allow multiple scrolls before considering a refresh

        while len(group_urls) < max_groups:
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            current_scroll_position = 0

            # Find initial number of group links
            group_links_before = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/')]")
            num_links_before = len(group_links_before)

            # Scroll multiple times before deciding to refresh
            while scroll_attempts < max_scroll_attempts:
                scroll_step = random.randint(800, 1200)  # Mimic a human scroll
                current_scroll_position += scroll_step
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                print(f"Scrolled {scroll_step}px down the page.")

                random_delay(1, 2)

                # Check for new group links
                group_links_after = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/')]")
                num_links_after = len(group_links_after)

                if num_links_after > num_links_before:
                    print(f"New content loaded: {num_links_after - num_links_before} new groups found.")
                    break  # Exit scrolling loop if new content appears

                scroll_attempts += 1  # Increment scroll attempts

            # Extract group links
            group_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/groups/')]")
            for link in group_links:
                url = link.get_attribute("href")
                if url and "/groups/" in url:
                    group_urls.add(url)

            print(f"Scraped {len(group_urls)} groups so far.")

            # Reset scroll attempts for next batch
            scroll_attempts = 0

            # Check if no new groups were found after multiple scrolls
            if len(group_urls) == last_count:
                retry_count += 1
                print(f"No new groups found. Attempt {retry_count}/{max_retries}. Waiting for {retry_delay} seconds...")
                random_delay(retry_delay, retry_delay + 3)

                if retry_count >= max_retries:
                    print("Maximum retries reached. Stopping scraping.")
                    break
            else:
                last_count = len(group_urls)
                retry_count = 0  # Reset retry counter when new groups are found

            # Pause after scraping a batch
            if len(group_urls) % batch_size == 0:
                print("Pausing briefly to avoid detection...")
                random_delay(5, 10)

        print(f"Extracted {len(group_urls)} group URLs after scrolling.")
        return list(group_urls)

    except Exception as e:
        print(f"Error extracting group URLs: {e}")
        return []
