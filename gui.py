import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QProgressBar, QCheckBox, QWidget, QLabel
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
        self.setGeometry(100, 100, 500, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.layout.addWidget(QLabel("Filters:"))
        self.filters = {
            "Fully Remote": QCheckBox("Fully Remote"),
            "Intern/Junior": QCheckBox("Intern/Junior"),
            "1-2 Years Experience": QCheckBox("1-2 Years Experience"),
            "2-5 Years Experience": QCheckBox("2-5 Years Experience"),
            "5+ Years Experience": QCheckBox("5+ Years Experience"),
            "Team Lead": QCheckBox("Team Lead"),
            "With Mentioned Salary": QCheckBox("With Mentioned Salary"),
            "Small Company": QCheckBox("Small Company"),
            "Big Company": QCheckBox("Big Company")
        }
        for filter_name, checkbox in self.filters.items():
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

    def get_selected_filters(self):
        """Build the URL filters based on selected checkboxes."""
        base_url = "https://dev.bg/company/jobs/back-end-development/"
        query_params = []
        for filter_name, checkbox in self.filters.items():
            if checkbox.isChecked():
                param = self.convert_filter_to_param(filter_name)
                query_params.append(param)
        return base_url + "?" + "&".join(query_params)

    @staticmethod
    def convert_filter_to_param(filter_name):
        """Convert a filter name to the corresponding query parameter."""
        mapping = {
            "Fully Remote": "_job_location=remote",
            "Intern/Junior": "_seniority=intern",
            "1-2 Years Experience": "_seniority=mid-level",
            "2-5 Years Experience": "_seniority=senior",
            "5+ Years Experience": "_seniority=lead",
            "Team Lead": "_seniority=team-lead",
            "With Mentioned Salary": "_salary=1",
            "Small Company": "_company_size=small",
            "Big Company": "_company_size=large"
        }
        return mapping.get(filter_name, "")

    def start_scraping(self):
        """Start the scraping process with selected filters."""
        selected_filters = self.get_selected_filters()
        print(f"Scraping with filters: {selected_filters}")

        self.scrape_thread = ScrapeThread(selected_filters)
        self.scrape_thread.progress.connect(self.update_progress)
        self.scrape_thread.status.connect(self.update_status)
        self.scrape_thread.start()

    def update_progress(self, value):
        """Update the progress bar."""
        self.progress_bar.setValue(value)

    def update_status(self, status):
        """Update the status label."""
        self.status_label.setText(f"Status: {status}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec())
