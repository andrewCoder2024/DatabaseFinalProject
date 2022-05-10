from datetime import date, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import pymysql as sql
import pymysql.cursors


def last1mon():
    return str((date.today() - timedelta(days=30)).isoformat())


def last6mons():
    return str((date.today() - timedelta(days=180)).isoformat())


def last1year():
    return str((date.today() - timedelta(days=365)).isoformat())


def today():
    return str(date.today().isoformat())


def yearFromNow():
    return str((date.today() + timedelta(days=365)).isoformat())


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae20295943'
conn = sql.connect(host='127.0.0.1',
                   user='root',
                   password='',
                   db='db__final',
                   unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
                   charset='utf8mb4',
                   cursorclass=pymysql.cursors.DictCursor)

from booking_agent import booking_agent_bp
from customer import customer_bp
from register import register_bp
from search import search_bp
from staff import staff_bp

app.register_blueprint(booking_agent_bp, url_prefix="/agent")
app.register_blueprint(customer_bp, url_prefix="/customer")
app.register_blueprint(register_bp, url_prefix="/register")
app.register_blueprint(search_bp, url_prefix="/search")
app.register_blueprint(staff_bp, url_prefix="/staff")
# db = SQLAlchemy(app)
# bcrypt = Bcrypt(app)
# login_manager = LoginManager(app)
# login_manager.login_view = "login_page"
# login_manager.login_message_category = "info"
