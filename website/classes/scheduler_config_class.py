from flask_apscheduler import APScheduler
from flask import Flask
from website.clients.models.utils import event_schedular
from os import environ
from datetime import datetime, timedelta


scheduler = APScheduler()

class Config:
    SCHEDULER_API_ENABLED = True

def init_scheduler(app: Flask):
    """ This is a function that intialized the APScheduler """

    if not app.config.get("SCHEDULER_INITIALIZED", False):
        app.config["SCHEDULER_INITIALIZED"] = True
        app.config.from_object(Config)
        scheduler.init_app(app)
        #scheduler.start()

        # Check if the scheduler is already running before starting it
        if not scheduler.running:
            scheduler.start()
            print("Scheduler started successfully.", flush=True)
        else:
            print("Scheduler is already running.", flush=True)

        # Ensure the job is not added multiple times
        if not scheduler.get_job("event_schedular"):
            scheduler.add_job(func=handle_event_schedular_alert, args=[app], trigger='interval', minutes=1, id='event_schedular')

def handle_event_schedular_alert(app):
    """ This is a function that handle the event schdular alert """

    with app.app_context():
        try:
            # Run the appointment function
            event_schedular()
            print("Running the appointments alert check...", flush=True)
        except Exception as e:
            print('Schedular Appointment Error: ', e, flush=True)
            return
