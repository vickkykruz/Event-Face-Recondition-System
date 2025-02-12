""" This is a module that handle thoes helpers functions """
import json
from dotenv import load_dotenv
from os import path, environ, getenv
import requests
from website.clients.models.models import Students, StudentInfo
from flask import request, redirect, flash, url_for, make_response, current_app, session
from firebase_admin import auth as firebase_auth, storage, firestore
import base64
import random


# Load environment variables once at startup
load_dotenv()


def handle_error_msg(e):
    """ This is function that handle the display of error msg """

    error_message = str(e)
    print('Error Msg', error_message)

    # Find the JSON part of the error message
    try:
        # Extract the part of the message that starts with '{' (JSON error)
        json_start_index = error_message.find('{')
        if json_start_index != -1:
            # Parse the JSON part of the error message
            error_json = json.loads(error_message[json_start_index:])

            # Extract the "message" field from the JSON
            error_message_to_user = error_json.get("error", {}).get("message", "An unknown error occurred.")
            #print('Extracted Error:', error_message_to_user)  # For debugging

            # Flash the extracted message to the user
            return f"Error: {error_message_to_user}"
        else:
            return "An unexpected error occurred. Please try again."
    except json.JSONDecodeError:
            return "An error occurred while processing your request."

def decode_base64url(data):
    """Helper function to decode base64url-encoded strings."""
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    return base64.urlsafe_b64decode(data).decode('utf-8')


def is_custom_token(token):
    """
    Check if the token passed is likely a custom token.
    Custom tokens have a different structure and content compared to ID tokens.
    This function examines the token format, header, and payload.
    """
    # Split the token into header, payload, and signature
    token_parts = token.split('.')

    # Custom tokens do not follow the standard JWT format (i.e., they don't have 3 parts).
    if len(token_parts) != 3:
        return True  # It's likely a custom token due to irregular format

    try:
        # Decode and inspect the JWT header
        header_json = decode_base64url(token_parts[0])
        header = json.loads(header_json)

        # Decode and inspect the JWT payload
        payload_json = decode_base64url(token_parts[1])
        payload = json.loads(payload_json)

        # Check the issuer (`iss`) field in the payload:
        if payload.get("iss").startswith("https://accounts.google.com") or \
                payload.get("iss").startswith("https://securetoken.google.com/"):
            # This is an ID token, as it's issued by Firebase Authentication
            return False

        # Check the audience (`aud`) field in the payload:
        if payload.get("aud") == "https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit":
            # This indicates it's likely a custom token, as the audience points to Identity Toolkit
            return True

    except Exception as e:
        # If decoding fails, assume it's a custom token
        print(f"Error decoding token: {e}. Assuming custom token.")
        return True

    # If it has the proper structure but does not contain Firebase-specific claims, assume custom token
    return True


def exchange_custom_token_for_id_token(custom_token):
    """
    Exchange a custom token for an ID token using Firebase Client SDK.
    """
    try:
        # Sign in with the custom token using the Firebase Client SDK
        user = current_app.firebase_auth.sign_in_with_custom_token(custom_token)
        # Get the ID token from the user's details
        id_token = user['idToken']
        return id_token
    except requests.exceptions.HTTPError as e:
        #print("Error: ", e)
        #print(f"Error exchanging custom token: {e}")
        return None


def decode_token(auth_token):
    """
    This function we want to handle three process
    1. Checking for a the token if is as followed
      a). Custom token
      b). Google O-auth tohen
      c). Firebase ID Token

    Step 2
      a). If it is a custom token, converting the custom token to Firebase ID token for verification
      b) If it is a Google O-auth token, converting the Google O-auth token to custom token then to Firebase ID token for verification.
      c). Verifying the Firebase ID token directly.
    """
    try:
        if is_custom_token(auth_token):
            #print(f"Exchanging custom token: {auth_token}")
            # If it's a custom token, exchange it for an ID token using the Firebase Client SDK
            id_token = exchange_custom_token_for_id_token(auth_token)
            if not id_token:
                return "Failed to exchange custom token for ID token."
        else:
            # It's already an ID token, so use it directly
            id_token = auth_token

        decoded_token = firebase_auth.verify_id_token(id_token)
        return decoded_token

    except firebase_auth.ExpiredIdTokenError:
        #print('Error: Token has expired')
        #print(traceback.format_exc())
        return "Token has expired."
    except firebase_auth.InvalidIdTokenError:
        #print('Error: Invalid token provided.')
        #print(traceback.format_exc())
        return "Invalid token provided."
    except ValueError as e:
        #print('Error: Invalid token provided.')
        #print(traceback.format_exc())
        return "Invalid token provided."
    except Exception as e:
        #print('Error: ', e)
        #print(traceback.format_exc())
        return f"An error occurred while decoding the token: {e}"


def get_user_uid_from_token(token=None):
    """ This is a function that fetchs the user data """

    # If token is provided, use it, otherwise get from cookies
    auth_token = token if token else request.cookies.get('auth_token')

    if not auth_token:
        return None

    # Retrieve session document from Firestore
    decoded_token = decode_token(auth_token)

    if isinstance(decoded_token, str):  # If it's a string, it's an error message
        return None

    # If we have a valid decoded token, process it
    user_uid = decoded_token['uid']
    return user_uid



def update_firebase_name_profile(id_token, display_name):
    """ This is a function a request to update the user display name """

    # Load environment variables from .env file
    load_dotenv()

    # Ensure you have your Measurement ID and API Secret from Firebase Analytics
    API_KEY = environ.get('FIREBASE_APIKEY')

    API_URL = "https://identitytoolkit.googleapis.com/v1/accounts:update?key={}".format(API_KEY)

    payload = {
        "idToken": id_token,
        "displayName": display_name,
        "returnSecureToken": True
    }

    headers = {
        "Content-Type": "application/json"
,    }

    response = requests.post(API_URL, json=payload, headers=headers)

    # Debug print to check the type of response
    # print("Type of response:", type(response))
    # print("Response status code:", response.status_code)

    # if isinstance(response, requests.Response):
    if response.status_code == 200:
        # return response.json()  # Successfully updated profile
        return response.status_code
    else:
        raise Exception(f"Failed to update profile: {response.json()}")


def send_alert_email(template_title, name, message, action, link, recipient_email):
    """ This is a function that construct the mail """
    from website.celery.tasks import send_mail

    # Construct the mail body using the mail template
    mail_body = mail_template(template_title, name, message, action, link)

    # Define the message structure
    msg = {
        "subject": f"Notification: {template_title}",
        "sender": "noreply@sacoeteccscdept.com.ng",
        "recipients": [recipient_email],
        "body": mail_body
    }

    # Send the email asynchronously
    return send_mail.delay(msg)


def mail_template(title, name, message, action, link=None):
    """ This is a mail template function """

    redirectLink = link if link else '#'

    body = r"""
        <!doctype html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">

<head>
    <title>

    </title>
    <!--[if !mso]><!-- -->
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <!--<![endif]-->
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style type="text/css">
        #outlook a {{
            padding: 0;
        }}

        .ReadMsgBody {{
            width: 100%;
        }}

        .ExternalClass {{
            width: 100%;
        }}

        .ExternalClass * {{
            line-height: 100%;
        }}

        body {{
            margin: 0;
            padding: 0;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }}

        table,
        td {{
            border-collapse: collapse;
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}

        img {{
            border: 0;
            height: auto;
            line-height: 100%;
            outline: none;
            text-decoration: none;
            -ms-interpolation-mode: bicubic;
        }}

        p {{
            display: block;
            margin: 13px 0;
        }}
    </style>
    <!--[if !mso]><!-->
    <style type="text/css">
        @media only screen and (max-width:480px) {{
            @-ms-viewport {{
                width: 320px;
            }}
            @viewport {{
                width: 320px;
            }}
        }}
    </style>
    <!--<![endif]-->
    <!--[if mso]>
        <xml>
        <o:OfficeDocumentSettings>
          <o:AllowPNG/>
          <o:PixelsPerInch>96</o:PixelsPerInch>
        </o:OfficeDocumentSettings>
        </xml>
        <![endif]-->
    <!--[if lte mso 11]>
        <style type="text/css">
          .outlook-group-fix {{ width:100% !important; }}
        </style>
        <![endif]-->


    <style type="text/css">
        @media only screen and (min-width:480px) {{
            .mj-column-per-100 {{
                width: 100% !important;
            }}
        }}
    </style>


    <style type="text/css">
    </style>

</head>

<body style="background-color:#f9f9f9;">


    <div style="background-color:#f9f9f9;">


        <!--[if mso | IE]>
      <table
         align="center" border="0" cellpadding="0" cellspacing="0" style="width:600px;" width="600"
      >
        <tr>
          <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">
      <![endif]-->


        <div style="background:#f9f9f9;background-color:#f9f9f9;Margin:0px auto;max-width:600px;">

            <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#f9f9f9;background-color:#f9f9f9;width:100%;">
                <tbody>
                    <tr>
                        <td style="border-bottom:#4099ff solid 5px;direction:ltr;font-size:0px;padding:20px 0;text-align:center;vertical-align:top;">
                            <!--[if mso | IE]>
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0">

        <tr>

        </tr>

                  </table>
                <![endif]-->
                        </td>
                    </tr>
                </tbody>
            </table>

        </div>


        <!--[if mso | IE]>
          </td>
        </tr>
      </table>

      <table
         align="center" border="0" cellpadding="0" cellspacing="0" style="width:600px;" width="600"
      >
        <tr>
          <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">
      <![endif]-->


        <div style="background:#fff;background-color:#fff;Margin:0px auto;max-width:600px;">

            <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="background:#fff;background-color:#fff;width:100%;">
                <tbody>
                    <tr>
                        <td style="border:#dddddd solid 1px;border-top:0px;direction:ltr;font-size:0px;padding:20px 0;text-align:center;vertical-align:top;">
                            <!--[if mso | IE]>
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0">

        <tr>

            <td
               style="vertical-align:bottom;width:600px;"
            >
          <![endif]-->

                            <div class="mj-column-per-100 outlook-group-fix" style="font-size:13px;text-align:left;direction:ltr;display:inline-block;vertical-align:bottom;width:100%;">

                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" style="vertical-align:bottom;" width="100%">

                                    <tr>
                                        <td align="center" style="font-size:0px;padding:10px 25px;word-break:break-word;">

                                            <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:collapse;border-spacing:0px;">
                                                <tbody>
                                                    <tr>
                                                        <td style="width:64px;">

                                                            <div class="" style="display: flex; justify-content: center; align-items: center;">
                                                                <img height="auto" src="https://i.ibb.co/0rvqGZj/favicon.png" style="border:0;display:block;outline:none;text-decoration:none;width:100%;" width="64" />
                                                            </div>

                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>

                                        </td>
                                    </tr>

                                    <tr>
                                        <td align="center" style="font-size:0px;padding:10px 25px;padding-bottom:40px;word-break:break-word;">

                                            <div style="font-family:Helvetica Neue,Arial,sans-serif;font-size:28px;font-weight:bold;line-height:1;text-align:center;color:#555;">
                                                {title}
                                            </div>

                                        </td>
                                    </tr>

                                    <tr>
                                        <td align="left" style="font-size:0px;padding:10px 25px;word-break:break-word;">

                                            <div style="font-family:Helvetica Neue,Arial,sans-serif;font-size:16px;line-height:22px;text-align:left;color:#555;">
                                                Hello {name}!<br></br>
                                                {message}. Click the link below to {action}:
                                            </div>

                                        </td>
                                    </tr>

                                    <tr>
                                        <td align="center" style="font-size:0px;padding:10px 25px;padding-top:30px;padding-bottom:50px;word-break:break-word;">

                                            <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="border-collapse:separate;line-height:100%;">
                                                <tr>
                                                    <td align="center" bgcolor="#4099ff" role="presentation" style="border:none;border-radius:3px;color:#ffffff;cursor:auto;padding:15px 25px;" valign="middle">
                                                        <a href="{btnLink}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                                                            <p style="background:#4099ff;color:#ffffff;font-family:Helvetica Neue,Arial,sans-serif;font-size:15px;font-weight:normal;line-height:120%;Margin:0;text-decoration:none;text-transform:none;">
                                                                {btnText}
                                                            </p>
                                                        </a>
                                                    </td>
                                                </tr>
                                            </table>

                                        </td>
                                    </tr>

                                    <tr>
                                        <td align="left" style="font-size:0px;padding:10px 25px;word-break:break-word;">

                                            <div style="font-family:Helvetica Neue,Arial,sans-serif;font-size:16px;line-height:22px;text-align:left;color:#555;">
                                                <a href="{anochLink}" style="text-decoration: none; color:#4099ff;">{anochText}</a><br><br>
                                                If you have problems, please paste the above URL into your web browser, Or contact your addmistrator if issues araises.
                                            </div>

                                        </td>
                                    </tr>

                                    <tr>
                                        <td align="left" style="font-size:0px;padding:10px 25px;word-break:break-word;">

                                            <div style="font-family:Helvetica Neue,Arial,sans-serif;font-size:14px;line-height:20px;text-align:left;color:#525252;">
                                                Best regards,<br><br> <b>Unlimited Health Managements</b><br>
                                            </div>

                                        </td>
                                    </tr>

                                </table>

                            </div>

                            <!--[if mso | IE]>
            </td>

        </tr>

                  </table>
                <![endif]-->
                        </td>
                    </tr>
                </tbody>
            </table>

        </div>


        <!--[if mso | IE]>
          </td>
        </tr>
      </table>

      <table
         align="center" border="0" cellpadding="0" cellspacing="0" style="width:600px;" width="600"
      >
        <tr>
          <td style="line-height:0px;font-size:0px;mso-line-height-rule:exactly;">
      <![endif]-->


        <div style="Margin:0px auto;max-width:600px;">

            <table align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;">
                <tbody>
                    <tr>
                        <td style="direction:ltr;font-size:0px;padding:20px 0;text-align:center;vertical-align:top;">
                            <!--[if mso | IE]>
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0">

        <tr>

            <td
               style="vertical-align:bottom;width:600px;"
            >
          <![endif]-->

                            <div class="mj-column-per-100 outlook-group-fix" style="font-size:13px;text-align:left;direction:ltr;display:inline-block;vertical-align:bottom;width:100%;">

                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">
                                    <tbody>
                                        <tr>
                                            <td style="vertical-align:bottom;padding:0;">

                                                <table border="0" cellpadding="0" cellspacing="0" role="presentation" width="100%">

                                                    <tr>
                                                        <td align="center" style="font-size:0px;padding:0;word-break:break-word;">

                                                            <div style="font-family:Helvetica Neue,Arial,sans-serif;font-size:12px;font-weight:300;line-height:1;text-align:center;color:#575757;">
                                                                Tai Solarin College Of Education, Omu, Ijebu-Ode, Ogun State, Nigeria.
                                                            </div>

                                                        </td>
                                                    </tr>

                                                    <tr>
                                                        <td align="center" style="font-size:0px;padding:10px;word-break:break-word;">

                                                            <div style="font-family:Helvetica Neue,Arial,sans-serif;font-size:12px;font-weight:300;line-height:1;text-align:center;color:#575757;">
                                                                <a href="" style="color:#575757">Unsubscribe</a> from our emails
                                                            </div>

                                                        </td>
                                                    </tr>

                                                </table>

                                            </td>
                                        </tr>
                                    </tbody>
                                </table>

                            </div>

                            <!--[if mso | IE]>
            </td>

        </tr>

                  </table>
                <![endif]-->
                        </td>
                    </tr>
                </tbody>
            </table>

        </div>


        <!--[if mso | IE]>
          </td>
        </tr>
      </table>
      <![endif]-->


    </div>

</body>

</html>

    """.format(title=title, name=name, message=message, action=action, btnLink=redirectLink, btnText=action, anochLink=redirectLink, anochText=redirectLink)

    return body


def get_user_data(user_uid, userRole):
    """ This function fetches user details based on role """

    if not user_uid or not userRole:
        return None  # Return None if either user_uid or userRole is missing

    try:
        user_data = None  # Initialize variable to avoid undefined reference

        # Fetch data based on user role
        if userRole == "landlords":
            user_data = Landlord.query.filter_by(uid=user_uid).first()
        elif userRole == "tenants":
            user_data = Tenant.query.filter_by(uid=user_uid).first()

        if user_data:
            return user_data
        else:
            print(f"User data not found in DB for UID: {user_uid}, Role: {userRole}")
            return None

    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None


#def get_user_info_data(bind_id, userRole):
#    """ This function fetches user details based on role """
#
#    if not bind_id or not userRole:
#        return None  # Return None if either user_uid or userRole is missing
#
#    try:
#
#        # Fetch data based on user role
#        if userRole == "landlords":
#            user_info = LandlordInfo.query.filter_by(landlord_id=bind_id).first()
#        elif userRole == "tenants":
#            user_info = TenantInfo.query.filter_by(tenant_id=bind_id).first()
#        elif userRole == "properties":
#            user_info = Properties.query.filter_by(secondary_key=bind_id).first()
#
#        if user_info:
#            return user_info
#        else:
#            return None
#
#    except Exception as e:
#        print(f"Error fetching user data: {e}")
#        return None

def get_property_based_on_landlord(landlord_id):
    """ This is a function that list out all the properties the landlords has uploaded """

    if not landlord_id:
        return None

    properties = Properties.query.filter_by(landlord_id=landlord_id).all()

    return properties


def get_inboxs_based_bind_id(bind_id):
    """ This is a function that list out all the properties the landlords has uploaded """

    if not bind_id:
        return None

    inboxs = Inbox.query.filter_by(receiver_id=bind_id).all()

    return inboxs

#def fetch_and_shuffle_properties():
#    """ This is a function that get all the propeties, then shuttle it """
#
#    properties = Properties.query.all()  # Fetch all products
#    random.shuffle(properties)        # Shuffle the products
#    return properties

#def get_properties_based_pagination(page=1, per_page=10):
#    """ This is a function that fetch all the properties """
#
#    try:
#        page = int(request.args.get('page', page))  # Get the current page from query params
#        per_page = int(request.args.get('per_page', per_page))  # Get the number of items per page
#        return Properties.query.order_by(Properties.create_date.desc()).paginate(page=page, per_page=per_page)
#    except Exception as e:
#        # Handle invalid page numbers or other errors
#        return None


#def get_property_details(property_id):
#    """ This is a function that get the property details based on the property_id """
#
#    return Properties.query.filter_by(property_bind_id=property_id).first()


#def get_property_images(property_id):
#    """ This is a function that get the property images """
#
#    return PropertiesImages.query.filter_by(property_id=property_id).first()


def get_user_bind_id(landlord_bind_id, userRole):
    """ This is a function that get the landlord details and tenants details """

    if userRole == "landlords":
        user_data = Landlord.query.filter_by(landlord_bind_id=landlord_bind_id).first()

    return user_data
