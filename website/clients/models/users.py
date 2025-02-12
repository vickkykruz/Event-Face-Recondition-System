""" This is a modue that deals with the functionality of the user """

import re
from website.clients.models.models import Students

# from website.admin.models.utilities import generate_random_number


# vaildate user info if it is an email or a phone number
def validate_email(email):
    # Regular expression pattern for validating email addresses
    email_pattern = r"^[\w\.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_pattern, email) is not None


def validate_phone_number(phone_number):
    # Regular expression pattern for validating phone numbers
    phone_pattern = (
        r"^(\+?\d{1,3})?[-.\s]?"
        r"\(?\d{3}\)?[-.\s]?"
        r"\d{3}[-.\s]?\d{4}$"
    )
    return re.match(phone_pattern, phone_number) is not None


# Fetching a user data thorogh their email address
def get_user_by_email(email):
    return Students.query.filter_by(email=email).first()


# Fetching a user data through their phone number
def get_user_by_phone_number(phone_number):
    return Students.query.filter_by(phone_number=phone_number).first()


# Fetching the user data through their session bind_id
def get_user_by_bind_id(bind_id):
    """This is a function that return the user data as a dictionary"""
    return Students.query.filter_by(bind_id=bind_id).first()
