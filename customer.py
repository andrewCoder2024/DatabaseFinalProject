import datetime

from config import app, conn,today,last1mon,last1year,last6mons
from flask import render_template, redirect, url_for, flash, request, session, Blueprint
from forms import LoginForm, TrackSpendingForm
from flask_login import login_user, logout_user, login_required, current_user
from flask import session
from dateutil.relativedelta import relativedelta

customer_bp = Blueprint("customer", __name__,static_folder="static", template_folder="templates")


def total_spending(username, from_date=None, to_date=None):
    cursor = conn.cursor()
    from_date = from_date if from_date else last1year()
    to_date = to_date if from_date else today()
    query = """select SUM(flight.price) as spend from customer 
               inner join purchases on email=customer_email 
               natural join ticket natural join flight 
               where name = 'Customer'
               and purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
            """
    cursor.execute(query, (username, from_date, to_date))
    data = cursor.fetchone()
    cursor.close()
    try:
        return data['TotalSpending']
    except:
        return "Null"


def get_spending_spread(username, from_date=None, to_date=None):
    cursor = conn.cursor()
    from_date = from_date if from_date else last1year()
    to_date = to_date if from_date else today()
    query = """ select SUM(price) as spend, YEAR(purchase_date) as year, 
                MONTH(purchase_date) as month from customer 
                inner join purchases on email=customer_email 
                natural join ticket natural join flight 
                where name = %s
                and purchase_date between date_sub(%s, INTERVAL 2 DAY) 
                and date_sub(%s, INTERVAL 2 DAY)
                GROUP BY year, month
                ORDER BY purchases.purchase_date
            """
    cursor.execute(query, (username, from_date, to_date))
    data = cursor.fetchall()
    cursor.close()
    labels = []
    datas = []
    for line in data:
        label = str(line['year']) + '-' + str(line['month'])
        data = int(line['spend'])
        labels.append(label)
        datas.append(data)
    return labels, datas


@customer_bp.route('/', methods=['GET', 'POST'])
def customer_home_page():
    username = session["username"]

    q = """
                    SELECT purchases.ticket_id,
                        ticket.airline_name,
                        ticket.flight_num,
                        flight.departure_airport,
                        flight.departure_time,
                        flight.arrival_airport,
                        flight.arrival_time,
                        flight.price,
                        flight.status,
                        flight.airplane_id
                    FROM flight natural join purchases NATURAL join ticket
                    where customer_email = %s
                    AND departure_time > curdate()
        """

    cursor = conn.cursor()
    cursor.execute(q, username)
    data = cursor.fetchall()
    cursor.close()
    form = TrackSpendingForm()
    if request.method == "POST":
        fromDate = form['fromDate'].data
        toDate = form['toDate'].data
        mySpending = total_spending(username, fromDate, toDate)
        labels, datas = get_spending_spread(username, fromDate, toDate)
    else:
        mySpending = total_spending(username)
        labels, datas = get_spending_spread(username)

    return render_template("home/customer_home.html", username=username, posts=data, form=form, mySpending=mySpending,
                           labels=labels, data=datas)
