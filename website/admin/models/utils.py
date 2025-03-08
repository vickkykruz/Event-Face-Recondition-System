""" """

from website.admin.models.models import Venues, Events, Admin, Attendance
from website.clients.models.models import Students, StudentInfo


def get_admin_data(user_uid):
    """ This function fetches user details based on role """

    if not user_uid:
        return None  # Return None if either user_uid or userRole is missing

    try:
        user_data = None  # Initialize variable to avoid undefined reference

        # Fetch data based on user role
        user_data = Admin.query.filter_by(uid=user_uid).first()

        if user_data:
            return user_data
        else:
            print(f"User data not found in DB for UID: {user_uid}, Role: {userRole}")
            return None

    except Exception as e:
        print(f"Error fetching user data: {e}")
        return None

def get_all_venues():
    """ This is a function that get all the venues """

    return Venues.query.order_by(Venues.id.desc()).all()

def get_venue_details(venue_bind_id):
    """ This is a function that get the venue details """

    return Venues.query.filter_by(venue_bind_id=venue_bind_id).first()

def get_all_events():
    """ This is a function that get all the venues """

    return Events.query.order_by(Events.id.desc()).all()

def get_event_details(venue_bind_id):
    """ This is a function that get the venue details """

    return Events.query.filter_by(event_bind_id=venue_bind_id).first()

def get_selected_students(department, level):
    """ This is a function that get the selected students """

    return Students.query.join(
        StudentInfo, StudentInfo.student_id == Students.student_bind_id
    ).filter(
        StudentInfo.dept == department,
        StudentInfo.level == level
    ).order_by(Students.id.desc()).all()

def get_event_attendance(event_id):
    """ This is a function that fetch all the students who is meant to attend this event """

    return Attendance.query.filter_by(event_id=event_id).all()

