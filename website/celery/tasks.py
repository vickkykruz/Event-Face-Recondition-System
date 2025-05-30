""" This is a module that handle the background tasks """
#from eventlet import monkey_patch
#monkey_patch()

from website.celery.celery_worker import get_celery
from website.mailer.mail import mail
from flask_mail import Message
from time import sleep
import logging
import base64
from firebase_admin import storage
from website.clients.models.utils import get_user_info_data
from dotenv import load_dotenv
from os import path, environ, getenv
import firebase_admin


celery = get_celery()
task_logger = logging.getLogger('celery_task')


# Load environment variables once at startup
load_dotenv()


EVENT_FACE_RECONGITION_FIREBASE_CREDENTIALS = environ.get('EVENT_FACE_RECONGITION_FIREBASE_KEY_PATH')
TELEMEDICAL_FIREBASE_CREDENTIALS = environ.get('TELEMEDICAL_FIREBASE_KEY_PATH')

def get_firebase_app():
    """ Ensure Firebase is initilaized only once """

    if not firebase_admin._apps:
        if not EVENT_FACE_RECONGITION_FIREBASE_CREDENTIALS or not TELEMEDICAL_FIREBASE_CREDENTIALS:
            raise ValueError("Firebase credentials are missing. Check environment variables.")

        event_face_recognition_cred = credentials.Certificate(EVENT_FACE_RECONGITION_FIREBASE_CREDENTIALS)
        telemedical_cred = credentials.Certificate(TELEMEDICAL_FIREBASE_CREDENTIALS)

        event_app = firebase_admin.initialize_app(event_face_recognition_cred, name="event-face")
        telemedical_app = firebase_admin.initialize_app(telemedical_cred, {
            'storageBucket': 'telemedical-710dc.appspot.com'
        }, name="telemedical")

        return event_app, telemedical_app
    return firebase_admin.get_app("event-face"), firebase_admin.get_app("telemedical")



@celery.task(bind=True, default_retry_delay=60, max_retries=3)
def send_mail(self, message, **kwargs):
    """ This function handles the send mail functionality """

    try:
        # Extract subject, sender, and recipients from the message dictionary
        msg = Message(
            subject=message['subject'],
            sender=message['sender'],
            recipients=message['recipients']
        )

        # Format the message body with the additional variables passed via kwargs
        if kwargs:
            # If multiple variables are passed in kwargs, format the message body with them
            msg.html = message['body'].format(**kwargs)
        else:
            # Use the default message body if no additional variables are passed
            msg.html = message['body']

        # msg body
        msg.body = 'Unlimited Health'
        # Send the email
        mail.send(msg)
        task_logger.info(f"Email sent to {message['recipients']}")
        print("Email sent successfully!")

    except Exception as e:
        # Log the error if sending the email fails
        task_logger.error(f"Error sending email: {str(e)}")
        raise self.retry(exc=e)


@celery.task(bind=True, max_retries=3)
def upload_file_to_firebase_task(self, file_data, file_key, content_type, file_path, task_role, task_key):
    """Uploads a file to Firebase Storage asynchronously."""

    from website import db
    #from website.clients.models.models import LandlordInfo, TenantInfo, Properties, PropertiesImages

    #print(f"Task Started: file_data={file_data}, file_name={file_name}, content_type={content_type}, path={path}, {task_role}, {task_key}")

    try:
        # Decode the Base64-encoded file data
        decoded_file_data = base64.b64decode(file_data)

        firebase_app = firebase_admin.get_app("telemedical")

        # Upload the file to Firebase
        bucket = storage.bucket(app=firebase_app)
        blob = bucket.blob(file_path)
        blob.upload_from_string(decoded_file_data, content_type=content_type)
        blob.make_public()

        # Prepare the profile picture URL to return
        file_url = blob.public_url
        user_data = None

        user_data = get_user_info_data(task_key, task_role)


        if task_role == "student_info":
            if user_data: 
                # Update the file_key with the file URL
                setattr(user_data, file_key, file_url)
        else:
            raise ValueError(f"Invalid task role: {task_role}")


        db.session.commit()
    except Exception as exc:
        # Log the error
        print(f"Task failed: {exc}")
        # Retry the task if it fails
        raise self.retry(exc=exc, countdown=5)

    finally:
        # Ensure the database session is closed
        db.session.remove()
