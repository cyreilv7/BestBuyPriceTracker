from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, NumberRange, ValidationError
import re


def special_characters(form, field): 
    characters_regex = re.compile(r'^[a-zA-Z0-9\-_.]+$')
    mo = characters_regex.search(field.data)
    if not mo:
        raise ValidationError('Valid characters are A-Z a-z 0-9 . _ -')


class ProductInfoForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    price_cutoff = DecimalField('Price Cutoff', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Track Item')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=6, max=30), special_characters])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password', message='Passwords must match.')])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')

