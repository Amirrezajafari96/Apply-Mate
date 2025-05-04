# ✅ STEP 1: Import packages
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# ✅ STEP 2: Set up ChromeDriver path and options
service = Service('C:/Users/Student/.wdm/drivers/chromedriver/win64/135.0.7049.115/chromedriver-win64/chromedriver.exe')
options = Options()
options.add_argument("--disable-webrtc")

# ✅ STEP 3: Launch browser
driver = webdriver.Chrome(service=service, options=options)

# ✅ STEP 4: Login to LinkedIn
driver.get("https://www.linkedin.com/checkpoint/rm/sign-in-another-account")
username_field = driver.find_element(By.ID, "username")
password_field = driver.find_element(By.ID, "password")

username_field.send_keys("mygermanapply@gmail.com")
password_field.send_keys("969899100")

login_button = driver.find_element(By.XPATH, '//button[@aria-label="Sign in"]')
login_button.click()

# Wait for login to complete
time.sleep(5)
try:
    WebDriverWait(driver, 10).until(EC.url_contains("feed"))
    print("Login Successful!")
except:
    print("Login Failed!")

# ✅ STEP 5: Load job links from CSV
df = pd.read_csv("jobs_hannover_braunschweig.csv")
links = df["Link"].dropna().tolist()

job_descriptions = []

# ✅ STEP 6: Scrape job description from each link
for idx, link in enumerate(links):
    try:
        driver.get(link)
        time.sleep(5)
        # ✅ Step: Close LinkedIn pop-up if it shows up
        try:
            connect_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Yes, keep all connected")]'))
            )
            connect_button.click()
            print("Dismissed 'Keep services connected' popup.")
            time.sleep(2)
        except:
            pass  # Pop-up didn't appear; continue normally

        # ✅ Step: Scrape job description
        description_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "description__text"))
        )

        job_text = description_element.text
        job_descriptions.append(job_text)
        print(f"[{idx+1}/{len(links)}] Scraped successfully.")
    except Exception as e:
        job_descriptions.append("N/A")
        print(f"[{idx+1}/{len(links)}] Failed to scrape: {e}")

# ✅ STEP 7: Save to new CSV
df["Job Description"] = job_descriptions
df.to_csv("scraped_job_ads.csv", index=False)
print("Saved to scraped_job_ads.csv")

# ✅ Optional: Close browser
# driver.quit()
