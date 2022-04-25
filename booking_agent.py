from flask import Flask, render_template, request, session, url_for, redirect, Blueprint, flash
import pymysql.cursors
import datetime
from config import app, conn, today, last1mon, last1year, last6mons, yearFromNow
from forms import *
from datetime import date, timedelta
import json

booking_agent_bp = Blueprint("booking_agent", __name__, static_folder="static", template_folder="templates")


def getAgentID(username):
    cursor = conn.cursor()
    query = 'SELECT booking_agent_id FROM booking_agent WHERE email=%s'
    cursor.execute(query, username)
    data = cursor.fetchone()
    cursor.close()
    return data['booking_agent_id']


def flightView(username, fromDate=today(), toDate=yearFromNow):
    q = """SELECT distinct purchases.ticket_id,
                                    ticket.airline_name,
                                    ticket.flight_num,
                                    flight.departure_airport,
                                    flight.departure_time,
                                    flight.arrival_airport,
                                    flight.arrival_time,
                                    flight.price,
                                    flight.status,
                                    flight.airplane_id
                                FROM flight natural join purchases NATURAL join ticket natural join booking_agent
                                Where booking_agent_id = %s and departure_time between date_sub(%s, INTERVAL 2 DAY) 
                            and date_sub(%s, INTERVAL 2 DAY)  """
    booking_agent_id = getAgentID(username)
    cursor = conn.cursor()
    cursor.execute(q, (booking_agent_id, fromDate, toDate))
    data = cursor.fetchall()
    cursor.close()
    return data


def get_agent_data(username, fromDate=last1mon(), toDate=today()):
    cursor = conn.cursor()
    q1 = """SELECT sum(price) as sum_sales
                FROM booking_agent NATURAL JOIN 
                purchases NATURAL JOIN ticket
                natural join flight 
                WHERE purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s,INTERVAL 2 DAY)
                    GROUP by email
                    having email = %s
            """
    q2 = """SELECT avg(price) as avg_sales
                FROM booking_agent NATURAL JOIN 
                purchases NATURAL JOIN ticket
                natural join flight 
                WHERE purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s,INTERVAL 2 DAY)
                    GROUP by email
                    having email = %s"""
    q3 = """SELECT COUNT(price) as sales
                FROM booking_agent NATURAL JOIN 
                purchases NATURAL JOIN ticket
                natural join flight 
                WHERE purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s,INTERVAL 2 DAY)
                    GROUP by email
                    having email = %s
            """
    cursor.execute(q1, (fromDate, toDate, username))
    sum_sales = cursor.fetchone()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute(q2, (fromDate, toDate, username))
    avg_sales = cursor.fetchone()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute(q3, (fromDate, toDate, username))
    num_sales = cursor.fetchone()
    cursor.close()
    try:
        return sum_sales['sum_sales'], \
               avg_sales['avg_sales'], \
               num_sales['sales']
    except Exception as e:
        flash(f'{e}')
        return 0, 0, 0


# tickets 6 commission year
def top_customers(username):
    q1 = """SELECT customer_email, COUNT(ticket_id) as top_sale
                            FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket
                            natural join flight
                            WHERE booking_agent.email = %s
                            AND purchase_date >= date_sub(curdate(), INTERVAL 6 MONTH)
                                GROUP BY customer_email ORDER BY top_sale DESC LIMIT 5
                    """
    q2 = """  SELECT customer_email, SUM(price) as top_commission
                            FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket
                            natural join flight
                            WHERE booking_agent.email = %s
                            AND purchase_date >= date_sub(curdate(), INTERVAL 1 YEAR)
                                GROUP by customer_email ORDER by top_commission DESC LIMIT 5
                    """

    cursor = conn.cursor()
    cursor.execute(q1, username)
    data1 = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute(q2, username)
    data2 = cursor.fetchall()
    cursor.close()

    labels1 = []
    dataset1 = []
    labels2 = []
    dataset2 = []

    for line in data1:
        labels1.append(line['customer_email'])
        dataset1.append(int(line['top_sale']))
    for line in data2:
        labels2.append(line['customer_email'])
        dataset2.append(int(line['top_commission']))
    return labels1, dataset1, labels2, dataset2


@booking_agent_bp.route('/', methods=['GET', 'POST'])
def agent_home_page():
    username = session['username']
    form = AgentSalesForm()
    flights_form = AgentFlightsForm()
    sum_sales, avg_sales, num_sales = get_agent_data(username)
    labels1, dataset1, labels2, dataset2 = top_customers(username)
    labels1, dataset1, labels2, dataset2 = json.dumps(labels1), json.dumps(dataset1), \
                                           json.dumps(labels2), json.dumps(dataset2)
    data = flightView(username)
    if request.method == 'POST':
        if form.validate_on_submit():
            flash("success")

            sum_sales, avg_sales, num_sales = get_agent_data(username, request.form['fromDate'], request.form['toDate'])
            flash(f'{sum_sales} {avg_sales} {num_sales}')
            flash(request.form['toDate'])
            return render_template("home/agent_home.html", username=username, form=form,
                                   sum_sales=sum_sales, avg_sales=avg_sales, num_sales=num_sales,
                                   labels1=labels1, dataset1=dataset1, labels2=labels2, dataset2=dataset2, posts=data,
                                   flights_form=flights_form)
        elif flights_form.validate_on_submit():
            fromDate = flights_form['fromDate1'].data
            toDate = flights_form['toDate1'].data

            data = flightView(username, fromDate, toDate)
            return render_template("home/agent_home.html", username=username, form=form,
                                   sum_sales=sum_sales, avg_sales=avg_sales, num_sales=num_sales,
                                   labels1=labels1, dataset1=dataset1, labels2=labels2, dataset2=dataset2, posts=data,
                                   flights_form=flights_form)

    return render_template("home/agent_home.html", username=username, form=form,
                           sum_sales=sum_sales, avg_sales=avg_sales, num_sales=num_sales,
                           labels1=labels1, dataset1=dataset1, labels2=labels2, dataset2=dataset2, posts=data,
                           flights_form=flights_form)
