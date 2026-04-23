import requests
import os

def downloadResume(url, company_title, name):
    directory = f"C:/Resumes/{company_title}"

    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Define file path
    file_path = os.path.join(directory, f"{name}.pdf")

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)

        if response.status_code == 200:
            with open(file_path, "wb") as file:
                file.write(response.content)
            print(f"File saved to {file_path}")
            return file_path
        else:
            print(f"Failed to download. Status code: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return None


# Usage
url = "http://45.15.160.247:5000/job/description/Joshua_Ryan/Cathcart_Technology/Joshua%20Ryan%20Cathcart%20Technology.pdf"
company_title = "Cathcart_Technology"
name = "Joshua_Ryan"

downloadResume(url, company_title, name)