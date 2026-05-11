from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import math
import requests
import os

# Bid Platform User Info
user_email = "joshua.ryan.uk@outlook.com"
user_days = 30

def getAppliedCompanyNames(email, days):
    server_url = os.getenv("BIT_PLATFORM_SERVER_URL")

    response = requests.get(
        f"{server_url}/api/bids/get-companies-by-days",
        params={
            "email": email,
            "days": days
        }
    )
    return response.json()

def getAllCVLibraryJobsURLs(driver):
    BASE_URL = "https://www.cv-library.co.uk/remote-software-engineer-jobs?distance=750&perpage=100&posted=7&us=1"

    print("Scraping job listings...")
    driver.get(BASE_URL)

    # Wait for the results header to appear
    total_jobs = 0
    try:
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.search-header__results")))

        b_tags = driver.find_elements(By.CSS_SELECTOR, "p.search-header__results b")
        print(f"  Found {len(b_tags)} <b> tags: {[b.text for b in b_tags]}")  # debug

        # "of 185" text is in the paragraph, extract it
        result_p = driver.find_element(By.CSS_SELECTOR, "p.search-header__results")
        full_text = result_p.text  # e.g. "Displaying 1-100 of 185 jobs"
        print(f"  Result text: {full_text}")  # debug

        total_jobs = int(full_text.split("of")[1].strip().split()[0].replace(",", ""))
        print(f"Total jobs found: {total_jobs}")
    except Exception as e:
        print(f"Could not get total job count: {e}, scraping first page only")

    total_pages = max(1, math.ceil(total_jobs / 100))
    print(f"Total pages to scrape: {total_pages}")

    all_links = set()

    applied_company_names = getAppliedCompanyNames(user_email, user_days)
    print(f"Total applied company names: {applied_company_names}")

    for page in range(1, total_pages + 1):
        url = f"{BASE_URL}&page={page}"
        print(f"Scraping page {page}/{total_pages}...")
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.job__main")))

        found = 0
        for job_main in driver.find_elements(By.CSS_SELECTOR, "div.job__main"):
            try:
                company_name = job_main.find_element(By.CSS_SELECTOR, "a.job__company-link").text
                href = job_main.find_element(By.CSS_SELECTOR, "h2.job__title a").get_attribute("href")
                if company_name and company_name not in applied_company_names:
                    if href and href not in all_links:
                        all_links.add(href)
                        found += 1
            except Exception as e:
                print(f"Skipping job card: {e}")

        print(f"  Found {found} jobs on page {page}")

        if found == 0:
            print("No jobs found on this page, stopping.")
            break

    print(f"Total job links collected: {len(all_links)}")
    return all_links