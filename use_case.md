
##Public Use Cases
  ###1. Public search
  Get List of flights:
  ```sql
    SELECT distinct f.airline_name,
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
```
 All users, whether logged in or not, can Search for upcoming flights based on source city/airport name, destination city/airport name, date.
  ###2. Registration:
  register customer:
  ```sql
    INSERT INTO customer (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`)
                                VALUES (%s, %s, md5(%s), %s, %s, %s, %s, %s, %s, %s, %s, %s) 
```
  register staff:
  ```sql
    INSERT INTO airline_staff (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`)
                            VALUES (%s, md5(%s), %s, %s, %s, %s)
```
register agent:
  ```sql
    INSERT INTO booking_agent (`email`, `password`, `booking_agent_id`) VALUES (%s, md5(%s), %s)
```
  ###3. Login:
  
  Login based upon customer type: fetch result. If no result, then user not found
  ```python
        if usertype == 'customer':
            q = 'SELECT * FROM customer WHERE email = %s and password = md5(%s)'
        elif usertype == 'agent':
            q = 'SELECT * FROM booking_agent WHERE email = %s and password = md5(%s)'
        else:
            q = 'SELECT * FROM airline_staff WHERE username = %s and password = md5(%s)'
```
    
##Customer Use Cases
  ###1. View My Flights
  ```mysql
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
```
gets upcoming flights for customer_email as provided by the login info
  ###2.  Purchase Tickets
  ```python
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

```
Get the value of ticket_id to insert into ticket table, and then insert those values along with the airline name and flight number of the purchased flight into purchases table
###3. Search For Flights
```sql
SELECT distinct f.airline_name,
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
```
Flights who have seats > # tickets sold will be shown to user, who can then purchase them

###4. Track My Spending

```sql
select SUM(price) as spend, YEAR(purchase_date) as year, 
                MONTH(purchase_date) as month from customer 
                natural join purchases 
                natural join ticket natural join flight 
                where email = %s
                and purchase_date between date_sub(%s, INTERVAL 2 DAY) 
                and date_sub(%s, INTERVAL 2 DAY)
                GROUP BY year, month
                ORDER BY purchases.purchase_date
```
Money spent per month will be gathered
```sql
select SUM(flight.price) as spend from customer 
               natural join purchases
               natural join ticket natural join flight 
               where email = %s
               and purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
```
As well as total money spent within the same time frame 

###5. Logout 
```python
    if session:
        session.clear()
        flash("You have been logged out!", category='info')
        return redirect(url_for("home_page"))
    else:
        session.clear()
        flash("You have not logged in yet!", category='info')
        return redirect(url_for("home_page"))
```
Pop data from session

##Booking Agent Use Cases 
###1. View My Flights
```mysql
SELECT distinct purchases.ticket_id,
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
                            and date_sub(%s, INTERVAL 2 DAY)  
```
View Flights between user entered dates with matching agent id number for the purchases

###2. Purchase Tickets
```python
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

```

Same query as for customer purchase of tickets, however the username variable in the query is equivalent to an entered customer's email address

###3. Search For Flights
```sql
SELECT distinct f.airline_name,
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
```
Same as for customer
###4. View My Commission
Get sum of sales:
```sql 
SELECT sum(price) as sum_sales
                FROM booking_agent NATURAL JOIN 
                purchases NATURAL JOIN ticket
                natural join flight 
                WHERE purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s,INTERVAL 2 DAY)
                    GROUP by email
                    having email = %s
```
Get Average of Sales:
```sql
SELECT avg(price) as avg_sales
                FROM booking_agent NATURAL JOIN 
                purchases NATURAL JOIN ticket
                natural join flight 
                WHERE purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s,INTERVAL 2 DAY)
                    GROUP by email
                    having email = %s
```
Get Number of Sales:
```sql
SELECT COUNT(price) as sales
                FROM booking_agent NATURAL JOIN 
                purchases NATURAL JOIN ticket
                natural join flight 
                WHERE purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s,INTERVAL 2 DAY)
                    GROUP by email
                    having email = %s
```
###5. View Top Customers:
Top by number of sales
```sql
SELECT customer_email, COUNT(ticket_id) as top_sale
                            FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket
                            natural join flight
                            WHERE booking_agent.email = %s
                            AND purchase_date >= date_sub(curdate(), INTERVAL 6 MONTH)
                                GROUP BY customer_email ORDER BY top_sale DESC LIMIT 5

```
Top by commission
```sql

SELECT customer_email, SUM(price) as top_commission
                            FROM booking_agent NATURAL JOIN purchases NATURAL JOIN ticket
                            natural join flight
                            WHERE booking_agent.email = %s
                            AND purchase_date >= date_sub(curdate(), INTERVAL 1 YEAR)
                                GROUP by customer_email ORDER by top_commission DESC LIMIT 5
```
###6. Logout
```python
    if session:
        session.clear()
        flash("You have been logged out!", category='info')
        return redirect(url_for("home_page"))
    else:
        session.clear()
        flash("You have not logged in yet!", category='info')
        return redirect(url_for("home_page"))
```
Same as for customer
 
##Airline Staff Use Cases
###1. View My Flights
```sql
SELECT distinct ticket.flight_num,
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
                        group by flight_num;
```
View flights based upon given departure and arrival dates for a given airline

###2. Create New Flights
```sql
INSERT INTO `flight` (`airline_name`, `flight_num`, 
        `departure_airport`, `departure_time`, `arrival_airport`, 
        `arrival_time`, `price`, `status`, `airplane_id`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
```
Insert into flights based on values collected through a form
Admin permission required
###3. Change Status of Flights
```sql
UPDATE `flight` SET `status` = %s WHERE 
        `flight`.`airline_name` = %s AND `flight`.`flight_num` = %s
```
Update status of a flight based on choice of three options given by a form. Operator permission required

###4. Add airplane in the system
```python
        q_id = """select max(airplane_id)+1 from airplane"""
        cursor.execute(q_id)
        airplane_id = cursor.fetchone()
        query = """
                    INSERT INTO airplane VALUES(%s, %s, %s)  """
        cursor.execute(query, (airline, airplane_id, seats))
```
He or she adds a new airplane, providing all the needed data, via forms after obtaining the next airpline id to insert into the system
Admin permission required
###5. Add new airport in the system
```python
        query = """
                INSERT INTO airport VALUES (%s, %s) """
        cursor.execute(query, (name, city))
```
Admin permission required
###6. View all the booking agents
```python
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
```
View top by booking agents by sales and by commission

###7. View frequent customers
```sql
select customer_email, count(distinct ticket_id) from customer 
    natural join purchases natural join ticket natural join 
    airline as a where %s in (select username from airline_staff 
    where airline_staff.airline_name = a.airline_name ) group by 
    customer_email having count(distinct ticket_id) 
    >= all(select count(distinct ticket_id) from customer natural join 
    purchases natural join ticket natural join airline as a where %s in 
    (select username from airline_staff where airline_staff.airline_name = a.airline_name ) group by customer_email)
```

View customer with the most purchases on a given airline 

```sql
select distinct flight_num from ticket natural join purchases where 
    airline_name = %s and purchases.customer_email = %s
```
See the flights purchased by the MVP customer 

###8. View Reports

```sql
SELECT YEAR(purchase_date) as year, MONTH(purchase_date) as month, COUNT(ticket_id) as sales
                FROM purchases NATURAL JOIN ticket JOIN flight USING(airline_name, flight_num)
                    WHERE  airline_name = %s
                    AND purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
                GROUP BY year, month
```

Reports for ticket sales by month

###9. Comparison of Revenue earned
```sql
SELECT *  FROM
                (SELECT SUM(price) as direct FROM purchases NATURAL JOIN ticket natural join flight 
                    WHERE  airline_name = %s
                    AND purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
                    AND booking_agent_id IS NULL) as one,
                (SELECT SUM(price) as indirect FROM purchases NATURAL JOIN ticket natural join flight 
                    WHERE  airline_name = %s
                    AND purchase_date BETWEEN date_sub(%s, INTERVAL 2 DAY) AND date_sub(%s, INTERVAL 2 DAY)
                    AND booking_agent_id IS NOT NULL) as two
```
Get comparison of agented and unagented ticket sales for the airline 

###10. View Top destinations
```python
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
```
Get the most frequented destination cities for a given airline in the past 3 months and year

###11. Grant new permissions
```sql
INSERT INTO `permission` (`username`, `permission_type`) VALUES (%s, %s)
```
Give airline staff with username obtained through forms a permission 

###12. Add booking agents
```python
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
```

See if a given booking_agent email is within the system. If they are, then add to the airline.

###13. Logout
```python
    if session:
        session.clear()
        flash("You have been logged out!", category='info')
        return redirect(url_for("home_page"))
    else:
        session.clear()
        flash("You have not logged in yet!", category='info')
        return redirect(url_for("home_page"))
```
Same as for customer