# Facebook Scraper

## Overview
The Facebook Scraper is a Python-based web scraping tool that automates the process of extracting data from Facebook. It uses Selenium for automated browsing and BeautifulSoup for HTML parsing. The scraper collects information from Facebook groups and member profiles, storing the extracted data in structured formats.

## Features
- **Login Automation**: Uses undetected Selenium to log into Facebook.
- **Group URL Scraping**: Extracts URLs of groups based on search queries.
- **Member Extraction**: Extracts member profile URLs from public groups.
- **Profile Scraping**: Collects data from user profiles, including basic info, contact info, and social links.
- **Data Storage**: Stores extracted data in JSON and CSV formats.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Selenium
- BeautifulSoup4
- Undetected ChromeDriver
- WebDriver Manager

### Setup
1. Clone this repository:
   ```sh
   git clone https://github.com/your-repo/facebook-scraper.git
   cd facebook-scraper
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Configure the `.env` file with your Facebook login credentials:
   ```env
   FB_ACCOUNT=your_email
   FB_PASSWORD=your_password
   ```

## 📌 **Pipeline Overview**
1. **login** 
   - Uses Selenium to navigate to Facebook and log in with provided credentials.
   - Need to handle captcha manually!!!
2. **Extract Groups from Search Terms**
   - The scraper takes a search term (e.g., "crypto") and finds public Facebook groups matching that term.
   - Each search term generates a JSON file in `group_url_lists/`.

3. **Extract Members from Groups**
   - Each group found in `group_url_lists/{search_term}.json` is processed to extract member profile URLs.
   - Members are stored in `member_urls_lists/{search_term}/{group_id}.json`.

4. **Scrape Member Profiles**
   - Each member’s profile is visited, and data such as name, user ID, work history, location, and contact information is extracted.
   - The final structured data is stored in `output/FB_scrape_{search_term}_YYYYMMDD_HHMMSS.csv`.

---

## 📂 **Project Structure**

```
📁 group_urls_lists/
│   ├── crypto.json              # JSON file with group URLs for search term "crypto"
│   ├── forex.json               # JSON file with group URLs for search term "forex"
│   ├── ...                      # One file per search term
│
📁 member_urls_lists/{search_term}/
│   ├── {group_id}.json          # Each file contains member profile URLs of a specific group
│   ├── {another_group}.json     # Each group has its own JSON file with members
│
📁 output/
│   ├── FB_scrape_crypto_YYYYMMDD_HHMMSS.csv   # Final extracted profile data for "crypto" search term
│   ├── FB_scrape_forex_YYYYMMDD_HHMMSS.csv    # Final extracted profile data for "forex"
│
📁 venv/                         # Virtual environment
├── .env                         # Environment variables (credentials, settings)
├── fb_scraper.py                 # Main scraper logic
├── helper.py                     # Utility functions
├── login.py                      # Handles Facebook login
├── main.py                       # Orchestrates the scraping process
├── requirements.txt               # Dependencies
├── scrape_url_lists.py            # Handles scraping of group and member URLs
```

---

## 📝 **Output Structure**

### **1️⃣ `group_urls_lists/{search_term}.json`**
Each search term generates a JSON file containing a list of group URLs.

```json
[
    "https://www.facebook.com/groups/281416320243934",
    "https://www.facebook.com/groups/297520669266164",
    ...
]
```

---

### **2️⃣ `member_urls_lists/{search_term}/{group_id}.json`**
Each group has a JSON file with its members.

```json
[
    "https://www.facebook.com/groups/281416320243934/user/100015078106826",
    "https://www.facebook.com/groups/281416320243934/user/100078153108794",
    ...
]
```

---

### **3️⃣ `output/FB_scrape_{search_term}_YYYYMMDD_HHMMSS.csv`**
Final structured CSV file containing scraped profile data.

| Profile URL | Name | User ID | Contact Info | Work & Education | Places Lived | Social Links | Categories |
|------------|------|---------|--------------|-------------------|--------------|--------------|------------|
| https://www.facebook.com/profile.php?id=100015078106826 | John Doe | 100015078106826 | johndoe@gmail.com | Engineer at XYZ | New York | Twitter: @johndoe | Digital Creator |
| https://www.facebook.com/jane.smith | Jane Smith | jane.smith | Not Available | Marketing at ABC | Los Angeles | Not Available | Business Owner |

---

## ⚙️ **How to Run the Scraper**

### **1️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2️⃣ Set Up `.env` File**
- Copy `.env.example` to `.env`
- Add Facebook credentials (`FB_EMAIL`, `FB_PASSWORD`)

### **3️⃣ Run the Scraper**
```bash
python main.py
```

---

## 🚀 **Future Improvements**
- Handle private groups more effectively.
- Improve CAPTCHA-solving capabilities.
- Optimize scraping speed and error handling.

---

Let me know if you need any modifications! 🚀
Aven Sun: aven@borderxai.com

