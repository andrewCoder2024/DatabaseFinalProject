from datetime import date, timedelta

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import pymysql as sql
import pymysql.cursors


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ec9439cfc6c796ae20295943'
conn = sql.connect(host='127.0.0.1',
                   user='root',
                   password='',
                   db='ScannerDB',
                   unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
                   charset='utf8mb4',
                   cursorclass=pymysql.cursors.DictCursor)
from register import register_bp
app.register_blueprint(register_bp, url_prefix="/register")
