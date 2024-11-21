import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QProgressBar, QCheckBox, QWidget, QLabel, QComboBox, QGroupBox
)
from PySide6.QtCore import Qt, QThread, Signal
import time

class ScrapeThread(QThread):
    progress = Signal(int)
    status = Signal(str)

    def __init__(self, filters):
        super().__init__()
        self.filters = filters

    def run(self):
        total_jobs = 100
        for i in range(total_jobs):
            time.sleep(0.05)
            self.progress.emit(int((i + 1) / total_jobs * 100))
        self.status.emit("Scraping complete!")

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Job Scraper")
        self.setGeometry(100, 100, 700, 500)

        with open("styles.css", "r") as file:
            self.setStyleSheet(file.read())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.layout.addWidget(QLabel("Select Category:"))
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
        self.layout.addWidget(self.category_selector)

        # Filters grouped into categories
        self.filters_layout = QVBoxLayout()
        self.create_filter_groups()
        self.layout.addLayout(self.filters_layout)

        self.scrape_button = QPushButton("Scrape All Jobs")
        self.scrape_button.clicked.connect(self.start_scraping)
        self.layout.addWidget(self.scrape_button)

        self.count_button = QPushButton("Count Technologies")
        self.layout.addWidget(self.count_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Status: Waiting...")
        self.layout.addWidget(self.status_label)

        self.scrape_thread = None
        self.update_filters()

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
                "Next.js": "_ts_front_end_development=next-js"
            }
        }
        self.filter_checkboxes = {}

        for category, options in self.filter_options.items():
            group_box = QGroupBox(category)
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
        selected_filters = self.get_selected_filters()
        print(f"Scraping with filters: {selected_filters}")

        self.scrape_thread = ScrapeThread(selected_filters)
        self.scrape_thread.progress.connect(self.update_progress)
        self.scrape_thread.status.connect(self.update_status)
        self.scrape_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
