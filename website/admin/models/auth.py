"""
This is a module that define and handle the authenication of the the
adminstrators
"""


from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, make_response
from website import db
from website.admin.models.admins import get_admin_by_email
from website.clients.models.forms import LoginForm
from website.admin.models.utils import get_admin_data
from website.clients.models.utils import (
        handle_error_msg,
        get_user_uid_from_token,
        get_location_from_ip)
from datetime import datetime, timedelta, timezone, time


# Define the BluePrint
adminAuth = Blueprint("adminAuth", __name__, static_folder="website/clients/static", template_folder="website/admin/templates")


@adminAuth.route("/logout")
def logout():
    """This function handles the logout process for all user roles."""

    # Create a response for the logout process
    response = make_response(redirect(url_for('adminAuth.adminLogin', userRole=userRole)))

    # Remove the auth_token cookie
    response.set_cookie('auth_token', '', expires=0, httponly=True, secure=False)
    response.set_cookie('background_session_id', '', httponly=True, secure=False)

    # Flash a message to the user (optional)
    flash('You have successfully logged out.', 'success')
    return response


@adminAuth.route("/login", methods=["GET", "POST"])
def adminLogin():
    """ This a function that handle the login of the admins """

    title = f"SACOETEC Event System | Admin | Login"
    viewType = f"Admin Login"
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

            # Check cache for admin data
            user_data = get_admin_data(user_uid)
            if not user_data:
                raise ValueError("User record not found. Please register first.")

            # Get location from IP
            #user_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

            #if user_ip and ',' in user_ip:
            #    user_ip = user_ip.split(',')[0].strip()

            #match = re.search(r'::ffff:(\d+\.\d+\.\d+\.\d+)', user_ip)
            #if match:
            #    user_ip = match.group(1)

            #print('UserIP Address: ', user_ip)

            #user_location = get_location_from_ip(user_ip, IPINFO_API_TOKEN)

            #if not user_location:
            #    flash("An error occured. Please try again later.", "danger")
            #    print('An error occureds. Please try again later.')
            #    return redirect(url_for('auth.clientLogin', userRole=userRole))

            #current_latitude = user_location['latitude']
            #current_longitude = user_location['longitude']
            #previous_latitude = previous_latitude = getattr(user_data, "previous_latitude", None) or "None"
            #previous_longitude = getattr(user_data, "previous_longitude", None) or "None"

            # Get the current time and the previous 'last_logged_in' and user,s location
            current_time = datetime.utcnow()  # Current time in UTC
            previous_last_logged_in = getattr(user_data, "last_logged_in", None) or "None"

            #user_data.current_latitude = current_latitude
            #user_data.current_longitude = current_longitude
            #user_data.previous_latitude = previous_latitude
            #user_data.previous_longitude = previous_longitude
            user_data.last_logged_in = current_time
            user_data.previous_last_logged_in = previous_last_logged_in

            # Commit the changes
            db.session.commit()


            # Store session token in cookies
            response = make_response(redirect(url_for('adminViews.adminHome')))
            response.set_cookie('auth_token', auth_token, httponly=True, secure=False, max_age=3600)

            flash('You are welcome', 'success')
            return response
        except ValueError as e:
            print(f'Error: {e}')
            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return redirect(url_for('adminAuth.adminLogin'))
        except Exception as e:
            print(f'Error: {e}')
            # Handle general exceptions
            error_message = handle_error_msg(e)
            flash(error_message, "danger")
            return redirect(url_for('adminAuth.adminLogin'))

    return render_template("auth.html", title=title, form=form, viewType=viewType)
