import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError


class RegisterForm(FlaskForm):
    apple_id = StringField(label='Apple ID:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=6, max=50), DataRequired()])
    credit_card = IntegerField(label='Credit Card Number:', validators=[DataRequired()])
    submit = SubmitField(label='Create Account')
class LoginForm(FlaskForm):
    apple_id = StringField(label='Apple ID:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=6, max=50), DataRequired()])
    submit = SubmitField(label='Sign in')

