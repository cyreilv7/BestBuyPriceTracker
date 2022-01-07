from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, NumberRange, ValidationError
import re
from application.models import User
from application import bcrypt

def special_characters(form, field): 
    characters_regex = re.compile(r'^[a-zA-Z0-9\-_.]+$')
    mo = characters_regex.search(field.data)
    if not mo:
        raise ValidationError('Valid characters are A-Z a-z 0-9 . _ -')

def unique_username(form, field):
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('Username has already been taken.')


def unique_email(form, field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Email has already been taken.')
    

class ProductInfoForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    price_cutoff = DecimalField('Price Cutoff', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Track Item')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=30), special_characters, unique_username])
    email = StringField('Email', validators=[DataRequired(), Email(), unique_email])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')

    # def unique_username(self, username):
    #     if User.query.filter_by(username=username.data).first():
    #         raise ValidationError('Username has already been taken.')

    # def unique_email(self, email):
    #     if User.query.filter_by(email=email.data).first():
    #         raise ValidationError('Email is already being used.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')

