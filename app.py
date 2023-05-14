from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import openai

app = Flask(__name__)
#load_dotenv()

class CalendarEventGenerator():

    def __init__(self, prompt) -> None:
        
        load_dotenv()
        # Set up your OpenAI API key
        openai.api_key = os.environ.get("OPENAI_API_KEY")

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-event', methods=['POST'])
def generate_event():
    prompt = request.form['prompt']
    event_gen = CalendarEventGenerator(prompt)
    event_gen.save_ical()
    event_gen.open_ical()
    return 'Event generated successfully!'

if __name__ == '__main__':
    app.run(debug=True)