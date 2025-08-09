"""
This is a module that define views routes for the users to access...
"""

from flask import Blueprint, render_template, flash, request, redirect, url_for, make_response, current_app, session, jsonify
#from website.clients.models.forms import LandLordRegistrationForm, PropertyForm, PropertyImagesForm
from website.clients.models.utils import (
        get_user_uid_from_token,
        get_user_data,
        get_user_info_data,
        delete_cookies_and_redirect,
        get_lastest_event,
        get_new_events,
        get_student_records,
        get_all_users)
from website.admin.models.utils import (
        get_event_details,
        get_venue_details)
import base64
#from werkzeug.utils import secure_filename
from website import db
#from website.clients.models.models import LandlordInfo, TenantInfo, Properties
from datetime import datetime, timedelta, timezone, time
import uuid
import face_recognition
import numpy as np
import json
import os


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


@views.route("/<userRole>/dashboard", defaults={'user_uid': None}, methods=["GET"])
@views.route("/<userRole>/dashboard/<user_uid>", methods=["GET"])
def clientDashboard(userRole, user_uid):
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
    if not user_uid:
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

    student_blind_uid = user_data.student_bind_id

    if userRole == "students":
        userRole_info = "student_info"

    student_bind_id = user_data.student_bind_id

    # Retrieve user information
    user_info = get_user_info_data(student_bind_id, userRole_info)

    if not user_info:
        flash('Error: Failed to retrieve user info.', 'danger')
        cookies_to_delete = ['userRole', 'auth_token']
        return delete_cookies_and_redirect(cookies_to_delete, url_for('auth.clientLogin', userRole=userRole))

    department = user_info.dept
    level = user_info.level

    # List three coming event in related to the students
    upcomming_events = get_lastest_event(department, level)

    table = "attendance"
    filtered_upcoming_events = []

    for comming_event, comming_venue in upcomming_events:

        select_events = get_student_records(student_blind_uid, comming_event.event_bind_id, table)

        if select_events and select_events.status == "pending":
            # Push the particular event and venue
            filtered_upcoming_events.append((comming_event, comming_venue))


    # Get all the events
    all_new_evenets = get_new_events(department, level)

    print('all_new_evenets', all_new_evenets)
    filtered_events = []

    for event in all_new_evenets:

        select_events = get_student_records(student_blind_uid, event.event_bind_id, table)

        if select_events and select_events.status == "pending":
            # Push the particular event and venue
            filtered_events.append(event)

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

    print("upcoming_events before rending at the template:", upcomming_events)

    return render_template(
            "dashboard/index.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info,
            upcomming_events=filtered_upcoming_events,
            all_new_evenets=filtered_events,
            formatted_previous_last_logged_in=formatted_previous_last_logged_in,
            userRole=userRole)


@views.route("/<userRole>/venue")
@views.route("/<userRole>/venue/<string:details>/<string:venue_bind_id>")
def locate_venue(userRole, details=None, venue_bind_id=None):
    """ This is a function that allows the admin to register the venue """

    title = f"SACOETEC EVENT FACE RECONGISTION | Admin | VENUE OVERVIEW"
    viewType = f"Admin Register Venue"
    userRole_info = None
    venue_details = None
    event_details = None
    user_info = "Admin"

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

    print(f"Details: {details} and event_bind_id: {venue_bind_id}")
    spacial_event_id = None


    if details == "locate_user" and venue_bind_id:
        event_details = get_event_details(venue_bind_id)
        special_event_id = event_details.event_bind_id

        venue_bind_id = event_details.venue_id
        venue_details = get_venue_details(venue_bind_id)

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            details=details,
            venue_details=venue_details,
            venue_bind_id=venue_bind_id,
            event_details=event_details,
            special_event_id=special_event_id,
            userRole=userRole,
            user_info=user_info)


@views.route("/<userRole>/attendance-scan/<event_bind_id>", methods=["GET"])
def attendance_scan(userRole, event_bind_id):
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
            event_bind_id=event_bind_id,
            user_uid=user_uid,
            userRole=userRole)


@views.route("/<userRole>/sucessfull-verification")
@views.route("/<userRole>/sucessfull-verification/<user_uid>")
def successful_verification(userRole, user_uid=None):
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
    if not user_uid:
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

    department = user_info.dept
    level = user_info.level

    # List three coming event in related to the students
    upcomming_events = get_lastest_event(department, level)

    table = "attendance"
    filtered_upcoming_events = []

    for comming_event, comming_venue in upcomming_events:

        select_events = get_student_records(student_bind_id, comming_event.event_bind_id, table)

        if select_events and select_events.status == "pending":
            # Push the particular event and venue
            filtered_upcoming_events.append((comming_event, comming_venue))


    # Get all the events
    all_new_evenets = get_new_events(department, level)

    print('all_new_evenets', all_new_evenets)
    filtered_events = []

    for event in all_new_evenets:

        select_events = get_student_records(student_bind_id, event.event_bind_id, table)

        if select_events and select_events.status == "pending":
            # Push the particular event and venue
            filtered_events.append(event)

    return render_template(
            "dashboard/blank.html",
            title=title,
            user_data=user_data,
            viewType=viewType,
            user_info=user_info,
            user_uid=user_uid,
            upcomming_events=filtered_upcoming_events,
            all_new_evenets=filtered_events,
            userRole=userRole)


############### HELPER ROUTERS ################################
@views.route("/<userRole>/recognize-face", methods=["POST"])
@views.route("<userRole>/recognize-face/<event_bind_id>", methods=["POST"])
def recognize_face(userRole, event_bind_id=None):
    """ This is a function route that implement the recognation of the user face """

    try:
        data = request.json
        image_data = data.get("scanResult")
        face_scan_key = data.get("faceScanKey")

        if not image_data or not face_scan_key:
            return jsonify({"error": "Missing required data"}), 400

        # ✅ Generate a temporary filename
        temp_filename = "scanned_face.png"
        temp_dir = "temp_faces/"
        temp_image_path = os.path.join(temp_dir, temp_filename)
        print("temp_image_path", temp_image_path)


        if not os.path.exists(temp_dir):
            print("Yes Opened the directory")
            os.makedirs(temp_dir)

        try:
            # ✅ Extract only the Base64 image data (remove prefix)
            if ',' in image_data:
                image_data = image_data.split(",")[1]

            # ✅ Decode Base64 and save the image locally
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            return jsonify({"error": "Invalid Base64 image data", "details": str(e)}), 400


        with open(temp_image_path, "wb") as img_file:
            print("Write into the file")
            img_file.write(image_bytes)

        # ✅ Process the image with face_recognition
        print("Process the image with face_recognition")
        scanned_image = face_recognition.load_image_file(temp_image_path)
        scanned_encodings = face_recognition.face_encodings(scanned_image)

        # ✅ Ensure at least one face is detected
        if len(scanned_encodings) == 0:
            print("Delete temp file if no face detected")
            os.remove(temp_image_path)  # Delete temp file if no face detected
            return jsonify({
                "error": "No face detected. Try again.",
                "redirect_url": f"https://efrs.sacoeteccscdept.com.ng/students/sucessfull-verification"}), 400

        scanned_encoding = scanned_encodings[0]  # Get first detected face

        # ✅ Retrieve all stored face encodings from the database
        students = get_all_users(f"{userRole}")

        for student in students:
            stored_encoding = np.array(json.loads(student.face_encoding))  # Convert JSON back to NumPy array

            # ✅ Compare the scanned face with stored face encoding
            match = face_recognition.compare_faces([stored_encoding], scanned_encoding, tolerance=0.5)  # Adjust tolerance

            if match[0]:  # If a match is found
                os.remove(temp_image_path)  # 🗑️ Delete temp file after processing

                # ✅ Store user authentication in session
                student_uid = student.uid

                user_data = get_user_data(student_uid, userRole)

                print("user_data", user_data)

                if not user_data:
                    return jsonify({"error": "Face not recognized! Access Denied."}), 401

                # Mark the user attendance
                student_blind_id = user_data.student_bind_id
                print("student_blind_id", student_blind_id)

                if not event_bind_id:
                    event_bind_id = face_scan_key

                print("event_bind_id", event_bind_id)

                mark_attendence = get_student_records(student_blind_id, event_bind_id, "attendance")
                print("mark_attendence", mark_attendence)
                mark_attendence.status = "present"

                # Commit the changes
                db.session.commit()


                return jsonify({
                    "success": True,
                    "message": "Face Recognized! Redirecting...",
                    "user_id": student_uid,
                    "redirect_url": f"https://efrs.sacoeteccscdept.com.ng/students/sucessfull-verification/{student_uid}"
                })

        os.remove(temp_image_path)  # 🗑️ Delete temp file if no match found
        return jsonify({"error": "Face not recognized! Access Denied."}), 401

    except Exception as e:
        print("Error recognizing face:", e)
        return jsonify({"error": "Error processing image"}), 500
