from flask import Blueprint, render_template, flash, request, redirect, url_for, make_response, current_app, session, jsonify
# from website.admin.models.admins import get_admin_by_email
#from website.clients.models.password_utils import set_password, check_password
from website import db
from website.clients.models.users import (
    validate_email,
    validate_phone_number,
    get_user_by_email,
    get_user_by_phone_number,
)
from website.clients.models.forms import LoginForm, RegisterForm, EmailVerificationForm, ForgottenPasswordForm, ResetPasswordForm, ResendEmailVerificationForm
from website.clients.models.models import Students, EmailVerification, ResetVerification, StudentInfo
from website.clients.models.utils import (
        handle_error_msg,
        update_firebase_name_profile,
        send_alert_email,
        get_user_data,
        get_user_uid_from_token,
        get_location_from_ip,
        generate_auth_token,
        get_user_by_email_firebase,
        get_user_info_data)
import json
import re
import secrets
import base64
import face_recognition
import numpy as np
import cv2
from firebase_admin import auth as firebase_auth, firestore
from firebase_admin.exceptions import FirebaseError
from os import path, environ, getenv
from datetime import datetime, timedelta, timezone, time
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import firebase_admin


# Load environment variables once at startup
load_dotenv()

IPINFO_API_TOKEN = environ.get('IPINFO_API_TOKEN')


# Define the BluePrint
auth = Blueprint(
    "auth",
    __name__,
    static_folder="website/clients/static",
    template_folder="website/clients/templates",
)

# Define the routes for user authenication
@auth.route("/<userRole>/logout", methods=['GET'])
def logout(userRole):
    """This function handles the logout process for all user roles."""

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    background_session_id = request.cookies.get('background_session_id')
    if background_session_id:
        current_app.redis_client.delete(f'session_data:{background_session_id}')

    # Create a response for the logout process
    response = make_response(redirect(url_for('auth.clientLogin', userRole=userRole)))

    # Remove the auth_token cookie
    response.set_cookie('auth_token', '', expires=0, httponly=True, secure=False)
    response.set_cookie('background_session_id', '', httponly=True, secure=False)


    # Flash a message to the user (optional)
    flash('You have successfully logged out.', 'success')
    return response


@auth.route("/<userRole>/login", methods=['GET', 'POST'])
def clientLogin(userRole):
    """ This is a function hadles the patients login functionalities """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC Event System | {userRole.upper()} | Login"
    viewType = f"{userRole.capitalize()} Login"
    form = LoginForm()

    if request.method == 'POST':
        print("recieved POST data")
        # Get the data
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required.", "danger")
            return redirect(url_for('auth.clientLogin', userRole=userRole))

        try:

            # Authenticate user (using Firebase, or your authentication method using SDK)
            # user_record = firebase_auth.get_user_by_email(email)
            user_record = current_app.firebase_auth.sign_in_with_email_and_password(email, password)

            # If user authentication fails, return an error
            if not user_record or 'localId' not in user_record or 'idToken' not in user_record:
                raise ValueError("Invalid email or password. Please try again.")

            user_uid = user_record['localId']
            auth_token = user_record['idToken']

            # Check cache for user data
            user_data = get_user_data(user_uid, userRole)
            if not user_data:
                raise ValueError("User record not found. Please register first.")

             # Check if email is verified
            if user_data.email_verify == "Not Verified":
                flash("Your email is not verified. Please verify your email.", "danger")
                return redirect(url_for('auth.resend_verification', userRole=userRole))

            student_blind_uid = user_data.student_bind_id

            if userRole == "students":
                userRole_info = "student_info"

            student_bind_id = user_data.student_bind_id

            # Retrieve user information
            user_info = get_user_info_data(student_bind_id, userRole_info)

            # Get location from IP
            user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

            if user_ip and ',' in user_ip:
                user_ip = user_ip.split(',')[0].strip()

            match = re.search(r'::ffff:(\d+\.\d+\.\d+\.\d+)', user_ip)
            if match:
                user_ip = match.group(1)

            print('UserIP Address: ', user_ip)

            user_location = get_location_from_ip(user_ip, IPINFO_API_TOKEN)

            if not user_location:
                flash("An error occured. Please try again later.", "danger")
                print('An error occureds. Please try again later.')
                return redirect(url_for('auth.clientLogin', userRole=userRole))

            current_latitude = user_location['latitude']
            current_longitude = user_location['longitude']
            previous_latitude = previous_latitude = getattr(user_data, "previous_latitude", None) or "None"
            previous_longitude = getattr(user_data, "previous_longitude", None) or "None"

            # Get the current time and the previous 'last_logged_in' and user,s location
            current_time = datetime.utcnow()  # Current time in UTC
            previous_last_logged_in = getattr(user_data, "last_logged_in", None) or "None"

            user_data.current_latitude = current_latitude
            user_data.current_longitude = current_longitude
            user_data.previous_latitude = previous_latitude
            user_data.previous_longitude = previous_longitude
            user_data.last_logged_in = current_time
            user_data.previous_last_logged_in = previous_last_logged_in

            # Commit the changes
            db.session.commit()


            # Store session token in cookies
            if user_info:
                response = make_response(redirect(url_for('views.clientDashboard', userRole=userRole, user_uid=user_uid)))
            else:
                response = make_response(redirect(url_for('auth.submit_information', userRole=userRole, user_uid=user_uid)))

            response.set_cookie('auth_token', auth_token, httponly=True, secure=False, max_age=3600)

            flash('You are welcome', 'success')
            return response
        except ValueError as e:
            print(f'Error: {e}')
            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return redirect(url_for('auth.clientLogin', userRole=userRole))
        except Exception as e:
            print(f'Error: {e}')
            # Handle general exceptions
            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return redirect(url_for('auth.clientLogin', userRole=userRole))

    return render_template("auth.html", title=title, form=form, userRole=userRole, viewType=viewType)



@auth.route("/<userRole>/register", methods=['GET', 'POST'])
def clientRegister(userRole):
    """This is a function that return the view landlords register page.
    """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404


    form = RegisterForm()
    title = f"SACOETEC PROPERTY | {userRole.upper()} | Register"
    viewType = f"{userRole.capitalize()} Register"

    if request.method == 'POST':
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        user = None

        try:
            if not name or not email or not password:
                flash("All the fields are required.", "danger")
                return redirect(url_for('auth.clientRegister', userRole=userRole))

            user = current_app.firebase_auth.create_user_with_email_and_password(email, password)
            user_uid = user['localId']
            auth_token = user['idToken']

            # Update the display name using the update_profile method
            response = update_firebase_name_profile(auth_token, name)

            if not response == 200:
                raise ValueError("Unable to update profile records")


            # Generate token for email verification
            token = secrets.token_urlsafe(16)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=4)
            email_verf_key = f'email_{user_uid}'

            email_veriff_session = EmailVerification(
                    email_key=email_verf_key,
                    token=token,
                    email=email,
                    expiresAt=expires_at
            )

            link = url_for('auth.verify_email', userRole=userRole, token=token, user_uid=user_uid, _external=True)
            template_title = "SACOETEC : Email Verification Notification"
            message = "Your account has been created successfully."
            action = "activate your account"
            send_alert_email(template_title, name, message, action, link, email)

            if userRole == "students":
                add_user_session = Students(uid=user_uid, name=name, email=email)
            else:
                raise ValueError("Invalid user role.")

            db.session.add(email_veriff_session)
            db.session.add(add_user_session)
            db.session.commit()


            flash("Registration successful! Please check your email to verify your accoun.", "success")
            if userRole == "students":
                response = make_response(redirect(url_for('auth.clientRegister', userRole=userRole)))
            response.set_cookie('auth_token', auth_token, httponly=True, secure=False, max_age=3600)
            return response
        except (ValueError, Exception) as e:
            # Undo changes if something fails
            current_app.logger.info(f'Error: Error processing {e}')
            if user:
                user_uid = user['localId']
                firebase_auth.delete_user(user_uid)

                email_verf_key = f'email_{user_uid}'

                if userRole == "students":
                    record_to_delete = Students.query.filter_by(uid=user_uid).first()
                else:
                    record_to_delete = None

                email_record_to_delete = EmailVerification.query.filter_by(email_key=email_verf_key).first()

                if record_to_delete:
                    db.session.delete(record_to_delete)
                if email_record_to_delete:
                    db.session.delete(email_record_to_delete)

                db.session.commit()

            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return render_template("auth.html", title=title, form=form, viewType=viewType)

    return render_template("auth.html", title=title, form=form, userRole=userRole, viewType=viewType)


@auth.route("/<userRole>/submit_information/<user_uid>", methods=["GET","POST"])
def submit_information(userRole, user_uid):
    """ This is route function that process and store the user information """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404


    title = f"SACOETEC PROPERTY | {userRole.upper()} | Email Vertification"
    viewType = f"{userRole}_information"
    form = EmailVerificationForm()

    if request.method == 'POST':
        gender = request.form.get("gender")
        program = request.form.get("program")
        matric_no = request.form.get("matric_no")
        department = request.form.get("department")
        level = request.form.get("level")
        phone_number = request.form.get("phone_number")
        dob = request.form.get("dob")
        state = request.form.get("state")
        address = request.form.get("address")

        try:
            if not gender or not program or not matric_no or not department or not level or not phone_number or not dob or not state or not address:
                raise ValueError("Error: Missing Information. Ensure you fill all the field")

            if not user_uid:
                raise ValueError("Unable to fetch user id")

            user_data = get_user_data(user_uid, userRole)

            if not user_data:
                flash('Error: Failed to get client data', "danger")
                return redirect(url_for('auth.clientLogin', userRole=userRole))

            student_bind_id = getattr(user_data, "student_bind_id", None) or "None"
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()

            if student_bind_id is None or student_bind_id == "None":
                flash("An Error Occurred Please login again.", "danger")
                return redirect(url_for("auth.clientLogin", userRole=userRole))

            student_info = StudentInfo(
                    student_id=student_bind_id,
                    dob=dob_date,
                    gender=gender,
                    phone_number=phone_number,
                    marticno=matric_no,
                    dept=department,
                    level=level,
                    state=state,
                    address=address,
                    program=program
            )

            db.session.add(student_info)

            # Commit the changes
            db.session.commit()

            if userRole == "students":
                return redirect(url_for("auth.clientFaceScan", userRole=userRole, user_uid=user_uid))

        except (firebase_auth.InvalidIdTokenError, FirebaseError, Exception, ValueError) as e:
            db.session.rollback()

            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return redirect(url_for("auth.clientLogin", userRole=userRole))
    return render_template("auth.html", title=title, form=form, viewType=viewType)


@auth.route("/<userRole>/email_verification/<user_uid>/<token>", methods=["GET"])
def verify_email(userRole, user_uid, token):
    """ This is a function that handle email verification """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404


    title = f"SACOETEC PROPERTY | {userRole.upper()} | Email Vertification"
    viewType = "EmailVerification"

    try:
        if not user_uid:
            raise ValueError("Unable to fetch user id")

        user_data = get_user_data(user_uid, userRole)

        if not user_data:
            flash('Error: Failed to get client data', "danger")
            return redirect(url_for('auth.clientLogin', userRole=userRole))

        # Look for the token and the uid representing that document in the Firestore database
        email_verf_key = f'email_{user_uid}'
        email_verify_record = EmailVerification.query.filter_by(email_key=email_verf_key).first()

        # Check if the token matches the one in the URL
        if email_verify_record and email_verify_record.token != token:
            raise FirebaseError("auth/invalid-token", "Invalid verification token. Please login.")

        # Convert the 'expiresAt' string to a datetime object
        expires_at = email_verify_record.expiresAt

        # Check if the token has expired
        if expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            flash("Verification token has expired. Please login again.", "danger")
            return redirect(url_for("auth.resend_verification", userRole=userRole))

        # Get location from IP
        user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        if user_ip and ',' in user_ip:
            user_ip = user_ip.split(',')[0].strip()

        match = re.search(r'::ffff:(\d+\.\d+\.\d+\.\d+)', user_ip)
        if match:
            user_ip = match.group(1)

        print('UserIP Address: ', user_ip)

        user_location = get_location_from_ip(user_ip, IPINFO_API_TOKEN)

        if not user_location:
            flash("An error occured. Please try again later.", "danger")
            print('An error occureds. Please try again later.')
            return redirect(url_for('auth.clientLogin', userRole=userRole))

        current_latitude = user_location['latitude']
        current_longitude = user_location['longitude']
        previous_latitude = previous_latitude = getattr(user_data, "previous_latitude", None) or "None"
        previous_longitude = getattr(user_data, "previous_longitude", None) or "None"

        # Get the current time and the previous 'last_logged_in' and user,s location
        current_time = datetime.utcnow()  # Current time in UTC
        previous_last_logged_in = getattr(user_data, "last_logged_in", None) or "None"


        # Update the email_verify status to verify
        user_data.email_verify = "Verfied"
        user_data.current_latitude = current_latitude
        user_data.current_longitude = current_longitude
        user_data.previous_latitude = previous_latitude
        user_data.previous_longitude = previous_longitude
        user_data.last_logged_in = current_time
        user_data.previous_last_logged_in = previous_last_logged_in

        # Delete the email verify token
        db.session.delete(email_verify_record)

        # Commit the changes
        db.session.commit()

        return render_template("auth.html", title=title, viewType=viewType)

    except (firebase_auth.InvalidIdTokenError, FirebaseError, Exception, ValueError) as e:
        db.session.rollback()

        error_message = handle_error_msg(e)
        flash(error_message, "danger")
        return redirect(url_for("auth.resend_verification", userRole=userRole))


@auth.route("/<userRole>/face-scan/", defaults={'user_uid': None}, methods=["GET", "POST"])
@auth.route("/<userRole>/face-scan/<user_uid>", methods=["GET", "POST"])
def clientFaceScan(userRole, user_uid):
    """ This is a function that handle the face scan of the user """
    from website.celery.tasks import upload_file_to_firebase_task

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC PROPERTY | {userRole.upper()} | Face Scan"
    viewType = "FaceScan"

    return render_template("auth.html", title=title, user_uid=user_uid, viewType=viewType, userRole=userRole)


@auth.route("/<userRole>/process-face-scan", methods=["POST"])
@auth.route("/<userRole>/process-face-scan/<user_uid>", methods=["POST"])
def processFaceScan(userRole, user_uid=None):
    """Handle the face scan of the user"""
    from website.celery.tasks import upload_file_to_firebase_task

    # Define valid user roles
    valid_roles = ['students']

    # Validate user role
    if userRole not in valid_roles:
        return jsonify({"error": "Invalid user role"}), 400

    if request.method == "POST":
        try:
            data = request.json
            image_data = data.get("scanResult")
            face_scan_key = data.get("faceScanKey")

            if not image_data or not face_scan_key:
                return jsonify({"error": "Missing required data"}), 400

            print("image_data: ", image_data)
            print("face_scan_key: ", face_scan_key)

            face_image_filename = secure_filename(f"{face_scan_key}.png")
            face_image_dir = "Event_Face_Recongition/faces/"
            face_image_path = os.path.join(face_image_dir, face_image_filename)

            if not os.path.exists(face_image_dir):
                os.makedirs(face_image_dir)

            try:
                if ',' in image_data:
                    image_data = image_data.split(",")[1]

                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                return jsonify({"error": "Invalid Base64 image data", "details": str(e)}), 400

            with open(face_image_path, "wb") as img_file:
                img_file.write(image_bytes)

            # Process image with face_recognition
            image = face_recognition.load_image_file(face_image_path)
            face_encodings = face_recognition.face_encodings(image)

            if not face_encodings:
                os.remove(face_image_path)
                return jsonify({"error": "No face detected in the image"}), 400

            #if len(face_encodings) > 0:
            # Save face encoding to the database
            student_data = get_user_data(face_scan_key, userRole)

            if not student_data:
                os.remove(face_image_path)
                return jsonify({"error": "User not found"}), 404

            student_bind_id = student_data.student_bind_id
            student_data.face_encoding = json.dumps(face_encodings[0].tolist())
            db.session.commit()

            # Upload profile picture using Celery
            upload_file_to_firebase_task.delay(
                file_data=base64.b64encode(image_bytes).decode('utf-8'),
                file_key="photo_url",
                content_type="image/png",
                file_path=face_image_path,
                task_role="student_info",
                task_key=student_bind_id
            )

            # 🗑️  Delete the local file after processing
            if os.path.exists(face_image_path):
                os.remove(face_image_path)

            return jsonify({
                "success": True,
                "message": "Face registered successfully!",
                "redirect_url": f"https://8ef3-2a00-23a8-c03-1a01-596d-5e0e-577c-c612.ngrok-free.app/students/dashboard/{face_scan_key}"})

            #else:
                # 🗑️  Delete the local file after processing
            #    if os.path.exists(face_image_path):
            #        os.remove(face_image_path)
            #    return jsonify({"error": "No face detected. Try again."}), 400

        except Exception as e:
            print("Error processing image:", str(e))
            return jsonify({"error": "Internal server error", "details": str(e)}), 500


@auth.route("/<userRole>/forgot-password", methods=['GET', 'POST'])
def clientForgotPassword(userRole):
    """ This is a function that handles the forgot password of the patients """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC PROPERTY | {userRole.upper()} | Forgot Password"
    viewType = "ForgotPassword"
    form = ForgottenPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():

        # Get the email from the form
        email = request.form.get('email')

        # Generate a new verification token
        #user_record = firebase_auth.get_user_by_email(email)
        user_record = get_user_by_email_firebase(email)
        if not user_record:
            flash("User not found. Please register again", "danger")
            return redirect(url_for('auth.clientForgotPassword', userRole=userRole))

        user_uid = user_record.uid

        # Fetched the user data
        user_data = get_user_data(user_uid, userRole)

        if not user_data:
            flash("No data found associated with this email. Please register again", "danger")
            return redirect(url_for("auth.clientForgotPassword", userRole=userRole))


        # Generate a new token and resend the verification email
        token = secrets.token_urlsafe(16)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=4)

        # Update the email_verifications collection with the new token
        reset_pwd_key = f"reset_pwd_{user_uid}"

        reset_pwd_record_to_delete = ResetVerification.query.filter_by(reset_pwd_key=reset_pwd_key).first()

        if reset_pwd_record_to_delete:
            db.session.delete(reset_pwd_record_to_delete)

        reset_pwd_session = ResetVerification(
                    reset_pwd_key=reset_pwd_key,
                    token=token,
                    email=email,
                    expiresAt=expires_at,
                    created_at=datetime.utcnow()
        )

        db.session.add(reset_pwd_session)
        db.session.commit()

        # Send verification email
        link = url_for('auth.reset_password', userRole=userRole, user_uid=user_uid, token=token,  _external=True)
        template_title = "Reset Password Notification"
        name = user_data['name']
        message = (
                "We received a request to reset your account password. If this was you, please click the button below to securely reset your password"
                "If you did not request a password reset, please ignore this email or contact our support team immediately."
        )
        action = "reset Your Password"
        send_alert_email(template_title, name, message, action, link, email)


        # Using a secure random token for the session
        #auth_token = firebase_auth.create_custom_token(user_uid).decode('utf-8')
        auth_token = firebase_auth.create_custom_token(user_uid).decode()

        # Store session token in cookies
        response = make_response(redirect(url_for('auth.clientForgotPassword', userRole=userRole)))
        response.set_cookie('auth_token', auth_token, httponly=True, secure=False, max_age=3600)

        flash("Reset Password link was been sent!. Please check your inbox.", "info")
        return response

    return render_template("auth.html", title=title, form=form, viewType=viewType, userRole=userRole)


@auth.route("/<userRole>/reset-password/<user_uid>/<token>", methods=['GET', 'POST'])
def reset_password(userRole, user_uid, token):
    """ This is a function that handle reset paasword """

    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC PROPERTY | {userRole.upper()} | Reset Password Verification"
    viewType = "resetPasswordVerification"
    #user_uid = None

    form = ResetPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():

        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate passwords
        if password != confirm_password:
            flash('Passwords do not match. Please try again.', 'danger')
            return render_template('auth.html', userRole=userRole, token=token, viewType=viewType, title=title)

        try:
            user_data = get_user_data(user_uid, userRole)

            if not user_data:
                flash('Error: Failed to get client data')
                return redirect(url_for('auth.clientLogin', userRole=userRole))

            # Look for the token and the uid representing that document in the Firestore database
            # Query the email_verifications collection for the token
            reset_pwd_key = f"reset_pwd_{user_uid}"
            reset_pwd_record = ResetVerification.query.filter_by(reset_pwd_key=reset_pwd_key).first()

            # Check if the token exists
            if not reset_pwd_record:
                 raise FirebaseError("auth/invalid-token", "Invalid or expired verification token. Please login.")

            #user_veri_data = json.loads(user_veri_data)

            # Check if the token matches the one in the URL
            if reset_pwd_record.token != token:
                raise FirebaseError("auth/invalid-token", "Invalid verification token. Please login.")

            # Convert the 'expiresAt' string to a datetime object
            #expires_at = datetime.fromisoformat(reset_pwd_record.expiresAt)
            expires_at = reset_pwd_record.expiresAt.astimezone(timezone.utc)

            # Check if the token has expired
            if expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                flash("Verification token has expired. Please login again.", "danger")
                return redirect(url_for("auth.resend_verification", userRole=userRole))

            # Update the user's password
            firebase_auth.update_user(user_uid, password=password)

            # Inform the user that the verification was successful
            flash("Your password was updated successfully!", "success")
            return redirect(url_for("auth.clientLogin", userRole=userRole))
        except (firebase_auth.InvalidIdTokenError, FirebaseError, firebase_admin.auth.AuthError, ValueError, Exception) as e:
            current_app.logger.error(f'Error: {e}')
            # Undo changes if something fails
            user = firebase_auth.get_user(user_uid)
            old_password_hash = user.password_hash
            firebase_auth.update_user(user_uid, password=old_password_hash)

            # Handle general exceptions with a different messageresend_verification
            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return render_template('auth.html', token=token, form=form, userRole=userRole, viewType=viewType, title=title)

    return render_template('auth.html', token=token, form=form, userRole=userRole, viewType=viewType, title=title)


@auth.route("/<userRole>/resend-verification", methods=['GET','POST'])
def resend_verification(userRole):
    """ Resends the verification email if a user hasn't verified their email """

    # Define the valid user roles
    valid_roles = ['students']

    # Check if the provided userRole is valid
    if userRole not in valid_roles:
        # Redirect to a 404 page if userRole is invalid
        return render_template("404.html"), 404

    title = f"SACOETEC PROPERTY | {userRole.upper()} | Resend Email Verification"
    viewType = "resend-verification"
    form = ResendEmailVerificationForm()

    firebase_app = firebase_admin.get_app("telemedical")

    # and form.validate_on_submit()

    if request.method == 'POST':

        try:
            # Get the email from the form
            email = request.form.get('email')

            # Generate a new verification token
            try:
                #user_record = firebase_auth.get_user_by_email(email)
                user_record = get_user_by_email_firebase(email)
                user_uid = user_record.uid
            except firebase_auth.UserNotFoundError:
                flash("User not found. Please register again", "danger")
                return redirect(url_for('auth.clientRegister', userRole=userRole))

            # Fetch user from Firestore by email
            user_data = get_user_data(user_uid, userRole)

            if not user_data:
                flash("No data found associated with this email. Please register again", "danger")
                return redirect(url_for("auth.clientRegister", userRole=userRole))

            # Check the email if is verifed
            if user_data.email_verify == "Verfied":
                flash("Your email is already verified. Please login", "success")
                return redirect(url_for("auth.clientLogin", userRole=userRole))

            # Update the email_verifications collection with the new token
            email_verf_key = f'email_{user_uid}'

            email_record_to_delete = EmailVerification.query.filter_by(email_key=email_verf_key).first()

            if email_record_to_delete:
                db.session.delete(email_record_to_delete)

            token = secrets.token_urlsafe(16)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=4)


            email_veriff_session = EmailVerification(
                    email_key=email_verf_key,
                    token=token,
                    email=email,
                    expiresAt=expires_at,
                    create_date=datetime.utcnow()
            )

            db.session.add(email_veriff_session)
            db.session.commit()

            # Construct the mail template
            template_title = 'Account Re-Activation Link'
            name = user_data.name
            message = "We noticed that you haven't accessed your account in a while. We miss you! To continue enjoying our services,"
            action = 'reactivate your account'
            email = user_data.email
            link = url_for('auth.verify_email', token=token, userRole=userRole, user_uid=user_uid, _external=True)

            send_alert_email(template_title, name, message, action, link, email)

            # Using a secure random token for the session
            #auth_token = firebase_auth.create_custom_token(user_uid).decode('utf-8')
            auth_token = generate_auth_token(user_uid)

            # Store session token in cookies
            response = make_response(redirect(url_for('auth.resend_verification', userRole=userRole)))
            response.set_cookie('auth_token', auth_token, httponly=True, secure=False, max_age=3600)

            flash("Verification email resent. Please check your inbox.", "success")
            return response
        except Exception as e:
            print("Error: ", e)
            # Handle general exceptions with a different messageresend_verification
            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return redirect(url_for("auth.clientLogin", userRole=userRole))

    return render_template("auth.html", userRole=userRole, form=form, title=title, viewType=viewType)
