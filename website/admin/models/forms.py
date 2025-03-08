from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired
from website.admin.models.utils import get_all_venues


class EventRegistrationForm(FlaskForm):
    """This is the class for the event registration form"""

    # Fetch all the venues
    #all_venues = get_all_venues()

    event_title = StringField("Event Title", validators=[DataRequired()], render_kw={"class": "form-control"})
    event_description = TextAreaField("Event Description", validators=[DataRequired()], render_kw={"class": "form-control", "rows": 3})

    event_date = DateField("Event Date", validators=[DataRequired()], format='%Y-%m-%d', render_kw={"class": "form-control"})
    event_time = TimeField("Event Time", validators=[DataRequired()], format='%H:%M', render_kw={"class": "form-control"})

    department = SelectField("Department", choices=[
        ('', 'Choose your department'),
        ('Accounting', 'Accounting'),
        ('Agricultural Science', 'Agricultural Science'),
        ('Arabic', 'Arabic'),
        ('Biology', 'Biology'),
        ('Business Education', 'Business Education'),
        ('Chemistry', 'Chemistry'),
        ('Christian Religious Studies', 'Christian Religious Studies'),
        ('Computer Science', 'Computer Science'),
        ('Early Childhood & Care Education', 'Early Childhood & Care Education'),
        ('Economics', 'Economics'),
        ('English', 'English'),
        ('Entrepreneurship', 'Entrepreneurship'),
        ('Fine & Applied Arts', 'Fine & Applied Arts'),
        ('French', 'French'),
        ('Geography', 'Geography'),
        ('History', 'History'),
        ('Home Economics', 'Home Economics'),
        ('Integrated Science', 'Integrated Science'),
        ('Islamic Studies', 'Islamic Studies'),
        ('Marketing', 'Marketing'),
        ('Mathematics', 'Mathematics'),
        ('Office & Technology Management', 'Office & Technology Management'),
        ('Physical & Health Education', 'Physical & Health Education'),
        ('Physics', 'Physics'),
        ('Political Science', 'Political Science'),
        ('Primary Education Studies', 'Primary Education Studies'),
        ('Social Studies', 'Social Studies'),
        ('Technical Education (Metal Work, Wood Work, Building)', 'Technical Education (Metal Work, Wood Work, Building)'),
        ('Yoruba', 'Yoruba')
    ], render_kw={"class": "form-select form-select-lg mb-3"})

    level = SelectField("Level", choices=[
        ('100', '100 Level'),
        ('200', '200 Level'),
        ('300', '300 Level'),
        ('400', '400 Level')
    ], render_kw={"class": "form-select form-select-lg mb-3"})

    venue = SelectField("Venue", choices=[], render_kw={"class": "form-select form-select-lg mb-3"})  # Initially empty

    submit = SubmitField("SUBMIT", render_kw={"class": "btn btn-primary btn-lg"})


    def __init__(self, *args, **kwargs):
        """Fetch available venues and populate the dropdown"""
        super(EventRegistrationForm, self).__init__(*args, **kwargs)
        self.venue.choices = [(venue.venue_bind_id, venue.venue_name) for venue in get_all_venues()]

