from config import app, conn
from flask import render_template, redirect, url_for, flash, request, Response
from forms import LoginForm
from flask import session
import cv2
import pyzbar.pyzbar as pyzbar

camera=cv2.VideoCapture(0)
global value 
def read_qr_code(frame):
    try:
        detect = cv2.QRCodeDetector()
        value, points, straight_qrcode = detect.detectAndDecode(frame)
        return value
    except:
        return None
def generate_frames():
    while True:
        ## read the camera frame
        success,frame=camera.read()
        if not success:
            break
        else:
            value = read_qr_code(frame)
            if value:
                print(value)
            ret,buffer=cv2.imencode('.jpg',frame)
            frame=buffer.tobytes()
        yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
@app.route('/home')
def home_page():    
    return render_template('home/home.html')

@app.route('/scanned')
def scanned_page():  
    try:  
        return redirect(value)
    except:
        return redirect(url_for("video"))

@app.route('/video',methods=['GET'])
def video():
    try: 
        return Response(generate_frames(),mimetype='multipart/x-mixed-replace; boundary=frame')
    except:
        return redirect(url_for("scanned_page"))
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

