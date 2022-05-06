from config import app, conn
import pymysql as sql
import pymysql.cursors
from flask import session
import register
import customer
import booking_agent
import staff
import routes
conn = sql.connect(host='127.0.0.1',
                   user='root',
                   password='',
                   db='db__final',
                   unix_socket='/Applications/XAMPP/xamppfiles/var/mysql/mysql.sock',
                   charset='utf8mb4',
                   cursorclass=pymysql.cursors.DictCursor)

#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(debug=True, port=9997)