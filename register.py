from flask import request, render_template, flash, redirect, url_for, Blueprint
from config import app, conn
from forms import RegisterCustomerForm, RegisterAgentForm, RegisterStaffForm

register_bp = Blueprint("register", __name__, static_folder="static", template_folder="templates")


@register_bp.route('/')
def register_page():
    return render_template('register/register.html')


@register_bp.route('/customer', methods=['GET', 'POST'])
def register_customer():
    form = RegisterCustomerForm()
    if request.method == "POST":
        if form.validate_on_submit():
            name = form['name'].data
            email = form['email'].data
            password = form['password'].data
            building_number = form['building_number'].data
            street = form['street'].data
            city = form['city'].data
            state = form['state'].data
            phone_number = form['phone_number'].data
            passport_number = form['passport_number'].data
            passport_expiration = form['passport_expiration'].data
            passport_country = form['passport_country'].data
            date_of_birth = form['birth'].data
            cursor = conn.cursor()
            q = """INSERT INTO customer (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`)
                                VALUES (%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s) 
                            """

            '''
            q = """INSERT INTO customer (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, 
            `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES (
            'alustig2003@gmail.com', 'andrew', md5('abcdefg'), 123, 'abc', 'abc', 'abc', 123, 'abc', '2001-10-15','absb',
            '2001-10-15');"""
            '''
            try:
                cursor.execute(q, (
                    email, name, password, building_number, street, city, state, phone_number, passport_number,
                    passport_expiration, passport_country, date_of_birth))
                conn.commit()
                cursor.close()
                flash(f'Success! You are registered as customer: {email}', category='success')
                flash('Continue on to login', category='success')
                return redirect(url_for('login_page'))
            except Exception as e:
                print(e)
                flash('Registration failed! Please try again', category='danger')
    return render_template('register/register_customer.html', form=form)


@register_bp.route('/agent', methods=['GET', 'POST'])
def register_agent():
    form = RegisterAgentForm()
    if form.validate_on_submit():
        email = form['email'].data
        password = form['password'].data
        booking_agent_id = form['booking_agent_id'].data
        try:
            cursor = conn.cursor()
            q = """INSERT INTO booking_agent (`email`, `password`, `booking_agent_id`) VALUES (%s, md5(%s), %s)
                            """
            cursor.execute(q, (email, password, booking_agent_id))
            conn.commit()
            cursor.close()

            flash(f'Success! You are registered as agent: {email}', category='success')
            flash('Continue on to login', category='success')
            return redirect(url_for('login_page'))
        except Exception as e:
            print(e)
            flash('Registration failed! Please try again', category='danger')
    return render_template('register/register_agent.html', form=form)


@register_bp.route('/staff', methods=['GET', 'POST'])
def register_staff():
    form = RegisterStaffForm()
    if form.validate_on_submit():
        username = form['username'].data
        password = form['password'].data
        firstName = form['firstName'].data
        lastName = form['lastName'].data
        date_of_birth = form['birth'].data
        airline_name = form['airline'].data
        try:
            cursor = conn.cursor()
            q = """INSERT INTO airline_staff (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`)
                            VALUES (%s, md5(%s), %s, %s, %s, %s)
                        """
            cursor.execute(q, (username, password, firstName, lastName, date_of_birth, airline_name))
            conn.commit()
            cursor.close()
            flash(f'Success! You are registered as staff: {username}', category='success')
            flash('Continue on to login', category='success')
            return redirect(url_for('login_page'))
        except:
            flash('Registration failed! Please try again', category='danger')
    return render_template('register/register_staff.html', form=form)
