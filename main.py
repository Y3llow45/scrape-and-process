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
  print('Number of job offers: '+str(n))
  try:
    #for index in range(20):
    #  print("Index is "+str(index))
    #  extract_job_description(index)
    #  time.sleep(0.5)
    tech_usage = Counter()
    time.sleep(1)
    print('here /////////////////////////////////////////////////////////////////////////////////////')
    time.sleep(1)
    for job in job_descriptions:    
      job_tech_usage = extract_technologies([job], technologies)
      tech_usage.update(job_tech_usage)
    for tech, count in tech_usage.most_common():
      print(f'{tech}: {count}')
  except Exception as e:
    print(f"Error: {e}")
  finally:
    driver.quit()

def init():
  global technologies
  global job_descriptions
  global job_links
  with open('technologies.json', 'r') as file:
    technologies = json.load(file)
  with open('job_descriptions.json', 'r') as file:
    job_descriptions = [desc for desc in json.load(file) if desc]

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
    job_words = job_cleaned.split()
    for tech in tech_list:
      if tech.lower() in job_words:
        tech_counter[tech] += 1
  return tech_counter

def load():
  driver.get("https://dev.bg/company/jobs/back-end-development/?_job_location=remote")
  accept = driver.find_element(By.CLASS_NAME, "cmplz-accept")
  accept.click()
  time.sleep(2)

def extract_job_description(index):
  job_links = driver.find_elements(By.CSS_SELECTOR, "a.overlay-link.ab-trigger")
  job_links[index*2].click() # no idea why index*2 works
  try:
    job_description_div = WebDriverWait(driver, 10).until(
      EC.visibility_of_element_located((By.CLASS_NAME, "job_description"))
    )
    job_description = job_description_div.text
    save_job_description(job_description)
    driver.back()
  except:
    driver.back()
  

def save_job_description(description):
  try:
    with open('job_descriptions.json', 'r') as file:
      job_descriptions = json.load(file)
  except FileNotFoundError:
    job_descriptions = []
  if description not in job_descriptions:
    job_descriptions.append(description)
  with open('job_descriptions.json', 'w') as file:
    json.dump(job_descriptions, file, indent=4)

if __name__ == "__main__":
  main()
