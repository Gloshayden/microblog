from flask_wtf import FlaskForm # type:ignore (Importing FlaskForm to create forms)
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField # type: ignore (importing different form elements)
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length # type: ignore (importing different validation)
from app import db # Importing database instance
from app.models import User # Importing User model to access user data
import sqlalchemy as sa # type: ignore

# Form for user login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) # Username field, required
    password = PasswordField('Password', validators=[DataRequired()]) # Password field, required
    remember_me = BooleanField('Remember Me') # Checkbox for "remember me" option
    submit = SubmitField('Sign In') # Submit button for form

# Form for new user registration
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) # Username field, required
    email = StringField('Email', validators=[DataRequired(), Email()]) # Email field, required and validated as email
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]) # Confirm password field, must match password
    submit = SubmitField('register')

    # Custom validation to check if username is unique
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data)) # Query to find existing username
        if user is not None: # rases an error if same username is found
            raise ValidationError('Please use a different username')
    
    # Custom validation to check if email is unique
    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data)) # Query to find existing email
        if user is not None: # rases an error if same email is found
            raise ValidationError('Please use a different email')

# Form for editing user profile
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]) 
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=140)]) # Text area for "About Me", max 140 characters
    submit = SubmitField('Submit')

    # username validation
    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(User.username == username.data))
            if user is not None: # if the username is not available then raise error
                raise ValidationError('Please use a different username')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')