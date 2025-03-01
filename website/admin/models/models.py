"""
 This is a module that define our database schemer
 """

import uuid
from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class Admin(db.Model, UserMixin):
    """This is a class that contains the tenant auth information."""

    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    admin_bind_id = db.Column(
        db.String(36),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    uid = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    current_latitude = db.Column(db.String(100))
    current_longitude = db.Column(db.String(100))
    previous_latitude = db.Column(db.String(100))
    previous_longitude = db.Column(db.String(100))
    last_logged_in = db.Column(db.String, nullable=True)
    previous_last_logged_in = db.Column(db.String, nullable=True)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class Venues(db.Model):
    """ This is a class the define the schema for venue """

    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    venue_bind_id = db.Column(
        db.String(36),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )
    venue_name = db.Column(db.String(100))
    venue_desc = db.Column(db.String(100))
    venue_address = db.Column(db.String(250))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
