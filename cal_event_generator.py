from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton
import openai
import os


class CalanderEventGenerator():

    def __init__(self, prompt) -> None:

        # Set up your OpenAI API key
        openai.api_key = "YOUR OPEN API KEY"

        # get current date and time from os
        self.date = os.popen('date').read()
        self.time = os.popen('date +%H:%M').read()

        self.desktop_path = os.path.join(os.path.join(
            os.path.expanduser('~')), 'Desktop')

        # Create a chat completion request
        self.response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are a pogram that creates the content of icalendar files based on text input. You can extract date, time, location and event details based on what the user gives you. Do not include a header or any text before the ical example. Today's date is {self.date} and the time is {self.time}"},
                {"role": "user", "content": prompt},
            ]
        )

    def get_ical(self):
        return self.response['choices'][0]['message']['content']

    def save_ical(self):
        ''' save the ical file to the desktop '''

        # desktop location for mac os
        
        with open(f'{self.desktop_path}/event.ics', 'w') as f:
            f.write(self.get_ical())

    def open_ical(self):
        # open the file with the default app
        os.system(f'open {self.desktop_path}/event.ics')


# make a OS agnostic UI for the above and save the ical file to the desktop


class EventGeneratorUI(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set window title and size
        self.setWindowTitle("Event Generator")
        self.setFixedSize(800, 200)

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

        # Add a label for the user input
        self.label = QLabel(self)
        self.label.setText("Enter event details:")
        self.label.setFont(QFont("Helvetica", 14))
        self.label.move(20, 20)

        # Add a line edit for the user to input text
        self.lineEdit = QLineEdit(self)
        self.lineEdit.move(20, 60)
        self.lineEdit.resize(760, 30)

        # Add a button to generate the event

        button_style = '''
            QPushButton {
                border-radius: 10px;
                padding: 10px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #a70000, stop:1 #4d0000);
                color: white;
                font-size: 16px;
            }
            
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff2e2e, stop:1 #b30000);
            }
            
            QPushButton:pressed {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff2e2e, stop:1 #b30000);
                padding-left: 15px;
                padding-top: 15px;
            }
        '''

        self.generateButton = QPushButton(self)
        self.generateButton.setStyleSheet(button_style)
        self.generateButton.setText("Generate Event")
        self.generateButton.setFont(QFont("Helvetica", 14))
        # place the button in the middle of the window
        self.generateButton.move(320, 120)
        self.generateButton.resize(160, 50)
        self.generateButton.clicked.connect(self.generateEvent)

    def generateEvent(self):
        # This function would generate the event based on the user input text
        event = CalanderEventGenerator(self.lineEdit.text())
        event.save_ical()
        event.open_ical()


if __name__ == '__main__':
    app = QApplication([])
    window = EventGeneratorUI()
    window.show()
    app.exec_()
