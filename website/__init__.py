import secrets
import os
from flask import Flask, render_template, send_from_directory
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


# Load environment variables once at startup
load_dotenv()


# Connect to database
DB_NAME = "event_face_recongition_system232312@.db"
FIREBASE_CREDENTIALS = environ.get('FIREBASE_KEY_PATH')

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

    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'telemedical-710dc.appspot.com'
        })

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
