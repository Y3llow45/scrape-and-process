import re
from collections import Counter
from fuzzywuzzy import process
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

service = Service(executable_path='./driver/geckodriver.exe')
driver = webdriver.Firefox(service=service)
driver.set_window_size(700, 700)
driver.implicitly_wait(3)

def main():
  init()
  load()
  n = get_job_offers_count()
  try:
    for i in range(n):
      jobs = driver.find_elements(By.CLASS_NAME)
      tech_usage = extract_technologies(jobs, technologies)
      for tech, count in tech_usage.most_common():
        print(f'{tech}: {count}')
  except Exception as e:
    print(f"Error: {e}")
  finally:
    driver.quit()

def init():
  global technologies
  global job_descriptions
  with open('technologies.json', 'r') as file:
    technologies = json.load(file)
  with open('job_descriptions.json', 'r') as file:
    job_descriptions = json.load(file)

def get_job_offers_count():
  total_jobs_div = WebDriverWait(driver, 1).until(
     EC.visibility_of_element_located((By.CLASS_NAME, "facetwp-facet-total_items"))
  )
  total_jobs_text = total_jobs_div.text
  total_jobs_count = int(total_jobs_text.split()[0])
  return total_jobs_count

def extract_technologies(jobs, tech_list):
  tech_counter = Counter()
  for job in jobs:
    job_cleaned = re.sub(r'[^\w\s]', '', job).lower()
    for tech in tech_list:
      score = process.extractOne(tech.lower(), [job_cleaned])
      if score > 80: 
        tech_counter[tech] += 1
  return tech_counter

def load():
  driver.get("https://dev.bg/company/jobs/back-end-development/?_job_location=remote") # itjobs will ban you
  accept = driver.find_element(By.CLASS_NAME, "cmplz-accept")
  accept.click()
  time.sleep(2)

if __name__ == "__main__":
  main()