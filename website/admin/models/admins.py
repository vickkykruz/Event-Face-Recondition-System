""" """

from website.admin.models.models import Admin

# Fetching a user data thorogh their email address
def get_admin_by_email(email):
    """ This return the query data of the search admin """
    return Admin.query.filter_by(email=email).first()


# Fetching the user data through their session bind_id
def get_admin_by_bind_id(bind_id):
    """ This is a function that return the user data as a dictionary """

    try:
        uuid.UUID(bind_id)
    except ValueError:
        raise ValueError("bind id must be a vaild UUID")

    return Admin.query.filter_by(bind_id=bind_id).first()
