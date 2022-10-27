from config import app, conn
import pymysql as sql
import pymysql.cursors
from flask import session
import register
import routes
# Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(debug=True, port=9998)
