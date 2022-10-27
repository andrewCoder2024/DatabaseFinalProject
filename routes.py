from config import app, conn
from flask import render_template, redirect, url_for, flash, request
from forms import LoginForm
from flask import session


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home/home.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if session.get('apple_id'):
        flash('Already logged in!', category='danger')
        return redirect(url_for("home_page"))
    form = LoginForm()
    if form.validate_on_submit():
        apple_id = form['apple_id'].data
        password = form['password'].data
        q = 'SELECT * FROM User WHERE appleID = %s and password = md5(%s)'
        cursor = conn.cursor()
        cursor.execute(q, (apple_id, password))
        res = cursor.fetchone()
        cursor.close()
        if res:
            flash(f'Success! You are logged in as: {apple_id}', category='success')
            session['apple_id'] = apple_id
            return redirect(url_for('home_page'))
        else:
            flash('AppleID and password are not a match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    if session:
        session.clear()
        flash("You have been logged out!", category='info')
        return redirect(url_for("home_page"))
    else:
        session.clear()
        flash("You have not logged in yet!", category='info')
        return redirect(url_for("home_page"))

