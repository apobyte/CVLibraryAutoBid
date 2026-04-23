from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import time
import json
import zipfile
from getCVLibraryJobLinks import getAllCVLibraryJobsURLs
from applyToJob import applyToJob

EDGE_DRIVER_PATH = "./EdgeDriver/msedgedriver.exe"

# Your proxy credentials
PROXY_HOST = "46.151.227.39"
PROXY_PORT = "43233"
PROXY_USER = "thomasharris"
PROXY_PASS = "C115DED15AD37E34F2A606F8AB79388B"

def createProxyExtension(host, port, user, password):
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxy Auth",
        "permissions": [
            "proxy", "tabs", "unlimitedStorage", "storage",
            "<all_urls>", "webRequest", "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version": "22.0.0"
    }
    """

    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{host}",
                port: parseInt({port})
            }},
            bypassList: ["localhost"]
        }}
    }};

    chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    function callbackFn(details) {{
        return {{
            authCredentials: {{
                username: "{user}",
                password: "{password}"
            }}
        }};
    }}

    chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ["blocking"]
    );
    """

    # Save extension as zip
    with zipfile.ZipFile("proxy_auth.zip", "w") as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return "proxy_auth.zip"

# Create proxy extension
proxy_ext = createProxyExtension(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

options = Options()
options.add_extension(proxy_ext)  # load proxy extension
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0"
)
# Note: removed --disable-extensions since we need extensions for proxy auth

driver = webdriver.Edge(
    service=Service(EDGE_DRIVER_PATH),
    options=options
)

def loadCookies(driver, cookies_file):
    driver.get("https://www.cv-library.co.uk")
    time.sleep(2)
    with open(cookies_file, "r") as f:
        cookies = json.load(f)
    for cookie in cookies:
        cookie.pop("sameSite", None)
        cookie.pop("storeId", None)
        cookie.pop("id", None)
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"  Skipping cookie {cookie.get('name')}: {e}")
    driver.refresh()
    time.sleep(3)
    print("Cookies loaded successfully")

loadCookies(driver, "cookies.json")

job_links = getAllCVLibraryJobsURLs(driver)

with open("job_links.txt", "w") as f:
    for link in job_links:
        f.write(link + "\n")
print("Saved job links to job_links.txt")

# for i, link in enumerate(job_links, 1):
#     print(f"\n--- Job {i}/{len(job_links)} ---")
#     applyToJob(driver, link)
#     time.sleep(2)

# driver.quit()
# print("\nDone! All applications submitted.")