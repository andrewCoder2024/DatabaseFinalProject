from flask import request, render_template, flash, redirect, url_for, Blueprint
from config import app, conn
from forms import RegisterForm

register_bp = Blueprint("register", __name__, static_folder="static", template_folder="templates")


@register_bp.route('/',methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if request.method == "POST":
        if form.validate_on_submit():
            flash('post', category='success')
            apple_id = form['apple_id'].data
            password = form['password'].data
            cc_number = form['credit_card'].data
            cursor = conn.cursor()
            q = """INSERT INTO User (`appleID`, `password`, `credit_card_number`)
                                VALUES (%s, md5(%s), %s) 
                            """
            try:
                cursor.execute(q, (
                    apple_id, password, cc_number))
                conn.commit()
                cursor.close()
                flash(f'Success! You are registered as user: {apple_id}', category='success')
                flash('Continue on to login', category='success')
                return redirect(url_for('login_page'))
            except Exception as e:
                print(e)
                flash('Registration failed! Please try again', category='danger')
    return render_template('register/register.html', form=form)
