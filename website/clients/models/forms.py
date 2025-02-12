"""This is a module that handles the forms """
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FileField, IntegerField, TextAreaField, MultipleFileField, TelField, DateField
from wtforms.validators import DataRequired, Length, Email, NumberRange
#from website.clients.models.password_utils import email_or_username

class LoginForm(FlaskForm):
    """ This is a class that handle the Login layout of the form """

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],  # Add the Email validator
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Email",
            "id": "exampleInputEmail1"
        }
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Password",
            "id": "exampleInputPassword1"
        }
    )
    submit = SubmitField(
        'SIGN IN',
        render_kw={
            "class": "btn btn-block bg-info text-white btn-lg font-weight-medium auth-form-btn"
        }
    )


class RegisterForm(FlaskForm):
    """ This is a class that handle the registeration layout of the form """

    username = StringField(
        'Username',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Name",
            "id": "exampleInputEmail1"
        }
    )
    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],  # Add the Email validator
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Email",
            "id": "exampleInputEmail1"
        }
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Password",
            "id": "exampleInputPassword1"
        }
    )
    submit = SubmitField(
        'SIGN IN',
        render_kw={
            "class": "btn btn-block bg-info text-white btn-lg font-weight-medium auth-form-btn"
        }
    )


class ForgottenPasswordForm(FlaskForm):
    """ This is a class that handle the forgotten layout of the form """

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],  # Add the Email validator
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Email",
            "id": "exampleInputEmail1"
        }
    )

    submit = SubmitField(
        'SEND RESET PASSWORD LINK',
        render_kw={
            "class": "btn btn-block bg-info text-white btn-lg font-weight-medium auth-form-btn"
        }
    )


class ResendEmailVerificationForm(FlaskForm):
    """ This is a class that handle the forgotten layout of the form """

    email = StringField(
        'Email',
        validators=[DataRequired(), Email()],  # Add the Email validator
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Email",
            "id": "exampleInputEmail1"
        }
    )

    submit = SubmitField(
        'RESEND EMAIL VERIFICATION LINK',
        render_kw={
            "class": "btn btn-block bg-info text-white btn-lg font-weight-medium auth-form-btn"
        }
    )


class EmailVerificationForm(FlaskForm):
    """ This is a class that handle the email verfication layout of the form """

    gender = SelectField(
        'Gender',
        choices=[
            ('', 'Choose your gender'),
            ('Male', 'Male'),
            ('Female', 'Female')],
        validators=[DataRequired()],
        render_kw={"class": "form-select form-select-lg"}
    )

    program = SelectField(
        'Program',
        choices=[
            ('', 'Choose your program'),
            ('Degree', 'Degree'),
            ('NCE', 'NCE')],
        validators=[DataRequired()],
        render_kw={"class": "form-select form-select-lg"}
    )

    matric_no = StringField(
        'Matric No',
        validators=[DataRequired()],
        render_kw={"class": "form-control form-control-lg", "placeholder": "Matric No"}
    )

    department = SelectField(
        'Department',
        choices=[
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
        ],
        validators=[DataRequired()],
        render_kw={"class": "form-select form-select-lg"}
    )

    level = IntegerField(
        'Level',
        validators=[DataRequired()],
        render_kw={"class": "form-control form-control-lg", "placeholder": "Level"}
    )

    phone_number = TelField(
        'Phone Number',
        validators=[DataRequired()],
        render_kw={"class": "form-control form-control-lg", "placeholder": "Phone Number"}
    )

    dob = DateField(
        'Date of Birth',
        format='%Y-%m-%d',
        validators=[DataRequired()],
        render_kw={"class": "form-control form-control-lg", "placeholder": "DOB"}
    )

    state = StringField(
        'State',
        validators=[DataRequired()],
        render_kw={"class": "form-control form-control-lg", "placeholder": "State"}
    )

    address = StringField(
        'Address',
        validators=[DataRequired()],
        render_kw={"class": "form-control form-control-lg", "placeholder": "Address"}
    )

    submit = SubmitField(
        'SCAN MY FACE',
        render_kw={
            "class": "btn btn-block bg-info text-white btn-lg font-weight-medium auth-form-btn"
        }
    )

class ResetPasswordForm(FlaskForm):
    """ This is a class that handle the registeration layout of the form """

    newPassword = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Password",
            "id": "exampleInputPassword1"
        }
    )

    confirmPassword = PasswordField(
        'Password',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Password",
            "id": "exampleInputPassword1"
        }
    )

    submit = SubmitField(
        'RESET PASSWORD',
        render_kw={
            "class": "btn btn-block bg-info text-white btn-lg font-weight-medium auth-form-btn"
        }
    )


class LandLordRegistrationForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Name",
            "readonly": True
        }
    )
    email = StringField(
        'Email Address',
        validators=[DataRequired(), Email()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Email Address",
            "readonly": True
        }
    )
    phone_number = StringField(
        'Phone Number',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Enter Phone Number"
        }
    )
    profile_pic = FileField(
        'Profile Pic',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg"
        }
    )
    id_type = SelectField(
        'ID Type',
        choices=[
            ('', '--- Choose your document type ----'),
            ('ID Card', 'ID Card'),
            ('Passport', 'Passport'),
            ('Driver License', 'Driver License')
        ],
        validators=[DataRequired()],
        render_kw={
            "class": "form-select form-select-lg mb-3"
        }
    )
    id_doc = FileField(
        'ID Document',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg"
        }
    )
    acc_number = IntegerField(
        'Account Number',
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Bank Account Number"
        }
    )
    bank = SelectField(
        'Bank',
        choices=[
            ('', '--- Choose your bank ----'),
            ('1', 'One'),
            ('2', 'Two'),
            ('3', 'Three')
        ],
        validators=[DataRequired()],
        render_kw={
            "class": "form-select form-select-lg mb-3"
        }
    )
    acc_name = StringField(
        'Account Name',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Bank Account Name"
        }
    )
    submit = SubmitField(
        'SUBMIT',
        render_kw={
            "class": "btn btn-primary btn-lg"
        }
    )


class PropertyForm(FlaskForm):
    # Property Name
    property_name = StringField(
        'Property Name',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Property Name"
        }
    )

    # Property Image
    property_image = FileField(
        'Property Image',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg"
        }
    )

    # Property Type
    property_type = SelectField(
        'Property Type',
        choices=[
            ('', 'Open this select menu'),
            ('Apartment', 'Apartment'),
            ('House', 'House'),
            ('Duplexe and Triplexe', 'Duplexe and Triplexe'),
            ('Condo', 'Condo'),
            ('Shared Accommodations', 'Shared Accommodations')
        ],
        validators=[DataRequired()],
        render_kw={
            "class": "form-select form-select-lg mb-3"
        }
    )

    # Property Address
    property_address = StringField(
        'Property Address',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Address"
        }
    )

    # Property Description
    property_description = TextAreaField(
        'Property Description',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "rows": "3"
        }
    )

    # State
    state = StringField(
        'State',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "State"
        }
    )

    # Number of Bedrooms
    num_bedrooms = IntegerField(
        'Number Of Bedrooms',
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Number Of Bedrooms"
        }
    )

    # Number of Bathrooms
    num_bathrooms = IntegerField(
        'Number Of Bathrooms',
        validators=[DataRequired(), NumberRange(min=1)],
        render_kw={
            "class": "form-control form-control-lg",
            "placeholder": "Number Of Bathrooms"
        }
    )

    # Proof of Ownership
    proof_of_ownership = FileField(
        'Proof Of Ownership',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg"
        }
    )

    # Submit Button
    submit = SubmitField(
        'SUBMIT FORM',
        render_kw={
            "class": "btn btn-primary btn-lg"
        }
    )


class PropertyImagesForm(FlaskForm):
    # Property Images (multiple files)
    property_images = MultipleFileField(
        'Property Images',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control form-control-lg",
            "multiple": True  # Allow multiple file uploads
        }
    )

    # Submit Button
    submit = SubmitField(
        'SUBMIT',
        render_kw={
            "class": "btn btn-primary btn-lg"
        }
    )

