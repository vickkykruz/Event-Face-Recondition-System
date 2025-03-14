"""
 This is a module that define our database schemer
 """

import uuid
from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime


class Students(db.Model, UserMixin):
    """This is a class that contains the tenant auth information."""

    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_bind_id = db.Column(
        db.String(36),
        unique=True,
        default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String(100))
    username = db.Column(db.String(100))
    uid = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    email_verify = db.Column(db.Enum("Verfied", "Not Verified"), default="Not Verified", nullable=True)
    current_latitude = db.Column(db.String(100))
    current_longitude = db.Column(db.String(100))
    previous_latitude = db.Column(db.String(100))
    previous_longitude = db.Column(db.String(100))
    face_encoding = db.Column(db.String, nullable=True)
    last_logged_in = db.Column(db.String, nullable=True)
    previous_last_logged_in = db.Column(db.String, nullable=True)
    #password_hash = db.Column(db.String(128), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class StudentInfo(db.Model):
    """This class contains the tenant information."""

    __tablename__ = 'student_info'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(36), db.ForeignKey(
        'students.student_bind_id',
        ondelete='CASCADE'
    ))
    student = db.relationship(
        'Students',
        backref=db.backref('student_info', cascade='all, delete-orphan'))
    dob = db.Column(db.Date)
    gender = db.Column(
        db.Enum("Male", "Female"))
    phone_number = db.Column(db.String(15))
    marticno = db.Column(db.String(15), unique=True)
    dept = db.Column(db.String(30))
    level = db.Column(db.Integer)
    photo_url = db.Column(db.String(150))
    state = db.Column(db.String(50))
    address = db.Column(db.String(150))
    program = db.Column(
        db.Enum("Degree", "NCE"))
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class EmailVerification(db.Model):
    """This is a class that defines the email verification model."""
    
    __tablename__ = 'email_verifications'

    id = db.Column(db.Integer, primary_key=True)
    email_key = db.Column(db.String(100), nullable=False, index=True)
    token = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    expiresAt = db.Column(db.DateTime(timezone=True), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)

    def __repr__(self):
        return f"<EmailVerification(id={self.id}, email={self.email}, expiresAt={self.expiresAt})>"


class ResetVerification(db.Model):
    """This is a class that defines the reset verification model."""

    __tablename__ = 'reset_verifications'

    id = db.Column(db.Integer, primary_key=True)
    reset_pwd_key = db.Column(db.String(100), nullable=False, index=True)
    token = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=False, index=True)
    expiresAt = db.Column(db.DateTime(timezone=True), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)

    def __repr__(self):
        return f"<ResetVerification(id={self.id}, email={self.email}, expiresAt={self.expiresAt})>"
