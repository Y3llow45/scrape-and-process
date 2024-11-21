import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QProgressBar, QCheckBox, QWidget, QLabel, QComboBox
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
        self.setGeometry(100, 100, 600, 400)

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

        self.layout.addWidget(QLabel("Filters:"))
        self.filters = {}
        self.filter_options = {
            "Fully Remote": "_job_location=remote",
            "Sofia": "_job_location=sofiya",
            "Intern/Junior": "_seniority=intern",
            "1-2 Years Experience": "_seniority=junior",
            "2-5 Years Experience": "_seniority=mid-level",
            "5+ Years Experience": "_seniority=senior",
            "Team Lead": "_seniority=grand-master",
            "With Mentioned Salary": "_salary=1",
            "Small Company": "_it_employees_count=35%2C36",
            "Big Company": "_it_employees_count=37%2C38"
        }

        for filter_name in self.filter_options:
            checkbox = QCheckBox(filter_name)
            self.filters[filter_name] = checkbox
            self.layout.addWidget(checkbox)

        self.additional_filters = {
            "TypeScript": "_ts_front_end_development=typescript",
            "Node.js": "_ts_front_end_development=node-js",
            "Redux": "_ts_front_end_development=redux",
            "Express": "_ts_front_end_development=express",
            "Next.js": "_ts_front_end_development=next-js"
        }

        self.front_end_options = {}
        for filter_name in self.additional_filters:
            checkbox = QCheckBox(filter_name)
            self.front_end_options[filter_name] = checkbox
            self.layout.addWidget(checkbox)

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

    def update_filters(self):
        category = self.category_selector.currentText()
        if category == "ERP/CRM Development":
            self.filters["With Mentioned Salary"].setVisible(False)
        else:
            self.filters["With Mentioned Salary"].setVisible(True)

        is_front_end = category == "Front-End Development"
        for checkbox in self.front_end_options.values():
            checkbox.setVisible(is_front_end)

    def get_selected_filters(self):
        base_url = self.categories[self.category_selector.currentText()]
        query_params = []

        for filter_name, checkbox in self.filters.items():
            if checkbox.isChecked():
                param = self.filter_options.get(filter_name, "")
                query_params.append(param)

        if self.category_selector.currentText() == "Front-End Development":
            additional_params = []
            for filter_name, checkbox in self.front_end_options.items():
                if checkbox.isChecked():
                    additional_params.append(self.additional_filters[filter_name])
            if additional_params:
                query_params.append("_ts_front_end_development=" + "%2C".join(additional_params))

        return base_url + "?" + "&".join(query_params)

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
