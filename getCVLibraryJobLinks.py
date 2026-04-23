from selenium.webdriver.common.by import By
import time

def getAllCVLibraryJobsURLs(driver):
    URL = "https://www.cv-library.co.uk/remote-software-developer-jobs?distance=750&perpage=100&posted=7&us=1"

    print("Scraping job listings...")
    driver.get(URL)
    time.sleep(3)

    all_links = []
    for a in driver.find_elements(By.TAG_NAME, "a"):
        href = a.get_attribute("href")
        if href and "/job/" in href and href not in all_links:
            all_links.append(href)

    all_links = all_links[:5]  # get first 5 only

    all_links = ["https://www.cv-library.co.uk/job/224998408/Software-Developer?hlkw=software-developer&sid=34ab695f-bc21-4708-bf00-2f2ad30b4497"]
    print(f"Found {len(all_links)} job links")
    return all_links