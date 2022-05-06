import json
from datetime import date, timedelta

import plotly
from flask import session, request, flash, render_template, Blueprint, jsonify, Markup, redirect, url_for
from config import app, conn, today, last1mon, last1year, last6mons
from forms import AgentFlightsForm, CreateFlightsForm, ChangeFlightsStatus, AddAirplaneForm, AddAirportForm, \
    AgentReportsForm, BookingAgentAdditionForm, AgentPermissionsForm
import plotly.graph_objs as go
import plotly.offline as plt
import pandas as pd

staff_bp = Blueprint("staff", __name__, static_folder="static", template_folder="templates")


def get_perms(username):
    q = """select permission_type from airline_staff natural join permission where username = %s"""

    cursor = conn.cursor()
    cursor.execute(q, username)
    data = cursor.fetchall()
    cursor.close()
    return [line["permission_type"] for line in data]


def perm_fail(): flash('You do not meet the requisite conditions for this action', category='danger')


def grant_perms(username, permission):
    try:
        q = """INSERT INTO `permission` (`username`, `permission_type`) VALUES (%s, %s)"""
        cursor = conn.cursor()
        cursor.execute(q, (username, permission))
        cursor.close()
        flash(f"Permission {permission} has been granted to staff {username}!", category='success')
    except Exception as e:
        flash(f'{e}', category='danger')


def add_agents(email, airline_name):
    q1 = """SELECT * from booking_agent where email = %s"""
    cursor = conn.cursor()
    cursor.execute(q1, email)
    data = cursor.fetchall()
    cursor.close()
    if data:
        try:
            q2 = """INSERT INTO `booking_agent_work_for` (`email`, `airline_name`) VALUES (%s, %s)"""
            cursor = conn.cursor()
            cursor.execute(q2, (email, airline_name))
            cursor.close()
            flash(f"Agent with email: {email} has been employed to the airline!", category='success')
        except Exception as e:
            flash(f'{e}', category='danger')
    else:
        flash(f'No agent found with email {email}', category='danger')


def change_flight_status(airline_name, status, flight_num):
    try:
        q = """UPDATE `flight` SET `status` = %s WHERE 
        `flight`.`airline_name` = %s AND `flight`.`flight_num` = %s"""
        cursor = conn.cursor()
        cursor.execute(q, (status, airline_name, flight_num))
        conn.commit()
        cursor.close()
        flash(f"Flight status has been updated!", category='success')
    except Exception as e:
        flash(f'{e}', category='danger')


def create_airplane(airline, seats):
    try:
        cursor = conn.cursor()
        q_id = """select max(airplane_id)+1 from airplane"""
        cursor.execute(q_id)
        airplane_id = cursor.fetchone()
        query = """
                    INSERT INTO airplane VALUES(%s, %s, %s)  """
        cursor.execute(query, (airline, airplane_id, seats))
        conn.commit()
        cursor.close()
        flash(f"Airplane with id {airplane_id} has been created!", category='success')
    except Exception as e:
        flash(f'{e}', category='danger')


def getStaffAirline(username):
    cursor = conn.cursor()
    query = 'SELECT airline_name FROM airline_staff WHERE username = %s'
    cursor.execute(query, username)
    data = cursor.fetchone()
    cursor.close()
    return data['airline_name']


def add_flight(airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price,
               status, airplane_id):
    try:
        q = """INSERT INTO `flight` (`airline_name`, `flight_num`, 
        `departure_airport`, `departure_time`, `arrival_airport`, 
        `arrival_time`, `price`, `status`, `airplane_id`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor = conn.cursor()
        cursor.execute(q, (
            airline_name, flight_num, departure_airport, departure_time, arrival_airport, arrival_time, price, status,
            airplane_id))
        cursor.close()
        flash(f"Flight with number {flight_num} has been created!", category='success')
    except Exception as e:
        flash(f'{e}', category='danger')


def getReport(airline, fromDate=last6mons(), toDate=today()):
    cursor = conn.cursor()
    query = """SELECT YEAR(purchase_date) as year, MONTH(purchase_date) as month, COUNT(ticket_id) as sales
                FROM purchases NATURAL JOIN ticket JOIN flight USING(airline_name, flight_num)
                    WHERE  airline_name = %s
                    AND purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
                GROUP BY year, month
            """
    cursor.execute(query, (airline, fromDate, toDate))
    data = cursor.fetchall()
    cursor.close()
    labels = []
    dataset = []

    for line in data:
        label = str(line['year']) + '-' + str(line['month'])
        data = int(line['sales'])
        labels.append(label)
        dataset.append(data)

    return labels, dataset


def getTopDestinations(airline):
    cursor = conn.cursor()
    query = """
SELECT airport_city, COUNT(ticket_id) as count FROM airport, ticket natural join flight 
WHERE airport_name = arrival_airport 
AND airline_name= %s and departure_time between CURRENT_DATE - INTERVAL 90 DAY AND 
CURRENT_DATE GROUP by airport_city ORDER by count DESC LIMIT 3
            """
    cursor.execute(query, airline)
    top_3_mths = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()
    query = """
    SELECT airport_city, COUNT(ticket_id) as count FROM airport, ticket natural join flight 
    WHERE airport_name = arrival_airport 
    AND airline_name= %s and departure_time between CURRENT_DATE - INTERVAL 365 DAY AND 
    CURRENT_DATE GROUP by airport_city ORDER by count DESC LIMIT 3
                """
    cursor.execute(query, airline)
    top_year = cursor.fetchall()
    cursor.close()
    return top_3_mths, top_year


def default_customer_view(username):
    q = """SELECT distinct ticket.flight_num,
                                flight.airplane_id, 
                                purchases.ticket_id,
                                ticket.airline_name,
                                flight.departure_airport,
                                flight.departure_time,
                                flight.arrival_airport,
                                flight.arrival_time,
                                flight.price,
                                flight.status
                                
                            FROM flight natural join purchases NATURAL join ticket natural join airline_staff
                            where airline_staff.username = %s
                            AND departure_time between date_sub(CURRENT_DATE, INTERVAL 2 DAY) 
                        and date_sub(CURRENT_DATE + INTERVAL 30 day, INTERVAL 2 DAY) 
                        group by flight_num;"""
    cursor = conn.cursor()
    cursor.execute(q, username)
    data = cursor.fetchall()
    cursor.close()
    customer_flights = {}
    q = """select distinct customer_email from ticket natural join purchases natural join customer where flight_num = 
                %s """
    for line in data:
        flight_num = line['flight_num']
        customer_flights[flight_num] = []
        cursor = conn.cursor()
        cursor.execute(q, flight_num)
        customers = cursor.fetchall()
        cursor.close()
        for customer in customers:
            customer_flights[flight_num].append(customer["customer_email"])
    return data, customer_flights


def view_booking_agents():
    cursor = conn.cursor()
    q1 = """SELECT booking_agent_id, COUNT(distinct ticket_id) as sales 
    FROM purchases natural join ticket natural join flight 
    where purchase_date between CURRENT_DATE - INTERVAL 30 DAY AND 
    CURRENT_DATE and booking_agent_id is not null group by booking_agent_id order by sales DESC limit 5"""
    q2 = """
SELECT booking_agent_id, sum(price) as commission  FROM 
purchases natural join ticket natural join flight where  purchase_date 
between CURRENT_DATE - INTERVAL 365 DAY AND 
CURRENT_DATE and booking_agent_id is not null group by 
booking_agent_id order by commission DESC limit 5"""
    cursor.execute(q1)
    top_by_sales = cursor.fetchall()
    cursor.close()
    cursor = conn.cursor()
    cursor.execute(q2)
    top_by_commission = cursor.fetchall()
    cursor.close()
    return top_by_sales, top_by_commission


def getRevenue(airline):
    query = """SELECT *  FROM
                (SELECT SUM(price) as direct FROM purchases NATURAL JOIN ticket natural join flight 
                    WHERE  airline_name = %s
                    AND purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
                    AND booking_agent_id IS NULL) as one,
                (SELECT SUM(price) as indirect FROM purchases NATURAL JOIN ticket natural join flight 
                    WHERE  airline_name = %s
                    AND purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
                    AND booking_agent_id IS NOT NULL) as two
    """
    cursor = conn.cursor()
    cursor.execute(query, (airline, last1mon(), today(), airline, last1mon(), today()))
    last1MthData = cursor.fetchone()
    last1MthData['direct'] = int(last1MthData['direct'])
    last1MthData['indirect'] = int(last1MthData['indirect'])
    cursor.execute(query, (airline, last1year(), today(), airline, last1year(), today()))
    last1YearData = cursor.fetchone()
    last1YearData['direct'] = int(last1YearData['direct'])
    last1YearData['indirect'] = int(last1YearData['indirect'])
    cursor.close()
    return last1MthData, last1YearData


def create_airport(name, city):
    try:
        cursor = conn.cursor()
        query = """
                INSERT INTO airport VALUES (%s, %s) """
        cursor.execute(query, (name, city))
        conn.commit()
        cursor.close()
        flash(f"Airport with name {name} has been created!", category='success')
    except Exception as e:
        flash(f'{e}', category='danger')


def most_frequent_customer(username, airline_name):
    q = """select customer_email, count(distinct ticket_id) from customer 
    natural join purchases natural join ticket natural join 
    airline as a where %s in (select username from airline_staff 
    where airline_staff.airline_name = a.airline_name ) group by 
    customer_email having count(distinct ticket_id) 
    >= all(select count(distinct ticket_id) from customer natural join 
    purchases natural join ticket natural join airline as a where %s in 
    (select username from airline_staff where airline_staff.airline_name = a.airline_name ) group by customer_email)"""
    cursor = conn.cursor()
    cursor.execute(q, (username, username))
    top_customer = cursor.fetchone()
    cursor.close()
    q2 = """select distinct flight_num from ticket natural join purchases where 
    airline_name = %s and purchases.customer_email = %s"""
    cursor = conn.cursor()
    cursor.execute(q2, (airline_name, top_customer['customer_email']))
    top_customer_flights = cursor.fetchall()
    cursor.close()
    return top_customer, top_customer_flights


@staff_bp.route('/', methods=['GET', 'POST'])
def staff_home_page():
    if session.get('usertype') != 'staff':
        flash("You do not have access to this webpage!", category='danger')
        return redirect(url_for('home_page'))
    reports_plot = None
    labels = None
    dataset = None
    username = session["username"]
    flights_form = AgentFlightsForm()
    new_flights_form = CreateFlightsForm()
    status_flights_form = ChangeFlightsStatus()
    add_airplane_form = AddAirplaneForm()
    add_airport_form = AddAirportForm()
    reports_form = AgentReportsForm()
    add_agent_form = BookingAgentAdditionForm()
    permissions_form = AgentPermissionsForm()
    permissions = get_perms(username)
    flash(permissions, category='success')
    airline_name = getStaffAirline(username)
    data, customer_flights = default_customer_view(username)
    frequent_customer, frequent_customer_flights = most_frequent_customer(username, airline_name)
    rev_1mth, rev_1yrs = getRevenue(airline_name)
    top_by_sales, top_by_commission = view_booking_agents()
    top_3mth, top_yr = getTopDestinations(airline_name)
    if request.method == "POST":
        if flights_form.validate_on_submit():
            flash("post")
            try:
                q = """SELECT distinct ticket.flight_num,
                                ticket.airline_name,
                                
                                flight.departure_airport,
                                flight.departure_time,
                                flight.arrival_airport,
                                flight.arrival_time,
                                flight.price,
                                flight.status,
                                flight.airplane_id
                            FROM flight natural join purchases NATURAL join ticket natural join airline
                            where airline_name = %s  and departure_time between date_sub(%s, INTERVAL 2 DAY) 
                        and date_sub(%s, INTERVAL 2 DAY) 
                        group by flight_num;"""
                fromDate = flights_form['fromDate1'].data
                toDate = flights_form['toDate1'].data
                cursor = conn.cursor()
                cursor.execute(q, (airline_name, fromDate, toDate))
                data = cursor.fetchall()
                cursor.close()
                customer_flights = {}
                q = """select distinct customer_email from ticket natural join purchases natural join customer where flight_num = 
                %s """
                for line in data:
                    flight_num = line['flight_num']
                    customer_flights[flight_num] = []
                    cursor = conn.cursor()
                    cursor.execute(q, flight_num)
                    customers = cursor.fetchall()
                    cursor.close()
                    for customer in customers:
                        customer_flights[flight_num].append(customer["customer_email"])
                return render_template("home/staff_home.html", username=username, posts=data,
                                       customer_flights=customer_flights,
                                       frequent_customer=frequent_customer,
                                       rev_1mth=rev_1mth,
                                       rev_1yrs=rev_1yrs, top_by_sales=top_by_sales,
                                       top_by_commission=top_by_commission, top_3mth=top_3mth, top_yr=top_yr,
                                       flights_form=flights_form, new_flights_form=new_flights_form,
                                       status_flights_form=status_flights_form, add_airplane_form=add_airplane_form,
                                       add_airport_form=add_airport_form, reports_plot=reports_plot,
                                       add_agent_form=add_agent_form,
                                       permissions_form=permissions_form, labels=labels, dataset=dataset
                                       )
            except Exception as e:
                flash(f'{e}', category='danger')
        else:
            if new_flights_form.validate_on_submit():
                if "Admin" in permissions:
                    arrivalDate = new_flights_form['fromDate2'].data
                    departureDate = new_flights_form['toDate2'].data
                    departure_airport_name = new_flights_form['departure_airport_name'].data
                    arrival_airport_name = new_flights_form['arrival_airport_name'].data
                    status = new_flights_form['status1'].data
                    price = new_flights_form['price'].data
                    flight_num = new_flights_form['flight_num1'].data
                    airplaneID = new_flights_form['airplaneID'].data
                    add_flight(airline_name, flight_num, departure_airport_name,
                               departureDate, arrival_airport_name,
                               arrivalDate, price, status, airplaneID)
                    flash("success")
                else:
                    perm_fail()
            elif status_flights_form.validate_on_submit():
                if "Operator" in permissions:
                    status = status_flights_form['status2'].data
                    flight_num = status_flights_form['flight_num2'].data
                    change_flight_status(airline_name, status, flight_num)
                else:
                    perm_fail()
            elif add_airplane_form.validate_on_submit():
                if "Admin" in permissions:
                    seats = add_airplane_form['seats'].data
                    create_airplane(airline_name, seats)
                else:
                    perm_fail()
            elif add_airport_form.validate_on_submit():
                if "Admin" in permissions:
                    airport_name = add_airport_form['airport_name'].data
                    city = add_airport_form['city'].data
                    create_airport(airport_name, city)
                else:
                    perm_fail()
            elif reports_form.validate_on_submit():
                fromDate = reports_form['fromDate3'].data
                toDate = reports_form['toDate3'].data
                labels, dataset = getReport(airline_name, fromDate, toDate)
                labels, dataset = json.dumps(labels), json.dumps(dataset)
                return render_template("home/staff_home.html", username=username, posts=data,
                                       customer_flights=customer_flights,
                                       frequent_customer=frequent_customer, rev_1mth=rev_1mth,
                                       rev_1yrs=rev_1yrs, top_by_sales=top_by_sales,
                                       top_by_commission=top_by_commission, top_3mth=top_3mth, top_yr=top_yr,
                                       flights_form=flights_form, new_flights_form=new_flights_form,
                                       status_flights_form=status_flights_form, add_airplane_form=add_airplane_form,
                                       add_airport_form=add_airport_form, reports_form=reports_form,
                                       add_agent_form=add_agent_form,
                                       permissions_form=permissions_form, reports_plot=reports_plot,
                                       frequent_customer_flights=frequent_customer_flights,
                                       labels=labels, dataset=dataset
                                       )
            elif add_agent_form.validate_on_submit():
                if "Admin" in permissions:
                    email = add_agent_form['email2'].data
                    add_agents(email, airline_name)
                else:
                    perm_fail()
            elif permissions_form.validate_on_submit():
                if "Admin" in permissions:
                    username = permissions_form['username'].data
                    permission = permissions_form['usertype'].data
                    grant_perms(username, permission)
                else:
                    perm_fail()
    else:
        data, customer_flights = default_customer_view(username)
        frequent_customer, frequent_customer_flights = most_frequent_customer(username, airline_name)
        rev_1mth, rev_1yrs = getRevenue(airline_name)
        top_by_sales, top_by_commission = view_booking_agents()
        top_3mth, top_yr = getTopDestinations(airline_name)
    return render_template("home/staff_home.html", username=username, posts=data, customer_flights=customer_flights,
                           frequent_customer=frequent_customer, rev_1mth=rev_1mth,
                           rev_1yrs=rev_1yrs, top_by_sales=top_by_sales,
                           top_by_commission=top_by_commission, top_3mth=top_3mth, top_yr=top_yr,
                           flights_form=flights_form, new_flights_form=new_flights_form,
                           status_flights_form=status_flights_form, add_airplane_form=add_airplane_form,
                           add_airport_form=add_airport_form, reports_form=reports_form, add_agent_form=add_agent_form,
                           permissions_form=permissions_form, reports_plot=reports_plot,
                           frequent_customer_flights=frequent_customer_flights
                           )
