# تعریف کتابخانه‌های مورد نیاز
import requests
from bs4 import BeautifulSoup
import pandas as pd

# تعریف پارامترهای جستجو
keywords = ["werkstudent", "data"]
locations = ["Hannover", "Braunschweig"]

# لینک‌های اصلی برای LinkedIn و Indeed
linkedin_urls = [f"https://www.linkedin.com/jobs/search/?keywords={'%20'.join(keywords)}&location={location}" for location in locations]
indeed_urls = [f"https://de.indeed.com/jobs?q={'+'.join(keywords)}&l={location}" for location in locations]

# تابع برای استخراج اطلاعات از LinkedIn
def scrape_linkedin(url):
    headers = {"User-Agent": "Mozilla/5.0"}  # تنظیم هدر برای جلوگیری از بلاک شدن
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    jobs = []
    for job_card in soup.select(".base-card"):
        title = job_card.select_one(".base-card__title").text.strip() if job_card.select_one(".base-card__title") else "N/A"
        company = job_card.select_one(".base-card__subtitle").text.strip() if job_card.select_one(".base-card__subtitle") else "N/A"
        location = job_card.select_one(".job-search-card__location").text.strip() if job_card.select_one(".job-search-card__location") else "N/A"
        link = job_card.select_one("a")["href"] if job_card.select_one("a") else "N/A"
        jobs.append({"Title": title, "Company": company, "Location": location, "Link": link})

    return jobs

# تابع برای استخراج اطلاعات از Indeed
def scrape_indeed(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    jobs = []
    for job_card in soup.select(".job_seen_beacon"):
        title = job_card.select_one("h2.jobTitle span").text.strip() if job_card.select_one("h2.jobTitle span") else "N/A"
        company = job_card.select_one(".companyName").text.strip() if job_card.select_one(".companyName") else "N/A"
        location = job_card.select_one(".companyLocation").text.strip() if job_card.select_one(".companyLocation") else "N/A"
        link = "https://de.indeed.com" + job_card.select_one("a")["href"] if job_card.select_one("a") else "N/A"
        jobs.append({"Title": title, "Company": company, "Location": location, "Link": link})

    return jobs

# استخراج اطلاعات از LinkedIn و Indeed
linkedin_jobs = []
indeed_jobs = []
hannover_jobs = []
braunschweig_jobs = []

for i, location in enumerate(locations):
    linkedin_jobs_temp = scrape_linkedin(linkedin_urls[i])
    indeed_jobs_temp = scrape_indeed(indeed_urls[i])
    
    if location == "Hannover":
        hannover_jobs.extend(linkedin_jobs_temp + indeed_jobs_temp)
    elif location == "Braunschweig":
        braunschweig_jobs.extend(linkedin_jobs_temp + indeed_jobs_temp)

    linkedin_jobs.extend(linkedin_jobs_temp)
    indeed_jobs.extend(indeed_jobs_temp)

# ترکیب نتایج و ذخیره در فایل CSV
all_jobs = linkedin_jobs + indeed_jobs
jobs_df = pd.DataFrame(all_jobs)

# ذخیره در فایل CSV
jobs_df.to_csv("jobs_hannover_braunschweig.csv", index=False)

# شمارش تعداد فرصت‌های شغلی
hannover_count = len(hannover_jobs)
braunschweig_count = len(braunschweig_jobs)
job_count = len(all_jobs)

print(f"Data extraction completed. {hannover_count} job opportunities found in Hannover.")
print(f"{braunschweig_count} job opportunities found in Braunschweig.")
print(f"A total of {job_count} job opportunities found and saved in 'jobs_hannover_braunschweig.csv'.")
