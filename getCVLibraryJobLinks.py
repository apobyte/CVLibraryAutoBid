from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import math

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

    all_links = []

    for page in range(1, total_pages + 1):
        url = f"{BASE_URL}&page={page}"
        print(f"Scraping page {page}/{total_pages}...")
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.job__title")))

        found = 0
        for a in driver.find_elements(By.CSS_SELECTOR, "h2.job__title a"):
            href = a.get_attribute("href")
            if href and href not in all_links:
                all_links.append(href)
                found += 1

        print(f"  Found {found} jobs on page {page}")

        if found == 0:
            print("No jobs found on this page, stopping.")
            break

    print(f"Total job links collected: {len(all_links)}")
    return all_links