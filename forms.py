import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField, DateField, IntegerField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from config import today, last1mon, last1year, last6mons

'''
def validate_expiration(form, field):
    if field.data < datetime.datetime.today().strftime('%Y-%m-%d'):
        raise ValidationError("End date must not be earlier than start date.")
'''


class RegisterCustomerForm(FlaskForm):
    name = StringField(label='User Name:', validators=[Length(min=2, max=25), DataRequired()])
    email = StringField(label='Email Address:', validators=[Length(min=2, max=25), Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=6, max=50), DataRequired()])
    confirm = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    building_number = IntegerField('Building Number:', validators=[DataRequired()])
    street = StringField(label='Street:', validators=[Length(min=2, max=30), DataRequired()])
    state = StringField(label='State:', validators=[Length(min=2, max=30), DataRequired()])
    city = StringField(label='City:', validators=[Length(min=2, max=30), DataRequired()])
    phone_number = IntegerField(label='Phone_number:', validators=[DataRequired()])
    passport_number = StringField(label='Passport Number:', validators=[DataRequired()])
    passport_expiration = DateField(label='Passport Expiration:', validators=[DataRequired()])
    passport_country = StringField(label='Passport Country:', validators=[Length(min=2, max=25), DataRequired()])
    birth = DateField(label='DoB:', validators=[DataRequired()])
    submit = SubmitField(label='Create Account')


class RegisterStaffForm(FlaskForm):
    username = StringField(label='User Name:', validators=[Length(min=2, max=25), DataRequired()])
    email = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=6, max=50), DataRequired()])
    confirm = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    firstName = StringField(label='First Name:', validators=[DataRequired()])
    lastName = StringField(label='Last Name:', validators=[DataRequired()])
    birth = DateField(label='DoB:', validators=[DataRequired()])
    airline = StringField(label='Airline Name:', validators=[Length(min=2, max=25), DataRequired()])
    submit = SubmitField(label='Create Account')


class RegisterAgentForm(FlaskForm):
    email = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password = PasswordField(label='Password:', validators=[Length(min=6, max=50), DataRequired()])
    confirm = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    booking_agent_id = IntegerField('Booking Agent ID', validators=[DataRequired()])
    submit = SubmitField(label='Create Account')


class FlightSearchForm(FlaskForm):
    fromCity = StringField("From City", validators=[DataRequired()])
    fromAirport = StringField("From Airport", validators=[DataRequired()])
    fromDate = DateField("From Date", validators=[DataRequired()])
    toCity = StringField("To City", validators=[DataRequired()])
    toAirport = StringField("To Airport", validators=[DataRequired()])
    toDate = DateField("To Date", validators=[DataRequired()])
    submit = SubmitField(label='Search available flights!')


class AgentSalesForm(FlaskForm):
    fromDate = DateField("From Date", validators=[DataRequired()])
    toDate = DateField("To Date", validators=[DataRequired()])
    submit = SubmitField(label='Select dates for commission view')


class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    usertype = SelectField('User Type',
                           choices=['customer', 'agent', 'staff'],
                           validators=[DataRequired()])
    submit = SubmitField(label='Sign in')


class TrackSpendingForm(FlaskForm):
    fromDate = DateField("From Date", validators=[DataRequired()])
    toDate = DateField("To Date", validators=[DataRequired()])
    submit = SubmitField(label='Select Dates for spending tracking')


class PurchaseFlightForm(FlaskForm):
    submit = SubmitField(label='Purchase Flight!')


class AgentPurchaseForm(FlaskForm):
    email1 = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    submit0 = SubmitField(label='Purchase Flight for Customer!')


class AgentFlightsForm(FlaskForm):
    fromDate1 = DateField("Arrival Date", validators=[DataRequired()])
    toDate1 = DateField("Departure Date", validators=[DataRequired()])
    submit1 = SubmitField(label='Change Flight View!')


class CreateFlightsForm(FlaskForm):
    fromDate2 = DateField("Arrival Date", validators=[DataRequired()])
    toDate2 = DateField("Departure Date", validators=[DataRequired()])
    departure_airport_name = StringField(label="Departure Airport name:", validators=[DataRequired()])
    arrival_airport_name = StringField(label="Arrival Airport name:", validators=[DataRequired()])
    status1 = SelectField('Status:',
                          choices=['Upcoming', 'On Time', 'Delayed'],
                          validators=[DataRequired()])
    price = IntegerField(label='Price:', validators=[DataRequired()])
    flight_num1 = IntegerField(label='Flight Number:', validators=[DataRequired()])
    airplaneID = IntegerField(label='Airplane ID:', validators=[DataRequired()])
    submit2 = SubmitField(label='Create Flight!')


class ChangeFlightsStatus(FlaskForm):
    status2 = SelectField('Status:',
                          choices=['Upcoming', 'On Time', 'Delayed'],
                          validators=[DataRequired()])
    flight_num2 = IntegerField(label='Flight Number:', validators=[DataRequired()])
    submit3 = SubmitField(label='Change Flight Status!')


class AddAirplaneForm(FlaskForm):
    seats = IntegerField(label="Number of Seats", validators=[DataRequired()])
    submit4 = SubmitField(label='Add Airplane!')


class AddAirportForm(FlaskForm):
    airport_name = StringField(label="Airport name:", validators=[DataRequired()])
    city = StringField(label="City:", validators=[DataRequired()])
    submit5 = SubmitField(label='Add Airport!')


class AgentReportsForm(FlaskForm):
    fromDate3 = DateField("From Date", validators=[DataRequired()])
    toDate3 = DateField("To Date", validators=[DataRequired()])
    submit6 = SubmitField(label='Select Dates for ticket reports')


class BookingAgentAdditionForm(FlaskForm):
    email2 = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    submit7 = SubmitField(label='Add Agent!')


class AgentPermissionsForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    usertype = SelectField('Permission',
                           choices=['Operator', 'Admin'],
                           validators=[DataRequired()])
    submit8 = SubmitField(label='Give Permission!')
