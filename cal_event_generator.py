from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QListWidget, QMessageBox
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
import re
from datetime import datetime
import tempfile
import shutil

class CalendarEventGenerator():
    def __init__(self, prompt=None):
        load_dotenv()
        openai.api_key = os.environ.get("OPENAI_API_KEY")

        self.date = os.popen('date').read().strip()
        self.time = os.popen('date +%H:%M').read().strip()

        self.desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')

        client = OpenAI()

        # Update the system prompt to emphasize the need for multiple events
        user_message = "Your prompt here"  # Replace with your actual user message
        
        messages = [
            {"role": "system", "content": f"""You are a program that creates the content of iCalendar files based on text input. 
            Extract event details including title, location, and price. For events with multiple dates, create a separate iCalendar entry for each date.
            Today's date is {self.date} and the time is {self.time}. 
            Format each event as a complete iCalendar entry and separate them with '---EVENT---'.
            IMPORTANT: For recurring events or events with multiple dates, create a separate iCalendar entry for EACH date and time provided.
            Each entry should have the same event details (title, location, etc.) but with its specific date and time.
            Always create multiple entries for events with multiple dates, even if they appear to be part of a series."""},
            {"role": "user", "content": prompt} if prompt is not None else None
        ]
        
        self.response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        # Create a temporary directory for iCal files
        self.temp_dir = tempfile.mkdtemp(prefix="ical_events_")
        print(f"Temporary directory created at: {self.temp_dir}")
        print(f"Raw API response:\n{ical_content}")

        # Split the content into individual VEVENT blocks
        vevent_blocks = re.findall(r'BEGIN:VEVENT.*?END:VEVENT', ical_content, re.DOTALL)
        
        events = []
        for vevent in vevent_blocks:
            # Wrap each VEVENT in a complete VCALENDAR structure
            full_ical = f"BEGIN:VCALENDAR\nVERSION:2.0\n{vevent}\nEND:VCALENDAR"
            events.append(full_ical)

        print(f"Number of events extracted: {len(events)}")
        return events

    def save_icals(self):
        events = self.get_icals()
        for i, ical in enumerate(events):
            with open(os.path.join(self.temp_dir, f'event_{i+1}.ics'), 'w') as f:
                f.write(ical.strip())
        return len(events)

    def open_icals(self):
        for filename in os.listdir(self.temp_dir):
            if filename.endswith('.ics'):
                os.system(f'open {os.path.join(self.temp_dir, filename)}')

    @classmethod
    def load_existing_events(cls):
        temp_dir = tempfile.gettempdir()
        event_dir = next((d for d in os.listdir(temp_dir) if d.startswith('ical_events_')), None)
        if event_dir:
            full_path = os.path.join(temp_dir, event_dir)
            events = []
            for filename in os.listdir(full_path):
                if filename.endswith('.ics'):
                    with open(os.path.join(full_path, filename), 'r') as f:
                        events.append(f.read())
            return events
        return []

    @classmethod
    def clear_all_events(cls):
        temp_dir = tempfile.gettempdir()
        for d in os.listdir(temp_dir):
            if d.startswith('ical_events_'):
                shutil.rmtree(os.path.join(temp_dir, d))

class EventGeneratorUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Multi-Event Generator")
        self.setFixedSize(800, 400)

        # Set the color palette to a Raycast-like theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(23, 24, 28))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(39, 40, 47))
        palette.setColor(QPalette.AlternateBase, QColor(48, 49, 58))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(67, 70, 83))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.Highlight, QColor(79, 95, 244))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel("Enter event details:")
        self.label.setFont(QFont("Helvetica", 14))
        layout.addWidget(self.label)

        self.lineEdit = QLineEdit()
        layout.addWidget(self.lineEdit)

        self.generateButton = QPushButton("Generate Events")
        self.generateButton.setFont(QFont("Helvetica", 14))
        self.generateButton.clicked.connect(self.generateEvents)
        layout.addWidget(self.generateButton)

        self.eventList = QListWidget()
        layout.addWidget(self.eventList)

        self.saveButton = QPushButton("Save All Events")
        self.saveButton.setFont(QFont("Helvetica", 14))
        self.saveButton.clicked.connect(self.saveEvents)
        layout.addWidget(self.saveButton)

        self.openButton = QPushButton("Open All Events")
        self.openButton.setFont(QFont("Helvetica", 14))
        self.openButton.clicked.connect(self.openEvents)
        layout.addWidget(self.openButton)

        self.clearButton = QPushButton("Clear All Events")
        self.clearButton.setFont(QFont("Helvetica", 14))
        self.clearButton.clicked.connect(self.clearAllEvents)
        layout.addWidget(self.clearButton)

        self.event_generator = None
        self.loadExistingEvents()

    def loadExistingEvents(self):
        events = CalendarEventGenerator.load_existing_events()
        if events:
            self.event_generator = CalendarEventGenerator()
            self.eventList.clear()
            for i, ical in enumerate(events):
                summary = re.search(r'SUMMARY:(.+)', ical)
                summary = summary.group(1) if summary else 'Unknown Event'
                
                date = re.search(r'DTSTART:(\d{8}T\d{6})', ical)
                date = date.group(1) if date else 'Unknown Date'
                
                try:
                    formatted_date = datetime.strptime(date, "%Y%m%dT%H%M%S").strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    formatted_date = date
                
                self.eventList.addItem(f"Event {i+1}: {summary} on {formatted_date}")

    def clearAllEvents(self):
        CalendarEventGenerator.clear_all_events()
        self.eventList.clear()
        self.event_generator = None
        QMessageBox.information(self, "Events Cleared", "All events have been cleared from disk.")

    def generateEvents(self):
        self.event_generator = CalendarEventGenerator(self.lineEdit.text())
        self.eventList.clear()
        events = self.event_generator.get_icals()
        
        print(f"Total events to display: {len(events)}")
        
        for i, ical in enumerate(events):
            summary = re.search(r'SUMMARY:(.+)', ical)
            summary = summary.group(1) if summary else 'Unknown Event'
            
            date = re.search(r'DTSTART:(\d{8}T\d{6})', ical)
            date = date.group(1) if date else 'Unknown Date'
            
            try:
                formatted_date = datetime.strptime(date, "%Y%m%dT%H%M%S").strftime("%Y-%m-%d %H:%M")
            except ValueError:
                formatted_date = date
            
            self.eventList.addItem(f"Event {i+1}: {summary} on {formatted_date}")

    def saveEvents(self):
        if self.event_generator:
            num_events = self.event_generator.save_icals()
            QMessageBox.information(self, "Events Saved", f"{num_events} events have been saved.")

    def openEvents(self):
        if self.event_generator:
            self.event_generator.open_icals()

if __name__ == '__main__':
    app = QApplication([])
    window = EventGeneratorUI()
    window.show()
    app.exec_()
