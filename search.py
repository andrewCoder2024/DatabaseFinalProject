from flask import session, request, redirect, url_for, flash, render_template, Blueprint

from config import app, conn
from forms import FlightSearchForm, AgentPurchaseForm
from booking_agent import getAgentID

search_bp = Blueprint("search", __name__, static_folder="static", template_folder="templates")


@search_bp.route('/', methods=['GET', 'POST'])
def search_page():
    usertype = session.get('usertype')
    form = FlightSearchForm()
    if request.method == "POST":
        if form.validate_on_submit():
            fromCity = form['fromCity'].data
            fromAirport = form['fromAirport'].data
            fromDate = form['fromDate'].data
            toCity = form['toCity'].data
            toAirport = form['toAirport'].data
            toDate = form['toDate'].data
            if True:
                q = """SELECT distinct f.airline_name,
                                    f.flight_num,
                                    departure_airport,
                                    departure_time,
                                    arrival_airport,
                                    arrival_time,
                                    price,
                                    airplane_id
                                        FROM flight as f, airport
                                        WHERE airport.airport_name=f.departure_airport
                                        AND airport.airport_city = %s
                                        AND airport.airport_name = %s
                                        AND f.departure_time BETWEEN DATE_SUB(%s, INTERVAL 2 DAY) AND DATE_ADD(%s, INTERVAL 2 DAY)
                                        AND (f.airline_name, f.flight_num) in
                                            (SELECT flight.airline_name, flight.flight_num FROM flight, airport
                                                WHERE airport.airport_name=flight.arrival_airport
                                                AND airport.airport_city = %s
                                                AND airport.airport_name = %s)
                                        AND (SELECT DISTINCT seats FROM flight, airplane
                                                WHERE flight.airplane_id = airplane.airplane_id
                                                AND flight.airline_name = airplane.airline_name
                                                AND flight.airline_name = f.airline_name
                                                AND flight.flight_num = f.flight_num) >=
                                                    (SELECT COUNT(*) FROM ticket
                                                        WHERE ticket.airline_name = f.airline_name
                                                        AND ticket.flight_num = f.flight_num)
                        """
                try:
                    cursor = conn.cursor()
                    cursor.execute(q, (fromCity, fromAirport, fromDate, toDate, toCity, toAirport))
                    data = cursor.fetchone()
                    cursor.close()
                    if data:

                        flash("flight found", category="success")
                    '''
                    data_dict = {'airline_name': data['airline_name'], 'flight_num': data['flight_num'],
                                 'departure_airport': data['departure_airport'], 'departure_time': data['departure_time'],
                                 'arrival_airport': data['arrival_airport'], 'arrival_time': data['arrival_time'],
                                 'price': data['price'], 'airplane_id':data['airplane_id']}
                    '''
                    return redirect(url_for('search.search_result', airline_name=data['airline_name'],
                                            flight_num=data['flight_num'],
                                            departure_airport=data['departure_airport'],
                                            departure_time=data['departure_time'],
                                            arrival_airport=data['arrival_airport'], arrival_time=data['arrival_time'],
                                            price=data['price'], airplane_id=data['airplane_id']))
                except Exception as e:
                    print(e)
                    flash(f"No flight found! Please try again", category='danger')
    return render_template('flight_search.html', form=form, usertype=usertype)


@search_bp.route('/result', methods=['GET', 'POST'])
def search_result():
    purchase_form = AgentPurchaseForm()
    airplane_id = request.args['airplane_id']
    airline_name = request.args['airline_name']
    flight_num = request.args['flight_num']
    departure_airport = request.args['departure_airport']
    departure_time = request.args['departure_time']
    arrival_airport = request.args['arrival_airport']
    arrival_time = request.args['arrival_time']
    price = request.args['price']
    username = session.get('username')
    booking_agent_id = None
    if request.method == "POST":
        try:
            if session.get('usertype') == 'agent':
                booking_agent_id = getAgentID(username)
                flash("success 1")
                if purchase_form.validate_on_submit():

                    flash("success 2")
                    agent_q = """SELECT airline_name FROM booking_agent natural join 
                    booking_agent_work_for where airline_name = %s and email = %s """
                    flash("success 3")
                    cursor = conn.cursor()
                    flash("success 3.5")
                    cursor.execute(agent_q, (airline_name, username))
                    data = cursor.fetchall()
                    cursor.close()
                    flash("success 4")
                    if not data:
                        flash(f'Booking agent {username} does not work for airline {airline_name}', category='danger')
                        return redirect(search_page())
                    cursor = conn.cursor()
                    flash("success 5")
                    email = purchase_form['email1'].data
                    print("email", email)
                    flash(email)
                    query = """select email from customer where email = %s"""
                    cursor.execute(query, email)
                    data = cursor.fetchone()
                    cursor.close()
                    if data:
                        username = email
                    else:
                        flash(f'customer with email: {email} has not been found in the system', category='danger')
                        return redirect(url_for('home_page'))
            cursor = conn.cursor()
            query = """
                        SELECT MAX(ticket_id) + 1 as nxt_ticket_id FROM ticket
                            WHERE (SELECT COUNT(*) as count FROM ticket
                                    WHERE ticket.airline_name = %s AND ticket.flight_num = %s
                                ) < (SELECT airplane.seats as seats FROM flight, airplane
                                        WHERE flight.airline_name = %s AND flight.flight_num = %s
                                        AND flight.airplane_id = airplane.airplane_id)
                        """
            cursor.execute(query, (airline_name, flight_num, airline_name, flight_num))
            data = cursor.fetchone()
            nxt_ticket_id = data['nxt_ticket_id']
            queryInsertTicket = """
                                        INSERT INTO ticket VALUES(%s, %s, %s)
                                        """
            cursor.execute(queryInsertTicket, (nxt_ticket_id, airline_name, flight_num))
            queryInsertPurchase = """
                                            INSERT INTO purchases VALUES(%s, %s, %s, CURDATE())
                                            """
            cursor.execute(queryInsertPurchase, (nxt_ticket_id, username, None))
            conn.commit()
            cursor.close()
            flash(f'Success! You have purchased the flight #{flight_num}', category='success')
            return redirect(url_for('home_page'))
        except Exception as e:
            print(e)
            flash(f'exception {e}', category='danger')
    return render_template('search_result.html', purchase_form=purchase_form,
                           airplane_id=request.args['airplane_id'],
                           airline_name=request.args['airline_name'],
                           flight_num=request.args['flight_num'],
                           departure_airport=request.args['departure_airport'],
                           departure_time=request.args['departure_time'],
                           arrival_airport=request.args['arrival_airport'],
                           arrival_time=request.args['arrival_time'],
                           price=request.args['price'])
