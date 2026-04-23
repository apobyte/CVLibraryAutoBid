from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from openai import OpenAI
import time
import os
import re
from dotenv import load_dotenv

COVER_LETTER = """I am excited to apply for this software developer role. I have strong experience in 
full-stack development and am eager to contribute to your team.

Please find my CV attached for your consideration.

Kind regards,
Benjamin Davies"""

RESUMES_BASE_PATH = "C:/Resumes"

# Load .env file
load_dotenv(override=True)

# Get the API key from environment
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

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
    cv_path = os.path.join(RESUMES_BASE_PATH, safe_name, "BenjaminDavies.pdf")
    if not os.path.exists(cv_path):
        print(f"  Warning: CV not found at {cv_path}, using default CV")
        cv_path = os.path.join(RESUMES_BASE_PATH, "default", "BenjaminDavies.pdf")
    return cv_path

def answerAllQuestionsWithAI(questions):
    """Send all questions to OpenAI at once for better context."""
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

    prompt = f"""You are helping someone apply for a remote software developer job in the UK.
Answer each yes/no question below. Reply ONLY with a JSON array of answers like: ["yes", "no", "yes"]

Rules:
- If asked about technical experience, respond with = yes
- If asked about commuting, respond with = no (I am seeking a fully remote position and am unable to commute.)
- If asked about legal qualifications to work, respond with = yes (I am legally qualified to work in the UK)

Questions:
{questions_text}

Reply with ONLY a JSON array, nothing else. Example: ["yes", "no", "yes"]"""

    print(f"Sending to AI:\n{questions_text}")  # debug: confirm questions are sent

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],  # prompt contains all questions
        max_tokens=50
    )

    import json
    raw = response.choices[0].message.content.strip()
    print(f"  AI raw response: {raw}")  # debug: see what AI returned
    answers = json.loads(raw)
    return [a.lower() for a in answers]

def answerApplicationQuestions(driver):
    try:
        questions_section = driver.find_elements(By.CSS_SELECTOR, "section.apply__questions")
        if not questions_section:
            print("  No application questions found")
            return

        print("  Found application questions, answering with AI...")

        fieldsets = driver.find_elements(By.CSS_SELECTOR, "section.apply__questions fieldset")
        if not fieldsets:
            return

        # Collect all questions first
        questions = []
        for fieldset in fieldsets:
            try:
                legend = fieldset.find_element(By.TAG_NAME, "legend")
                questions.append(legend.text.strip())
            except:
                questions.append("unknown question")

        print(f"  Total questions found: {len(questions)}")

        # Send ALL questions to AI in one call
        answers = answerAllQuestionsWithAI(questions)
        print(f"  AI Answers: {answers}")

        # Click the correct radio for each question
        for i, (fieldset, answer) in enumerate(zip(fieldsets, answers)):
            try:
                if answer not in ["yes", "no"]:
                    answer = "yes"  # fallback

                radio = fieldset.find_element(
                    By.CSS_SELECTOR, f"input[type='radio'][value='{answer}']"
                )
                radio.click()
                time.sleep(0.5)
                print(f"  Q{i+1}: '{questions[i]}' → {answer}")

            except Exception as e:
                print(f"  Could not answer question {i+1}: {e}")

    except Exception as e:
        print(f"  Error answering questions: {e}")

def applyToJob(driver, job_url):
    print(f"\nOpening: {job_url}")
    driver.get(job_url)
    time.sleep(3)

    try:
        wait = WebDriverWait(driver, 10)

        # Click "Apply Now" button first
        try:
            apply_now_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-standard-apply]"))
            )
            apply_now_btn.click()
            time.sleep(3)
            print("  Clicked 'Apply Now'")
        except:
            print("  Could not find Apply Now button, skipping")

        # Get company name and build CV path
        company_name = getCompanyName(driver)
        if company_name:
            print(f"  Company: {company_name}")
            cv_path = getCVPath(company_name)
        else:
            print("  Could not detect company name, using default CV")
            cv_path = os.path.join(RESUMES_BASE_PATH, "default", "BenjaminDavies.pdf")

        print(f"  Using CV: {cv_path}")

        # Answer application questions with AI
        answerApplicationQuestions(driver)

        # Fill cover letter
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
                EC.element_to_be_clickable((By.XPATH, "//button[@data-toggle and .//span[contains(text(), 'Attach a different CV')]]"))
            )
            attach_cv_btn.click()
            time.sleep(2)
            print("  Clicked 'Attach a different CV'")
        except:
            print("  Could not find 'Attach a different CV' button, skipping")

        # Upload CV
        try:
            file_input = wait.until(
                EC.presence_of_element_located((By.ID, "doc"))
            )
            file_input.send_keys(cv_path)
            time.sleep(2)
            print("  CV uploaded")
        except:
            print("  Could not upload CV, skipping")

        # Click Send Application
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