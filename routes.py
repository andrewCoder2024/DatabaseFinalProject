from config import app, conn
from flask import render_template, redirect, url_for, flash, request
from forms import LoginForm
from flask import session


@app.route('/')
@app.route('/home')
def home_page():
    usertype = session.get('usertype')
    if usertype == 'agent':
        return redirect(url_for('booking_agent.agent_home_page'))
    elif usertype == 'staff':
        return redirect(url_for('staff.staff_home_page'))
    elif usertype == 'customer':
        return redirect(url_for('customer.customer_home_page'))
    else:
        return render_template('home/home.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if session.get('username'):
        flash('Already logged in!', category='danger')
        return redirect(url_for("home_page"))
    form = LoginForm()
    if form.validate_on_submit():
        username = form['username'].data
        password = form['password'].data
        usertype = form['usertype'].data
        if usertype == 'customer':
            q = 'SELECT * FROM customer WHERE email = %s and password = md5(%s)'
        elif usertype == 'agent':
            q = 'SELECT * FROM booking_agent WHERE email = %s and password = md5(%s)'
        else:
            q = 'SELECT * FROM airline_staff WHERE username = %s and password = md5(%s)'
        cursor = conn.cursor()
        cursor.execute(q, (username, password))
        res = cursor.fetchone()
        cursor.close()
        if res:
            flash(f'Success! You are logged in as: {username}', category='success')
            session['username'] = username
            session['usertype'] = usertype
            return redirect(url_for('home_page'))
        else:
            flash('Username and password are not a match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    session.clear()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))
