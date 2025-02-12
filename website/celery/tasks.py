""" This is a module that handle the background tasks """

from website.celery.celery_worker import get_celery
from website.mailer.mail import mail
from flask_mail import Message
from time import sleep
import logging
import base64
from firebase_admin import storage


celery = get_celery()
task_logger = logging.getLogger('celery_task')


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
    from website.clients.models.models import LandlordInfo, TenantInfo, Properties, PropertiesImages

    #print(f"Task Started: file_data={file_data}, file_name={file_name}, content_type={content_type}, path={path}, {task_role}, {task_key}")

    try:
        # Decode the Base64-encoded file data
        decoded_file_data = base64.b64decode(file_data)

        # Upload the file to Firebase
        bucket = storage.bucket()
        blob = bucket.blob(file_path)
        blob.upload_from_string(decoded_file_data, content_type=content_type)
        blob.make_public()

        # Prepare the profile picture URL to return
        file_url = blob.public_url
        user_data = None

        user_data = get_user_info(task_key, task_role)


        if task_role == "landlords":
            if not user_data:
                # Create a new LandlordInfo record if it doesn't exist
                user_data = LandlordInfo(landlord_id=task_key)
                db.session.add(user_data)
            # Update the file_key with the file URL
            setattr(user_data, file_key, file_url)

        elif task_role == "tenants":
            if not user_data:
                # Create a new TenantInfo record if it doesn't exist
                user_data = TenantInfo(tenant_id=task_key)
                db.session.add(user_data)
            # Update the file_key with the file URL
            setattr(user_data, file_key, file_url)

        elif task_role == "properties":
            if not user_data:
                # Create a new TenantInfo record if it doesn't exist
                user_data = Properties(secondary_key=task_key)
                db.session.add(user_data)
            # Update the file_key with the file URL
            setattr(user_data, file_key, file_url)

        elif task_role == "properties_images":
            if not user_data:
                # Create a new TenantInfo record if it doesn't exist
                user_data = PropertiesImages(property_id=task_key)
                db.session.add(user_data)
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
