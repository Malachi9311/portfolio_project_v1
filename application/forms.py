from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from application.models import User
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, InputRequired
from flask_login import current_user

class RegistrationForm(FlaskForm):
    """
    Registration page class with all the necessary fields that make it up
    """
    username = StringField('Username', validators=[InputRequired(),Length(min=2, max=20,)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign in')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already in use. Please choose another one')
        
    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is alreadt in use. Please choose another one')

class LoginForm(FlaskForm):
    """
    Login page class with all the necessary fields that make it up
    """
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    """
    Registration page class with all the necessary fields that make it up
    """
    username = StringField('Username', validators=[
                           InputRequired(), Length(min=2, max=20,)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    picture = FileField('To change your Profile Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Submit Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    'That username is already in use. Please choose another one')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is already in use. Please choose another one')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Share Your Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')
