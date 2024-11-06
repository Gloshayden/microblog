from flask_wtf import FlaskForm # Importing FlaskForm to create forms
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField # importing different form elements
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length # importing different validation
from app import db # Importing database instance
from app.models import User # Importing User model to access user data
from flask_babel import _, lazy_gettext as _l
import sqlalchemy as sa

# Form for user login
class LoginForm(FlaskForm):
    username = StringField(_l('Username', validators=[DataRequired()])) # Username field, required
    password = PasswordField(_l('Password', validators=[DataRequired()])) # Password field, required
    remember_me = BooleanField(_l('Remember Me')) # Checkbox for "remember me" option
    submit = SubmitField(_l('Sign In')) # Submit button for form

# Form for new user registration
class RegistrationForm(FlaskForm):
    username = StringField(_l('Username', validators=[DataRequired()])) # Username field, required
    email = StringField(_l('Email', validators=[DataRequired(), Email()])) # Email field, required and validated as email
    password = PasswordField(_l('password', validators=[DataRequired()]))
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')]) # Confirm password field, must match password
    submit = SubmitField(_l('register'))

    # Custom validation to check if username is unique
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data)) # Query to find existing username
        if user is not None: # rases an error if same username is found
            raise ValidationError(_('Please use a different username'))
    
    # Custom validation to check if email is unique
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data)) # Query to find existing email
        if user is not None: # rases an error if same email is found
            raise ValidationError(_('Please use a different email address'))

# Form for editing user profile
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About Me'), validators=[Length(min=0, max=140)]) # Text area for "About Me", max 140 characters
    submit = SubmitField(_l('Submit'))

    # username validation
    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None: # if the username is not available then raise error
                raise ValidationError(_('Please use a different username'))

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))