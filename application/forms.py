from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, NumberRange, ValidationError, Optional
from application.models import User
import re


def is_bestbuy_domain(form, field):
    url = field.data
    valid_domain_regex = re.compile(
        r'(bestbuy.com).+(skuId=)(\d{7})', re.IGNORECASE)
    mo = valid_domain_regex.search(url)
    if not mo:
        raise ValidationError('Please enter a valid BestBuy URL.')


def has_special_characters(form, field):
    characters_regex = re.compile(r'^[a-zA-Z0-9\-_.]+$')
    mo = characters_regex.search(field.data)
    if mo is None:
        raise ValidationError('Valid characters are A-Z a-z 0-9 . _ -')


def is_unique_username(form, field):
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('Username has already been taken.')


def is_unique_email(form, field):
    if User.query.filter_by(email=field.data).first():
        raise ValidationError('Email has already been taken.')


class ProductInfoForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(),
                                         URL(),
                                         is_bestbuy_domain])
    price_cutoff = DecimalField('Price Cutoff', places=2, validators=[DataRequired(),
                                                                      NumberRange(min=0)])
    submit = SubmitField('Track Item')


class NewPriceCutoffForm(FlaskForm):
    price_cutoff = DecimalField('Price Cutoff', places=2, validators=[DataRequired(),
                                                                      NumberRange(min=0)])
    submit = SubmitField('Submit Changes')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(min=4, max=30),
                                                   has_special_characters,
                                                   is_unique_username])

    email = StringField('Email', validators=[DataRequired(),
                                             Email(),
                                             is_unique_email])

    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm_password',
                                                             message='Passwords must match.')])

    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log In')
