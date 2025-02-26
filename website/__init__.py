import eventlet

eventlet.monkey_patch()

import secrets
import os
from flask import Flask, render_template, send_from_directory, request
from jinja2 import FileSystemLoader
from website.database.database import db
from website.mailer.mail import mail
from website.clients.models.views import views
from website.clients.models.auth import auth
#from website.admin.models.auth import adminAuth
#from website.admin.models.views import adminViews
from os import path, environ, getenv
from datetime import timedelta
import firebase_admin
from firebase_admin import credentials, firestore, storage
from dotenv import load_dotenv
import pyrebase
import requests
from flask_socketio import SocketIO, emit
import re
from website.clients.models.utils import get_location_from_ip


# Load environment variables once at startup
load_dotenv()

# Initialize SocketIO globally
socketio = SocketIO()

# Connect to database
DB_NAME = "event_face_recongition_system232312@.db"
EVENT_FACE_RECONGITION_FIREBASE_CREDENTIALS = environ.get('EVENT_FACE_RECONGITION_FIREBASE_KEY_PATH')
TELEMEDICAL_FIREBASE_CREDENTIALS = environ.get('TELEMEDICAL_FIREBASE_KEY_PATH')
IPINFO_API_TOKEN = environ.get('IPINFO_API_TOKEN')

if not firebase_admin._apps:
    event_face_recognition_cred = credentials.Certificate(EVENT_FACE_RECONGITION_FIREBASE_CREDENTIALS)
    telemedical_cred = credentials.Certificate(TELEMEDICAL_FIREBASE_CREDENTIALS)

    event_app = firebase_admin.initialize_app(event_face_recognition_cred, name="event-face")
    telemedical_app = firebase_admin.initialize_app(telemedical_cred, {
        'storageBucket': 'telemedical-710dc.appspot.com'
    }, name="telemedical")


# Here to store the uploaded images
UPLOAD_FOLDER = "website/static/uploads"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def create_app():
    """This is a function that issues the name of the app"""
    app = Flask(__name__)  # This represent the name of the file
    # This is going to encrpt or secure D cookie
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    # Set session timeout to 1 hour (for example)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Firebase Pyrebase Config (Replace with your actual Firebase project details)
    firebase_config = {
            'apiKey': environ.get('FIREBASE_APIKEY'),
            'authDomain': environ.get('FIREBASE_AUTHDOMAIN'),
            'projectId': environ.get('FIREBASE_PROJECTID'),
            'storageBucket': environ.get('FIREBASE_STOREAGEBUCKET'),
            'messagingSenderId': environ.get('FIRBASE_MESSAGEINGSENDERID'),
            'appId': environ.get('FIREBASE_APPID'),
            'measurementId': environ.get('FIREBASE_MEASUREMENTID'),
            'databaseURL': environ.get('FIREBASE_DATABASEURL')
    }

    # Store firebase_config in app.config
    app.config['FIREBASE_CONFIG'] = firebase_config

    # Define template folders for clients and admin
    client_template_folder = path.join(app.root_path, "clients", "templates")
    admin_template_folder = path.join(app.root_path, "admin", "templates")

    # Configure Jinja2 environment with multiple template folders
    loader = FileSystemLoader([client_template_folder, admin_template_folder])
    app.jinja_loader = loader  # Set the Jinja loader directly to the Flask app

    # Connect to our database
    app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///' + os.path.join(BASE_DIR, DB_NAME)
    #app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    #app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    #if not firebase_admin._apps:
    #    event_face_recognition_cred = credentials.Certificate(EVENT_FACE_RECONGITION_FIREBASE_CREDENTIALS)
    #    telemedical_cred = credentials.Certificate(TELEMEDICAL_FIREBASE_CREDENTIALS)

    #    event_app = firebase_admin.initialize_app(event_face_recognition_cred, name="event-face")
    #    telemedical_app = firebase_admin.initialize_app(telemedical_cred, {
    #        'storageBucket': 'telemedical-710dc.appspot.com'
    #    }, name="telemedical")

    # Firebase Frontend intilization (Initialize Firebase Pyrebase)
    firebase = pyrebase.initialize_app(firebase_config)
    app.firebase_auth = firebase.auth()

    # Configure Flask-Mail
    app.config['MAIL_SERVER'] = 'mail.sacoeteccscdept.com.ng'  # Your email server (e.g., smtp.gmail.com)
    app.config['MAIL_PORT'] = 587  # Port for your email server (e.g., 587 for Gmail)
    app.config['MAIL_USE_TLS'] = True  # Enable TLS encryption
    app.config['MAIL_USERNAME'] = 'noreply@sacoeteccscdept.com.ng'  # Your email address
    app.config['MAIL_PASSWORD'] = 'Vicchi232312@'  # Your email password
    app.config['MAIL_DEBUG'] = True

    db.init_app(app)
    mail.init_app(app)

    socketio.init_app(app, cors_allowed_origins="*", async_mode='eventlet', ping_timeout=120, ping_interval=25, message_queue="redis://localhost:6379/1")

    # Register the blueprint
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/auth")
    #app.register_blueprint(adminAuth, url_prefix="/admin")
    #app.register_blueprint(adminViews, url_prefix="/admin/page")

    # Custom error handler for 404 Not Found
    @app.errorhandler(404)
    def page_not_found(error):
        """This is a function that handle the 404 error handlers"""
        title = "Easiest Way to Find Your Dream Error | 404"
        return render_template("error_pages/404.html", title=title)

    @app.errorhandler(500)
    def internal_server_error(error):
        """This is a function that handler the 500 error handlers"""
        title = "Easiest Way to Find Your Dream Error | 500"
        return render_template("error_pages/500.html", title=title)

    @app.errorhandler(405)
    def method_not_found(error):
        """This is a function that handler the 405 error handlers"""
        title = "Easiest Way to Find Your Dream Error | 405"
        return render_template("error_pages/405.html", title=title)

    # Event handler when a client connects to the WebSocket
    @socketio.on('connect')
    def handle_connect(auth=None):
        print('Client connected')

        # Get the user’s IP during the connection
        user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        if user_ip and ',' in user_ip:
            user_ip = user_ip.split(',')[0].strip()

        match = re.search(r'::ffff:(\d+\.\d+\.\d+\.\d+)', user_ip)
        if match:
            user_ip = match.group(1)

        location_data = get_location_from_ip(user_ip, IPINFO_API_TOKEN)
        #print(f"user_ip: {user_ip}, user_location: {location_data}")

        if location_data and location_data.get("timezone"):
            timezone_time = pytz.timezone(location_data["timezone"])
            #server_timezone = pytz.timezone(timezone_time.tzname[0])

            # Start broadcasting time to this user
            socketio.start_background_task(target=broadcast_time, timezone=timezone_time)

        # Send a welcome message to the client
        #emit('message', {'data': 'Connected to the server!'})


    # Event handler for receiving a custom event from the client
    @socketio.on('custom_event')
    def handle_custom_event(json_data):
        print(f'Received custom event: {json_data}')
        #Broadcast the event to all connected clients
        emit('message', {'data': f'Server received: {json_data}'}, broadcast=True)


    @socketio.on('request_location')
    def handle_location_request(data):
        """ Fetch user's IP from the request, if behind a proxy set to request headers accordingly """
        #print("data: ", data)
        user_ip = data.get('ip') or request.headers.get('X-Forwarded-For', request.remote_addr)

        if user_ip and ',' in user_ip:
            user_ip = user_ip.split(',')[0].strip()

        match = re.search(r'::ffff:(\d+\.\d+\.\d+\.\d+)', user_ip)
        if match:
            user_ip = match.group(1)
        user_location = get_location_from_ip(user_ip, IPINFO_API_TOKEN)
        token = data.get('token')

        #print("user_ip: ", user_ip)
        #print("user_location: ", user_location)

        if not user_location:
            emit('update_location', {"error": "Location not founds"}, broadcast=False)
            return

        # Get the current user UID from token
        user_uid = get_user_uid_from_token(token)

        if not user_uid:
            emit('update_location', {"error": "User's uid not found"}, broadcast=False)
            return

        user_role, user_data = get_user_data_without_role(user_uid)

        if not user_data and not user_role:
            emit('update_location', {"error": "User's data and User Object not found"}, broadcast=False)
            return

        # Get the update the user's location on the database
        current_latitude = user_location['latitude']
        current_longitude = user_location['longitude']
        previous_latitude = user_data.get('location', {}).get('latitude', None)
        previous_longitude = user_data.get('location', {}).get('longitude', None)

        # Update the 'last_logged_in' with the current time
        location = {
                "latitude": current_latitude,
                "longitude": current_longitude,
                "prev_latitude": previous_latitude,
                "prev_longitude": previous_longitude,
        }

        emit('update_location', user_location, broadcast=False)

    @socketio.on('update_availability')
    def dynamically_fetch_items():
        """ This socket fetech all avilable items """
        print("Socket 'update_availability' event received.")
        emit('available_doctors', broadcast=True)

    @socketio.on('disconnect')
    def handle_disconnect():
        """ This is function that disconnect the socket session """
        print(f"Client disconnected: {request.sid}")


    # Define the route for serving uploaded files
    #@app.route("/<filename>")
    #def uploaded_file(filename):
    #    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    # Import the schemer of our database
    # from website.clients.models.models import User  # noqa: F841
    # from website.admin.models.models import Admin  # noqa: F841

    create_database(app)

    # Return the app
    return app


def create_database(app):
    """This is a function that create the database"""

    # check if the path of our database doesn't exist then create it
    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Created Database")

# Explicitly expose event_app and telemedical_app for imports
__all__ = ["event_app", "telemedical_app"]

