"""
This is a module that define views routes for the users to access...
"""
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app, jsonify
from website.admin.models.utils import get_admin_data, get_all_venues, get_venue_details
from website.clients.models.utils import (
        get_user_uid_from_token,
        delete_cookies_and_redirect)
from website import db
import os
from datetime import datetime, timedelta, timezone, time
from website.admin.models.models import Venues


# Define the BluePrint
adminViews = Blueprint("adminViews", __name__, static_folder="website/admin/static", template_folder="website/admin/templates")

# Define the home route
@adminViews.route("/home")
def adminHome():
    """ This is a function that contains the home page of the admin """

    title = f"SACOETEC EVENT FACE RECONGISTION | Admin | DASHBOARD"
    viewType = f"Admin Dashboard"
    userRole_info = None
    user_info = "Admin"

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_admin_data(user_uid)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))


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
            formatted_previous_last_logged_in=formatted_previous_last_logged_in,)

@adminViews.route("/venue-overview")
def venue_overview():
    """ This is a function that handle the overview of the ... """

    title = f"SACOETEC EVENT FACE RECONGISTION | Admin | VENUE OVERVIEW"
    viewType = f"Admin Venue-OverView"
    userRole_info = None
    user_info = "Admin"

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_admin_data(user_uid)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    return render_template(
            "dashboard/index.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info)

@adminViews.route("/upload-Venue", defaults={'details': None, 'venue_bind_id': None})
@adminViews.route("/upload-Venue/<details>/<venue_bind_id>")
def upload_venue(details, venue_bind_id):
    """ This is a function that allows the admin to register the venue """

    title = f"SACOETEC EVENT FACE RECONGISTION | Admin | VENUE OVERVIEW"
    viewType = f"Admin Register Venue"
    userRole_info = None
    venue_details = None
    user_info = "Admin"

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_admin_data(user_uid)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    if details and venue_bind_id and details == "viewVenue":
        venue_details = get_venue_details(venue_bind_id)

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            venue_details=venue_details,
            user_info=user_info)


@adminViews.route("/all-venues")
def all_venues():
    """ This is a function that list out all the registed venues """

    title = f"SACOETEC EVENT FACE RECONGISTION | Admin | VENUE OVERVIEW"
    viewType = f"Admin All Venue"
    userRole_info = None
    user_info = "Admin"

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_admin_data(user_uid)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    # Fetch all the venues
    all_venues = get_all_venues()

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            all_venues=all_venues,
            viewType=viewType,
            user_info=user_info)


@adminViews.route("/events-overview")
def event_overview():
    """ This is a function that handle the overview of the ... """

    title = f"SACOETEC EVENT FACE RECONGISTION | Admin | VENUE OVERVIEW"
    viewType = f"Admin Event-OverView"
    userRole_info = None
    user_info = "Admin"

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_admin_data(user_uid)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    return render_template(
            "dashboard/index.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info)


@adminViews.route("/upload_event")
def upload_event():
    """ This is a function that handle the overview of the ... """

    title = f"SACOETEC EVENT FACE RECONGISTION | Admin | VENUE OVERVIEW"
    viewType = f"Admin Upload-Event"
    userRole_info = None
    user_info = "Admin"

    # Get the current user UID from token
    user_uid = get_user_uid_from_token()

    if not user_uid:
        flash("Session timed out", 'danger')
        cookies_to_delete = ['auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    # Get the user's data based on their role
    print("user_uid: ", user_uid)
    user_data = get_admin_data(user_uid)

    if not user_data:
        flash('Error: Failed to retrieve user data.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('adminAuth.adminLogin'))

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info)


################### HELPER ROUTES #############################
@adminViews.route("/register-venue", methods=["POST"])
def register_venue():
    """ This is a function that register the venue """

    try:
        data = request.get_json()
        name = data.get("name")
        venueDesc = data.get("description")
        venueAddress = data.get("address")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not name or not venueDesc or not venueAddress or not latitude or not longitude:
            return jsonify({"error": "Missing fields"}), 400

        new_venue = Venues(
                venue_name=name,
                venue_desc=venueDesc,
                venue_address=venueAddress,
                latitude=latitude,
                longitude=longitude
        )

        db.session.add(new_venue)
        db.session.commit()
        return jsonify({"message": "Location registered successfully"}), 201

    except Exception as e:
        print("Error Storing Venue :", e)
        return jsonify({"error": "Missing fields"}), 400


