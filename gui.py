import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QCheckBox, QWidget, QLabel, QComboBox, QGroupBox, QGridLayout, QTabWidget, QTextEdit
)
from PySide6.QtCore import Qt, QThread, Signal
import re
from collections import Counter
from fuzzywuzzy import process
import math
import json
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ScrapeThread(QThread):
    progress = Signal(int)
    status = Signal(str)

    def __init__(self, driver, filters, job_descriptions, technologies):
        super().__init__()
        print("in init")
        self.driver = driver
        self.filters = filters
        self.job_descriptions = job_descriptions
        self.technologies = technologies

    def get_job_offers_count(self):
        total_jobs_div = WebDriverWait(self.driver, 1).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "facetwp-facet-total_items"))
        )
        return int(total_jobs_div.text.split()[0])

    def navigate_to_next_page(self):
        try:
            next_button = self.driver.find_element(By.CSS_SELECTOR, "a.facetwp-page.next")
            if next_button:
                next_button.click()
                time.sleep(1)
                return True
        except Exception:
            pass
        return False

    def process_job(index, self):
        try:
            print(f"Processing job at index {index}")
            self.extract_job_description(index)
        except Exception as e:
            print(f"Error processing job at index {index}: {e}")
            
    def extract_job_description(index, self):
        job_links = self.driver.find_elements(By.CSS_SELECTOR, "a.overlay-link.ab-trigger")
        job_links[index*2].click()
        try:
            job_description_div = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "job_description"))
            )
            job_description = job_description_div.text
            self.save_job_description(job_description)
            self.self.driver.back()
        except:
            self.self.driver.back()

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

    def extract_technologies(self, jobs):
        tech_counter = Counter()
        for job in jobs:
            job_cleaned = re.sub(r'[^\w\s]', '', job).lower()
            job_words = job_cleaned.split()
            for tech in self.technologies:
                if tech.lower() in job_words:
                    tech_counter[tech] += 1
        return tech_counter

    def getJobs(pages, left, self):
        n = self.get_job_offers_count()
        print('Number of job offers: '+str(n))

        for p in range(pages):
            for index in range(20):
                self.process_job(index)
                time.sleep(0.5)
            self.navigate_to_next_page()
        for index in range(left):
            self.process_job(index)
            time.sleep(0.5)  

    def run(self):
        self.driver.get()
        self.driver.get(self.filters)
        self.driver.find_element(By.CLASS_NAME, "cmplz-accept").click()
        time.sleep(2)

        n = self.get_job_offers_count()
        jobs_per_page = 20
        pages = math.floor(n / jobs_per_page)
        left = n - (pages * jobs_per_page)

        try:
            self.getJobs(pages, left, self)
            tech_usage = Counter()
            for job in self.job_descriptions:
                job_tech_usage = self.extract_technologies([job])
                tech_usage.update(job_tech_usage)

            for tech, count in tech_usage.most_common():
                print(f'{tech}: {count}') # store all results in a variable and then display the variable in results tab
        
            self.driver.quit()
            self.status.emit("Scraping complete!")
        except Exception as e :
            print(f"Error: {e}")
        finally:
            self.driver.quit()


class AppWindow(QMainWindow):
    def load_files(self):
        with open('technologies.json', 'r') as file:
            self.technologies = json.load(file)
        with open('job_descriptions.json', 'r') as file:
            self.job_descriptions = [desc for desc in json.load(file) if desc]
        with open("styles.css", "r") as file:
            self.setStyleSheet(file.read())

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Scraper")
        self.setGeometry(100, 100, 700, 500)

        self.driver = webdriver.Firefox(service=Service(executable_path='./driver/geckodriver.exe'))
        self.driver.set_window_size(700, 700)
        self.driver.implicitly_wait(3)

        self.load_files()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.create_filter_tab()
        self.create_results_tab()

    def create_filter_tab(self):
        self.filter_tab = QWidget()
        self.tab_widget.addTab(self.filter_tab, "Filters")

        layout = QVBoxLayout(self.filter_tab)

        layout.addWidget(QLabel("Select Category:"))
        self.category_selector = QComboBox()
        self.categories = {
            "Front-End Development": "https://dev.bg/company/jobs/front-end-development/",
            "Back-End Development": "https://dev.bg/company/jobs/back-end-development/",
            "Full-Stack Development": "https://dev.bg/company/jobs/full-stack-development/",
            "Operations": "https://dev.bg/company/jobs/operations/",
            "Quality Assurance": "https://dev.bg/company/jobs/quality-assurance/",
            "PM/BA and More": "https://dev.bg/company/jobs/pm-ba-and-more/",
            "Mobile Development": "https://dev.bg/company/jobs/mobile-development/",
            "Data Science": "https://dev.bg/company/jobs/data-science/",
            "ERP/CRM Development": "https://dev.bg/company/jobs/erp-crm-development/"
        }
        self.category_selector.addItems(self.categories.keys())
        self.category_selector.currentIndexChanged.connect(self.update_filters)
        layout.addWidget(self.category_selector)

        self.filters_layout = QVBoxLayout()
        self.create_filter_groups()
        layout.addLayout(self.filters_layout)

        self.scrape_button = QPushButton("Scrape All Jobs")
        self.scrape_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.scrape_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Status: Waiting...")
        layout.addWidget(self.status_label)

    def create_results_tab(self):
        self.results_tab = QWidget()
        self.tab_widget.addTab(self.results_tab, "Results")

        layout = QVBoxLayout(self.results_tab)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

    def create_filter_groups(self):
        self.filter_options = {
            "Location": {
                "Fully Remote": "_job_location=remote",
                "Sofia": "_job_location=sofiya"
            },
            "Seniority": {
                "Intern/Junior": "_seniority=intern",
                "1-2 Years Experience": "_seniority=junior",
                "2-5 Years Experience": "_seniority=mid-level",
                "5+ Years Experience": "_seniority=senior",
                "Team Lead": "_seniority=grand-master"
            },
            "Team Size": {
                "Small Company": "_it_employees_count=35%2C36",
                "Big Company": "_it_employees_count=37%2C38"
            },
            "Salary": {
                "With Mentioned Salary": "_salary=1"
            },
            "Tech Stack": {
                "TypeScript": "_ts_front_end_development=typescript",
                "Node.js": "_ts_front_end_development=node-js",
                "Redux": "_ts_front_end_development=redux",
                "Express": "_ts_front_end_development=express",
                "Next.js": "_ts_front_end_development=next-js",
                "CSS3": "_ts_front_end_development=css3"
            }
        }
        self.filter_checkboxes = {}

        for category, options in self.filter_options.items():
            group_box = QGroupBox(category)

            if category == "Seniority":
                group_layout = QGridLayout()
                for i, (filter_name, param) in enumerate(options.items()):
                    checkbox = QCheckBox(filter_name)
                    self.filter_checkboxes[filter_name] = checkbox
                    row, col = divmod(i, 3)
                    group_layout.addWidget(checkbox, row, col)
            elif category == "Tech Stack":
                group_layout = QGridLayout()
                for i, (filter_name, param) in enumerate(options.items()):
                    checkbox = QCheckBox(filter_name)
                    self.filter_checkboxes[filter_name] = checkbox
                    row, col = divmod(i, 3)
                    group_layout.addWidget(checkbox, row, col)
            elif category in ["Location", "Team Size"]:
                group_layout = QHBoxLayout()
                for filter_name, param in options.items():
                    checkbox = QCheckBox(filter_name)
                    self.filter_checkboxes[filter_name] = checkbox
                    group_layout.addWidget(checkbox)
            else:
                group_layout = QVBoxLayout()
                for filter_name, param in options.items():
                    checkbox = QCheckBox(filter_name)
                    self.filter_checkboxes[filter_name] = checkbox
                    group_layout.addWidget(checkbox)

            group_box.setLayout(group_layout)
            self.filters_layout.addWidget(group_box)

    def update_filters(self):
        category = self.category_selector.currentText()
        if category == "ERP/CRM Development":
            self.filter_checkboxes["With Mentioned Salary"].setVisible(False)
        else:
            self.filter_checkboxes["With Mentioned Salary"].setVisible(True)

        is_front_end = category == "Front-End Development"
        tech_stack_group = self.find_group_box("Tech Stack")
        for checkbox in tech_stack_group.findChildren(QCheckBox):
            checkbox.setVisible(is_front_end)

    def find_group_box(self, name):
        for i in range(self.filters_layout.count()):
            group_box = self.filters_layout.itemAt(i).widget()
            if isinstance(group_box, QGroupBox) and group_box.title() == name:
                return group_box
        return None

    def get_selected_filters(self):
        base_url = self.categories[self.category_selector.currentText()]
        location_params = []
        seniority_params = []
        query_params = []

        for filter_name, checkbox in self.filter_checkboxes.items():
            if checkbox.isChecked():
                param = self.get_filter_param(filter_name)
                if "job_location" in param:
                    location_params.append(param.split("=")[1])
                elif "seniority" in param:
                    seniority_params.append(param.split("=")[1])
                else:
                    query_params.append(param)

        if location_params:
            query_params.append(f"_job_location={'%2C'.join(location_params)}")
        if seniority_params:
            query_params.append(f"_seniority={'%2C'.join(seniority_params)}")

        return base_url + "?" + "&".join(query_params)

    def get_filter_param(self, filter_name):
        for category, options in self.filter_options.items():
            if filter_name in options:
                return options[filter_name]
        return ""

    def start_scraping(self):
        try:
            selected_filters = self.get_selected_filters()
            print(f"Scraping with filters: {selected_filters}")
            self.results_text.setText(f"Scraping with filters:\n{selected_filters}")
            self.scrape_thread = ScrapeThread(selected_filters)
            self.scrape_thread.progress.connect(self.update_progress)
            self.scrape_thread.status.connect(self.update_status)
            self.scrape_thread.results.connect(self.display_results)
            self.scrape_thread.start()
        except Exception as e:
            print(f"Error during scraping: {e}")
            
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

    def display_results(self, results):
        self.results_text.setText(results)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
