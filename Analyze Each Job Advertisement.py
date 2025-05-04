# ─── STEP 1: Import required libraries ──────────────────────────────────────────
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import pandas as pd
import time

# ─── STEP 2: Configure ChromeDriver ─────────────────────────────────────────────
service = Service(
    'C:/Users/Student/.wdm/drivers/chromedriver/win64/135.0.7049.115/chromedriver-win64/chromedriver.exe'
)
options = Options()
options.add_argument("--disable-webrtc")

# ─── STEP 3: Launch browser ────────────────────────────────────────────────────
driver = webdriver.Chrome(service=service, options=options)

# ─── STEP 4: Log in to LinkedIn ─────────────────────────────────────────────────
driver.get("https://www.linkedin.com/checkpoint/rm/sign-in-another-account")
driver.find_element(By.ID, "username").send_keys("mygermanapply@gmail.com")  # 4.1 enter username
driver.find_element(By.ID, "password").send_keys("969899100")                # 4.1 enter password
driver.find_element(By.XPATH, '//button[@aria-label="Sign in"]').click()     # 4.2 click Sign in
time.sleep(5)                                                                 # 4.3 wait for feed
try:
    WebDriverWait(driver, 10).until(EC.url_contains("feed"))
    print("✅ Login successful")
except TimeoutException:
    print("❌ Login failed")

# ─── STEP 5: Load job links from CSV ────────────────────────────────────────────
df = pd.read_csv("jobs_hannover_braunschweig.csv")
links = df["Link"].dropna().tolist()
job_descriptions = []

# ─── STEP 6: Iterate over each job link ─────────────────────────────────────────
for idx, link in enumerate(links, start=1):
    try:
        # 6.1 Navigate to the job posting
        driver.get(link)
        time.sleep(5)

        # 6.2 Dismiss "Keep services connected" popup if it appears
        try:
            popup = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                    '//button[contains(text(),"Yes, keep all connected")]'
                ))
            )
            popup.click()
            print(f"[{idx}] Dismissed popup")
            time.sleep(2)
        except TimeoutException:
            pass  # popup did not show

        # 6.3 Expand the full description by clicking "See more"
        try:
            span = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//span[contains(@class,'artdeco-button__text') and normalize-space(.)='See more']"
                ))
            )
            btn = span.find_element(By.XPATH, "./ancestor::button[1]")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
            time.sleep(0.5)
            try:
                btn.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
            print(f"[{idx}] Clicked 'See more'")
        except TimeoutException:
            pass  # no “See more” button

        # 6.4 Scrape the job description text
        try:
            desc = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                    "div.show-more-less-html__markup, div.jobs-description__content, section.jobs-description__job-description > div"
                ))
            )
            job_descriptions.append(desc.text)
            print(f"[{idx}/{len(links)}] Description scraped ({len(desc.text)} chars)")
        except TimeoutException:
            print(f"[{idx}] ⚠️ Description not found")
            job_descriptions.append("N/A")

    except Exception as e:
        # <-- This except closes the outer try for the loop
        job_descriptions.append("N/A")
        print(f"[{idx}/{len(links)}] Failed to scrape link: {e}")

# ─── STEP 7: Save results to CSV ────────────────────────────────────────────────
df["Job Description"] = job_descriptions
df.to_csv("scraped_job_ads.csv", index=False)
print("✅ Saved to scraped_job_ads.csv")

# ─── STEP 8 (Optional): Close browser ──────────────────────────────────────────
# driver.quit()
