"""
This is a module that define views routes for the users to access...
"""

from flask import Blueprint, render_template, flash, request, redirect, url_for, make_response, current_app, session
#from website.clients.models.forms import LandLordRegistrationForm, PropertyForm, PropertyImagesForm
#from website.clients.models.utils import (
#        get_user_uid_from_token,
#        get_user_data,
#        get_user_info_data,
#        get_property_based_on_landlord,
#        get_inboxs_based_bind_id,
#        fetch_and_shuffle_properties,
#        get_properties_based_pagination,
#        get_property_details,
#        get_property_images,
#        get_user_bind_id)
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

