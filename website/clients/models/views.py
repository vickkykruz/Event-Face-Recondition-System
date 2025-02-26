"""
This is a module that define views routes for the users to access...
"""

from flask import Blueprint, render_template, flash, request, redirect, url_for, make_response, current_app, session
#from website.clients.models.forms import LandLordRegistrationForm, PropertyForm, PropertyImagesForm
from website.clients.models.utils import (
        get_user_uid_from_token,
        get_user_data,
        get_user_info_data,
        delete_cookies_and_redirect)
import base64
#from werkzeug.utils import secure_filename
from website import db
#from website.clients.models.models import LandlordInfo, TenantInfo, Properties
from datetime import datetime, timedelta, timezone, time
import uuid


# Define the BluePrint
views = Blueprint(
    "views",
    __name__,
    static_folder="website/clients/static",
    template_folder="website/clients/templates",
)

@views.route("/")
def home():
    """This is a function that return the home page"""
    userRole = 'students'
    
    return redirect(url_for('auth.clientLogin', userRole=userRole))


@views.route("/<userRole>/dashboard")
def clientDashboard(userRole):
    """ This is function that handle the user dashboard """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC EVENT FACE RECONGISTION | {userRole.upper()} | DASHBOARD"
    viewType = f"{userRole.upper()} Dashboard"
    userRole_info = None

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_user_data(user_uid, userRole)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    if userRole == "students":
        userRole_info = "student_info"

    student_bind_id = user_data.student_bind_id

    # Retrieve user information
    user_info = get_user_info_data(student_bind_id, userRole_info)

    if not user_info:
        flash('Error: Failed to retrieve user info.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    # Format the last logged in time
    previous_last_logged_in = user_data.previous_last_logged_in

    if previous_last_logged_in:
        try:
            # Parse the string into a datetime object
            last_logged_in_time = datetime.fromisoformat(previous_last_logged_in)

            # Format the day suffix
            day_suffix = (
                'th' if 4 <= int(last_logged_in_time.strftime("%d")) <= 20 else
                {1: 'st', 2: 'nd', 3: 'rd'}.get(int(last_logged_in_time.strftime("%d")) % 10, 'th')
            )
            formatted_previous_last_logged_in = last_logged_in_time.strftime(
                f"%d{day_suffix} Of %B, %Y %I:%M:%S %p"
            )
        except ValueError:
            # Handle parsing errors
            formatted_previous_last_logged_in = "Invalid date format"
    else:
        formatted_previous_last_logged_in = "0th Of None, 0000 00:00:00 AM"


    return render_template(
            "dashboard/index.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info,
            formatted_previous_last_logged_in=formatted_previous_last_logged_in,
            userRole=userRole)

@views.route("/<userRole>/attendance-scan", methods=["GET"])
def attendance_scan(userRole):
    """ This is a function that handle the attendance scan"""

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC EVENT FACE RECONGISTION | {userRole.upper()} | ATTENDANCE"
    viewType = f"{userRole.upper()} Attendance"
    userRole_info = None

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_user_data(user_uid, userRole)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    if userRole == "students":
        userRole_info = "student_info"

    student_bind_id = user_data.student_bind_id

    # Retrieve user information
    user_info = get_user_info_data(student_bind_id, userRole_info)

    if not user_info:
        flash('Error: Failed to retrieve user info.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info,
            user_uid=user_uid,
            userRole=userRole)

@views.route("/<userRole>/sucessfull-verification")
def successful_verification(userRole):
    """ This is a route that redirect the user to a successful verification page"""

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC EVENT FACE RECONGISTION | {userRole.upper()} | SUCCESSFULL"
    viewType = f"Suceessfull_Verification"
    userRole_info = None

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_user_data(user_uid, userRole)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    if userRole == "students":
        userRole_info = "student_info"

    student_bind_id = user_data.student_bind_id

    # Retrieve user information
    user_info = get_user_info_data(student_bind_id, userRole_info)

    if not user_info:
        flash('Error: Failed to retrieve user info.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info,
            user_uid=user_uid,
            userRole=userRole)

@views.route("/<userRole>/events")
def event_page(userRole):
    """ This is a route that deals with the clients event """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC EVENT FACE RECONGISTION | {userRole.upper()} | S"
    viewType = "events_page"
    userRole_info = None

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_user_data(user_uid, userRole)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    if userRole == "students":
        userRole_info = "student_info"

    student_bind_id = user_data.student_bind_id

    # Retrieve user information
    user_info = get_user_info_data(student_bind_id, userRole_info)

    if not user_info:
        flash('Error: Failed to retrieve user info.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info,
            user_uid=user_uid,
            userRole=userRole)
