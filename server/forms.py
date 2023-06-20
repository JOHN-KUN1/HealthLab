from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed   # type of file we want to store and what kind of file we want to be updated
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from server.models import User


# FOR OUR REGISTRATION FORM
class RegistrationForms(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=6, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8, max=18)])
    confirmPassword = PasswordField('Confirm Password', validators=[
                                    DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username = username.data).first()

        if user:
            raise ValidationError('That username has been taken. Please choose a new one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user:
            raise ValidationError(
                'That email has been taken. Please choose a new one.')


# FOR OUR LOGIN FORM
class LoginForms(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8, max=18)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Login')

# FOR OUR UPDATE ACCOUNT FORM
class UpdateAccountForms(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=6, max=16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators = [FileAllowed(['png','jpg'])])
    
    submit = SubmitField('Update')

    # checks if username provided is a valid username or if it aleady exists in the database

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()

            if user:
                raise ValidationError(
                    'That username has been taken. Please choose a new one.')

     # checks if email provided is a valid email or if it aleady exists in the database

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()

            if user:
                raise ValidationError(
                    'That email has been taken. Please choose a new one.')


class PostForms(FlaskForm):
    title = StringField('Title', validators = [DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class UserInputForms(FlaskForm):
    type = SelectField('Type', validators=[DataRequired()],
                       choices=[('Gain', 'Gain'),
                                ('Loss', 'Loss')])
    category = SelectField("Category", validators=[DataRequired()],
                           choices=[('Snacks', 'Snacks'),
                                    ('Food', 'Food'),
                                    ]
                           )

    amount = IntegerField('Weight(kg)', validators = [DataRequired()])
    submit = SubmitField("Generate Report") 


# FOR OUR RESET PASSWORD FORM
class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Requst Email Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is None:
            raise ValidationError(
                'There is no account with this email. Please register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8, max=18)])
    confirmPassword = PasswordField('Confirm Password', validators=[
                                    DataRequired(), EqualTo('password')])
    submit = submit = SubmitField('Reset Password')
