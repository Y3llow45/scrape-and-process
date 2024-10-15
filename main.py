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

with open('technologies.json', 'r') as file:
    technologies = json.load(file)

with open('job_descriptions.json', 'r') as file:
    job_descriptions = json.load(file)


def extract_technologies(jobs, tech_list):
    tech_counter = Counter()
    for job in jobs:
        job_cleaned = re.sub(r'[^\w\s]', '', job).lower()
        for tech in tech_list:
            match, score = process.extractOne(tech.lower(), [job_cleaned])
            if score > 80: 
                tech_counter[tech] += 1
    return tech_counter

tech_usage = extract_technologies(job_descriptions, technologies)

def load():
  driver.get("https://www.google.com/search?q=tic+tac+toe")
  WebDriverWait(driver, 1).until(
    lambda d: d.execute_script("return document.readyState") == "complete"
  )
  div = driver.find_element(By.CSS_SELECTOR, "div.QS5gu.sy4vM")
  div.click()
  time.sleep(2)
for tech, count in tech_usage.most_common():
    print(f'{tech} {count}')