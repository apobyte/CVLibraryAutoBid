from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import re

COVER_LETTER = """I am excited to apply for this software developer role. I have strong experience in 
full-stack development and am eager to contribute to your team.

Please find my CV attached for your consideration.

Kind regards,
[Your Name]"""

RESUMES_BASE_PATH = "C:/Resumes"

def getCompanyName(driver):
    try:
        company_span = driver.find_element(By.CSS_SELECTOR, "span[data-jd-company]")
        company_link = company_span.find_element(By.TAG_NAME, "a")
        name = company_link.text.strip()
        if name:
            return name
    except:
        pass
    return None

def sanitizeFolderName(name):
    return re.sub(r'[<>:"/\\|?*]', '', name).strip()

def getCVPath(company_name):
    safe_name = sanitizeFolderName(company_name)
    cv_path = os.path.join(RESUMES_BASE_PATH, safe_name, "resume.pdf")
    if not os.path.exists(cv_path):
        print(f"  Warning: CV not found at {cv_path}, using default CV")
        cv_path = os.path.join(RESUMES_BASE_PATH, "default", "resume.pdf")
    return cv_path

def applyToJob(driver, job_url):
    print(f"\nOpening: {job_url}")
    driver.get(job_url)
    time.sleep(3)

    try:
        wait = WebDriverWait(driver, 10)

        # Get company name and build CV path
        company_name = getCompanyName(driver)
        if company_name:
            print(f"  Company: {company_name}")
            cv_path = getCVPath(company_name)
        else:
            print("  Could not detect company name, using default CV")
            cv_path = os.path.join(RESUMES_BASE_PATH, "default", "resume.pdf")

        print(f"  Using CV: {cv_path}")

        # Fill cover letter using exact textarea id
        try:
            cover_letter_field = wait.until(
                EC.presence_of_element_located((By.ID, "cover-letter"))
            )
            cover_letter_field.clear()
            cover_letter_field.send_keys(COVER_LETTER)
            print("  Cover letter filled")
        except:
            print("  No cover letter field found, skipping")

        # Click "Attach a different CV" button
        try:
            attach_cv_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Attach a different CV')]"))
            )
            attach_cv_btn.click()
            time.sleep(2)
            print("  Clicked 'Attach a different CV'")
        except:
            print("  Could not find 'Attach a different CV' button, skipping")

        # Upload CV using exact input id
        try:
            file_input = wait.until(
                EC.presence_of_element_located((By.ID, "doc"))
            )
            file_input.send_keys(cv_path)
            time.sleep(2)
            print("  CV uploaded")
        except:
            print("  Could not upload CV, skipping")

        # Click Send Application using exact attribute
        try:
            send_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-send-application]"))
            )
            send_btn.click()
            time.sleep(3)
            print("  Application sent!")
        except:
            print("  Could not find Send Application button")

    except Exception as e:
        print(f"  Error on {job_url}: {e}")