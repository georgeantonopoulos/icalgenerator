from flask import Flask, render_template, request, send_from_directory
from icalgenerator.cal_event_generator import CalendarEventGenerator
import os

my_app = Flask(__name__)

@my_app.route("/")
def index():
    return render_template("index.html")

@my_app.route("/generate_event", methods=["POST"])
def generate_event():
    event_details = request.form["event_details"]
    event = CalendarEventGenerator(event_details)
    event.save_ical()
    return send_from_directory(event.desktop_path, "event.ics", as_attachment=True)

if __name__ == "__main__":
    my_app.run(debug=True)
