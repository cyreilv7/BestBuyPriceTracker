from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, NumberRange

class ProductInfoForm(FlaskForm):
    url = StringField('URL', validators=[DataRequired(), URL()])
    price_cutoff = DecimalField('Price Cutoff', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Track Item')

class RegistrationForm(FlaskForm):
    pass
