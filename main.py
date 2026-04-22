from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
import json
from getCVLibraryJobLinks import getAllCVLibraryJobsURLs
from applyToJob import applyToJob

EDGE_DRIVER_PATH = "./EdgeDriver/msedgedriver.exe"

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0"
)

driver = webdriver.Edge(
    service=Service(EDGE_DRIVER_PATH),
    options=options
)

# Load cookies from file
def loadCookies(driver, cookies_file):
    # Must visit the domain first before adding cookies
    driver.get("https://www.cv-library.co.uk")
    time.sleep(2)

    with open(cookies_file, "r") as f:
        cookies = json.load(f)

    for cookie in cookies:
        # Remove keys that cause issues
        cookie.pop("sameSite", None)
        cookie.pop("storeId", None)
        cookie.pop("id", None)
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"  Skipping cookie {cookie.get('name')}: {e}")

    # Refresh to apply cookies
    driver.refresh()
    time.sleep(3)
    print("Cookies loaded successfully")

loadCookies(driver, "cookies.json")

# Get all job links
job_links = getAllCVLibraryJobsURLs(driver)

with open("job_links.txt", "w") as f:
    for link in job_links:
        f.write(link + "\n")
print("Saved job links to job_links.txt")

# Apply to each job
for i, link in enumerate(job_links, 1):
    print(f"\n--- Job {i}/{len(job_links)} ---")
    applyToJob(driver, link)
    time.sleep(2)

driver.quit()
print("\nDone! All applications submitted.")