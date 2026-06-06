from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='public', static_url_path='')
PORT = 3000

USE_MYSQL = os.environ.get('USE_MYSQL', '0') == '1'
MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DB = os.environ.get('MYSQL_DB', 'bus_reservation')

DB_PATH = os.path.join(os.path.dirname(__file__), 'bus_reservation.db')

if USE_MYSQL:
    import mysql.connector
MYSQL_CONN = None

def init_db():
    global USE_MYSQL, MYSQL_CONN
    if USE_MYSQL:
        try:
            MYSQL_CONN = mysql.connector.connect(
                host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB
            )
            cur = MYSQL_CONN.cursor()
            cur.execute('CREATE DATABASE IF NOT EXISTS bus_reservation; USE bus_reservation;')
            tables = [
                '''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS routes (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    from_city TEXT NOT NULL,
                    to_city TEXT NOT NULL,
                    date TEXT NOT NULL,
                    departure_time TEXT NOT NULL,
                    arrival_time TEXT NOT NULL,
                    bus_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    seats_available INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    user_id INTEGER NOT NULL,
                    route_id INTEGER NOT NULL,
                    seats INTEGER NOT NULL,
                    total_price REAL NOT NULL,
                    passenger_name TEXT NOT NULL,
                    passenger_phone TEXT NOT NULL,
                    payment_method TEXT DEFAULT 'cash',
                    status TEXT DEFAULT 'confirmed',
                    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (route_id) REFERENCES routes(id)
                )''',
                '''CREATE TABLE IF NOT EXISTS buses (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    bus_name TEXT NOT NULL,
                    bus_type TEXT NOT NULL,
                    total_seats INTEGER NOT NULL,
                    amenities TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTO_INCREMENT,
                    user_id INTEGER NOT NULL,
                    bus_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (bus_id) REFERENCES buses(id)
                )''',
            ]
            for ddl in tables:
                cur.execute(ddl)
                MYSQL_CONN.commit()
            cur.execute('SELECT * FROM users WHERE email = %s', ('admin@bus.com',))
            if not cur.fetchone():
                cur.execute('INSERT INTO users (name, email, phone, password, role) VALUES (%s, %s, %s, %s, %s)',
                            ('Admin', 'admin@bus.com', '9876543210', 'admin123', 'admin'))
                MYSQL_CONN.commit()
            cur.execute('SELECT COUNT(*) as count FROM buses')
            if cur.fetchone()['count'] == 0:
                buses = [
                    ('Volvo AC', 'AC Seater', 20, 'WiFi, AC, Water Bottle'),
                    ('Sleeper', 'Non-AC Sleeper', 15, 'Pillow, Blanket'),
                    ('Volvo Sleeper', 'AC Sleeper', 30, 'WiFi, AC, Pillow, Blanket'),
                    ('AC Seater', 'AC Seater', 25, 'AC, Charging Point'),
                ]
                cur.executemany('INSERT INTO buses (bus_name, bus_type, total_seats, amenities) VALUES (%s, %s, %s, %s)', buses)
                MYSQL_CONN.commit()
            cur.execute('SELECT COUNT(*) as count FROM routes')
            if cur.fetchone()['count'] == 0:
                base_date = datetime.now().date()
                routes = [
                    ('Mumbai', 'Pune', (base_date + timedelta(days=1)).isoformat(), '08:00', '11:30', 'Volvo AC', 500, 20),
                    ('Mumbai', 'Pune', (base_date + timedelta(days=1)).isoformat(), '14:00', '17:30', 'Sleeper', 450, 15),
                    ('Mumbai', 'Goa', (base_date + timedelta(days=2)).isoformat(), '20:00', '08:00', 'Volvo Sleeper', 1200, 30),
                    ('Delhi', 'Jaipur', (base_date + timedelta(days=3)).isoformat(), '06:00', '10:00', 'AC Seater', 400, 25),
                    ('Delhi', 'Jaipur', (base_date + timedelta(days=3)).isoformat(), '15:00', '19:00', 'Sleeper', 350, 20),
                ]
                cur.executemany('INSERT INTO routes (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', routes)
                MYSQL_CONN.commit()
            cur.execute('SELECT COUNT(*) as count FROM feedback')
            if cur.fetchone()['count'] == 0:
                feedbacks = [
                    (1, 1, 5, 'Great service and comfortable trip.'),
                    (1, 2, 4, 'Good experience with clean seats.'),
                ]
                cur.executemany('INSERT INTO feedback (user_id, bus_id, rating, comment) VALUES (%s,%s,%s,%s)', feedbacks)
                MYSQL_CONN.commit()
        except Exception as e:
            print('MySQL init failed, falling back to SQLite:', e)
            USE_MYSQL = False

    if not USE_MYSQL:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_city TEXT NOT NULL,
                to_city TEXT NOT NULL,
                date TEXT NOT NULL,
                departure_time TEXT NOT NULL,
                arrival_time TEXT NOT NULL,
                bus_name TEXT NOT NULL,
                price REAL NOT NULL,
                seats_available INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                route_id INTEGER NOT NULL,
                seats INTEGER NOT NULL,
                total_price REAL NOT NULL,
                passenger_name TEXT NOT NULL,
                passenger_phone TEXT NOT NULL,
                payment_method TEXT DEFAULT 'cash',
                status TEXT DEFAULT 'confirmed',
                booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (route_id) REFERENCES routes(id)
            );
            CREATE TABLE IF NOT EXISTS buses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bus_name TEXT NOT NULL,
                bus_type TEXT NOT NULL,
                total_seats INTEGER NOT NULL,
                amenities TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bus_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (bus_id) REFERENCES buses(id)
            );
        ''')
        cur.execute('SELECT * FROM users WHERE email = ?', ('admin@bus.com',))
        if not cur.fetchone():
            cur.execute('INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)',
                        ('Admin', 'admin@bus.com', '9876543210', 'admin123', 'admin'))
        cur.execute('SELECT COUNT(*) as count FROM buses')
        if cur.fetchone()['count'] == 0:
            buses = [
                ('Volvo AC', 'AC Seater', 20, 'WiFi, AC, Water Bottle'),
                ('Sleeper', 'Non-AC Sleeper', 15, 'Pillow, Blanket'),
                ('Volvo Sleeper', 'AC Sleeper', 30, 'WiFi, AC, Pillow, Blanket'),
                ('AC Seater', 'AC Seater', 25, 'AC, Charging Point'),
            ]
            cur.executemany('INSERT INTO buses (bus_name, bus_type, total_seats, amenities) VALUES (?, ?, ?, ?)', buses)
        cur.execute('SELECT COUNT(*) as count FROM routes')
        if cur.fetchone()['count'] == 0:
            base_date = datetime.now().date()
            routes = [
                ('Mumbai', 'Pune', (base_date + timedelta(days=1)).isoformat(), '08:00', '11:30', 'Volvo AC', 500, 20),
                ('Mumbai', 'Pune', (base_date + timedelta(days=1)).isoformat(), '14:00', '17:30', 'Sleeper', 450, 15),
                ('Mumbai', 'Goa', (base_date + timedelta(days=2)).isoformat(), '20:00', '08:00', 'Volvo Sleeper', 1200, 30),
                ('Delhi', 'Jaipur', (base_date + timedelta(days=3)).isoformat(), '06:00', '10:00', 'AC Seater', 400, 25),
                ('Delhi', 'Jaipur', (base_date + timedelta(days=3)).isoformat(), '15:00', '19:00', 'Sleeper', 350, 20),
            ]
            cur.executemany('INSERT INTO routes (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', routes)
        cur.execute('SELECT COUNT(*) as count FROM feedback')
        if cur.fetchone()['count'] == 0:
            feedbacks = [
                (1, 1, 5, 'Great service and comfortable trip.'),
                (1, 2, 4, 'Good experience with clean seats.'),
            ]
            cur.executemany('INSERT INTO feedback (user_id, bus_id, rating, comment) VALUES (?, ?, ?, ?)', feedbacks)
        conn.commit()
        conn.close()

def get_cursor():
    if USE_MYSQL:
        return MYSQL_CONN.cursor(dictionary=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # attach connection to cursor so callers can access `cur.connection` like MySQL branch expects
    try:
        cur.connection = conn
    except Exception:
        # in unlikely case attribute can't be set, wrap cursor in a simple object
        class _CurWrapper:
            def __init__(self, cursor, conn):
                self._cur = cursor
                self.connection = conn
            def execute(self, *a, **k):
                return self._cur.execute(*a, **k)
            def fetchone(self):
                return self._cur.fetchone()
            def fetchall(self):
                return self._cur.fetchall()
            def __getattr__(self, name):
                return getattr(self._cur, name)
        cur = _CurWrapper(cur, conn)
    return cur

def dict_rows(cursor):
    if USE_MYSQL:
        return cursor.fetchall()
    return [dict(row) for row in cursor.fetchall()]

def dict_row(cursor):
    if USE_MYSQL:
        row = cursor.fetchone()
        return dict(row) if row else None
    row = cursor.fetchone()
    return dict(row) if row else None

@app.route('/')
def index():
    return send_from_directory('views', 'index.html')

@app.route('/register')
def register():
    return send_from_directory('views', 'register.html')

@app.route('/login')
def login():
    return send_from_directory('views', 'login.html')

@app.route('/search')
def search_route():
    return send_from_directory('views', 'search.html')

@app.route('/dashboard')
def dashboard():
    return send_from_directory('views', 'dashboard.html')

@app.route('/admin')
def admin():
    return send_from_directory('views', 'admin.html')

@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        if USE_MYSQL:
            cur = get_cursor()
            cur.execute('INSERT INTO users (name, email, phone, password, role) VALUES (%s,%s,%s,%s,%s)', (name, email, phone, password, 'user'))
            MYSQL_CONN.commit()
        else:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute('INSERT INTO users (name, email, phone, password, role) VALUES (?,?,?,?,?)', (name, email, phone, password, 'user'))
            conn.commit()
            conn.close()
        return jsonify({'success': True, 'message': 'Registration successful'})
    except Exception as err:
        if 'Duplicate entry' in str(err) or 'UNIQUE constraint failed' in str(err):
            return jsonify({'success': False, 'message': 'Email already registered'})
        return jsonify({'success': False, 'message': 'Registration failed', 'error': str(err)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = None
        if USE_MYSQL:
            cur = get_cursor()
            cur.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password))
            user = dict_row(cur)
            MYSQL_CONN.close()
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
            row = cur.fetchone()
            if row:
                user = dict(row)
            conn.close()
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
        return jsonify({'success': True, 'message': 'Login successful', 'user': {'id': user['id'], 'name': user['name'], 'email': user['email'], 'role': user['role']}})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Login failed', 'error': str(err)}), 500

@app.route('/api/routes', methods=['GET'])
def api_routes():
    try:
        from_city = request.args.get('from', '')
        to_city = request.args.get('to', '')
        date = request.args.get('date', '')
        routes = []
        if USE_MYSQL:
            cur = get_cursor()
            sql = 'SELECT * FROM routes WHERE 1=1'
            params = []
            if from_city:
                sql += ' AND from_city LIKE %s'
                params.append(f'%{from_city}%')
            if to_city:
                sql += ' AND to_city LIKE %s'
                params.append(f'%{to_city}%')
            if date:
                sql += ' AND date = %s'
                params.append(date)
            sql += ' ORDER BY date, departure_time'
            cur.execute(sql, params)
            routes = dict_rows(cur)
            MYSQL_CONN.close()
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            sql = 'SELECT * FROM routes WHERE 1=1'
            params = []
            if from_city:
                sql += ' AND from_city LIKE ?'
                params.append(f'%{from_city}%')
            if to_city:
                sql += ' AND to_city LIKE ?'
                params.append(f'%{to_city}%')
            if date:
                sql += ' AND date = ?'
                params.append(date)
            sql += ' ORDER BY date, departure_time'
            cur.execute(sql, params)
            routes = [dict(row) for row in cur.fetchall()]
            conn.close()
        return jsonify({'success': True, 'routes': routes})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to load routes', 'error': str(err)}), 500

@app.route('/api/book', methods=['POST'])
def api_book():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        route_id = data.get('routeId')
        seats = data.get('seats')
        passenger_name = data.get('passengerName')
        passenger_phone = data.get('passengerPhone')
        payment_method = data.get('paymentMethod', 'cash')
        if USE_MYSQL:
            cur = get_cursor()
            cur.execute('SELECT * FROM routes WHERE id = %s', (route_id,))
            route = dict_row(cur)
            if not route:
                return jsonify({'success': False, 'message': 'Route not found'}), 404
            total_price = route['price'] * seats
            cur.execute('INSERT INTO bookings (user_id, route_id, seats, total_price, passenger_name, passenger_phone, payment_method, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                        (user_id, route_id, seats, total_price, passenger_name, passenger_phone, payment_method, 'confirmed'))
            MYSQL_CONN.commit()
            last_id = cur.lastrowid
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM routes WHERE id = ?', (route_id,))
            route = cur.fetchone()
            if not route:
                conn.close()
                return jsonify({'success': False, 'message': 'Route not found'}), 404
            route = dict(route)
            total_price = route['price'] * seats
            cur.execute('INSERT INTO bookings (user_id, route_id, seats, total_price, passenger_name, passenger_phone, payment_method, status) VALUES (?,?,?,?,?,?,?,?)',
                        (user_id, route_id, seats, total_price, passenger_name, passenger_phone, payment_method, 'confirmed'))
            conn.commit()
            last_id = cur.lastrowid
            conn.close()
        return jsonify({'success': True, 'message': 'Booking confirmed!', 'bookingId': last_id, 'totalPrice': total_price})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Booking failed', 'error': str(err)}), 500

@app.route('/api/bookings/<int:user_id>', methods=['GET'])
def api_bookings(user_id):
    try:
        param_fmt = '%s' if USE_MYSQL else '?'
        conn = None
        if USE_MYSQL:
            conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
        cur = conn.cursor(dictionary=True) if USE_MYSQL else conn.cursor()
        sql = '''SELECT b.*, r.from_city, r.to_city, r.date, r.departure_time, r.arrival_time, r.bus_name, r.price as route_price
                 FROM bookings b
                 JOIN routes r ON b.route_id = r.id
                 WHERE b.user_id = ''' + param_fmt + '''
                 ORDER BY b.booking_date DESC'''
        cur.execute(sql, (user_id,))
        bookings = dict_rows(cur)
        conn.close()
        return jsonify({'success': True, 'bookings': bookings})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to load bookings', 'error': str(err)}), 500

@app.route('/api/bookings/cancel', methods=['POST'])
def api_cancel():
    try:
        data = request.get_json()
        booking_id = data.get('bookingId')
        user_id = data.get('userId')
        param_fmt = '%s' if USE_MYSQL else '?'
        conn = None
        if USE_MYSQL:
            conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
        cur = conn.cursor(dictionary=True) if USE_MYSQL else conn.cursor()
        cur.execute(f'UPDATE bookings SET status = {param_fmt} WHERE id = {param_fmt} AND user_id = {param_fmt}', ('cancelled', booking_id, user_id))
        conn.commit()
        conn.close()
        if USE_MYSQL:
            return jsonify({'success': True, 'message': 'Booking cancelled'})
        if cur.rowcount == 0:
            return jsonify({'success': False, 'message': 'Booking not found'}), 404
        return jsonify({'success': True, 'message': 'Booking cancelled'})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Cancellation failed', 'error': str(err)}), 500

@app.route('/api/stats', methods=['GET'])
def api_stats():
    try:
        conn = get_cursor()
        if USE_MYSQL:
            conn.execute('SELECT COUNT(*) as count FROM users')
            total_users = conn.fetchone()['count']
            conn.execute('SELECT COUNT(*) as count FROM routes')
            total_routes = conn.fetchone()['count']
            conn.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'confirmed'")
            total_bookings = conn.fetchone()['count']
            conn.execute("SELECT SUM(total_price) as amount FROM bookings WHERE status = 'confirmed'")
            revenue = conn.fetchone()['amount'] or 0
            MYSQL_CONN.close()
        else:
            cur = conn
            cur.execute('SELECT COUNT(*) as count FROM users')
            total_users = cur.fetchone()['count']
            cur.execute('SELECT COUNT(*) as count FROM routes')
            total_routes = cur.fetchone()['count']
            cur.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'confirmed'")
            total_bookings = cur.fetchone()['count']
            cur.execute("SELECT SUM(total_price) as amount FROM bookings WHERE status = 'confirmed'")
            revenue = cur.fetchone()['amount'] or 0
            cur.connection.close()
        return jsonify({'success': True, 'stats': {'totalUsers': total_users, 'totalRoutes': total_routes, 'totalBookings': total_bookings, 'revenue': revenue}})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to load stats', 'error': str(err)}), 500

@app.route('/api/all-bookings', methods=['GET'])
def api_all_bookings():
    try:
        conn = None
        if USE_MYSQL:
            conn = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB)
            cur = conn.cursor(dictionary=True)
        else:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
        sql = '''SELECT b.*, u.name as user_name, r.from_city, r.to_city, r.date, r.departure_time, r.arrival_time
                 FROM bookings b
                 JOIN users u ON b.user_id = u.id
                 JOIN routes r ON b.route_id = r.id
                 ORDER BY b.booking_date DESC'''
        cur.execute(sql)
        bookings = dict_rows(cur)
        conn.close()
        return jsonify({'success': True, 'bookings': bookings})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to load bookings', 'error': str(err)}), 500

@app.route('/api/add-route', methods=['POST'])
def api_add_route():
    try:
        data = request.get_json()
        from_city = data.get('fromCity')
        to_city = data.get('toCity')
        date = data.get('date')
        departure_time = data.get('departureTime')
        arrival_time = data.get('arrivalTime')
        bus_name = data.get('busName')
        price = data.get('price')
        seats_available = data.get('seatsAvailable')
        param_fmt = '%s' if USE_MYSQL else '?'
        cur = get_cursor()
        cur.execute(f'INSERT INTO routes (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available) VALUES ({param_fmt},{param_fmt},{param_fmt},{param_fmt},{param_fmt},{param_fmt},{param_fmt},{param_fmt})',
                    (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available))
        if USE_MYSQL:
            MYSQL_CONN.commit()
            MYSQL_CONN.close()
        else:
            cur.connection.commit()
            cur.connection.close()
        return jsonify({'success': True, 'message': 'Route added successfully', 'routeId': cur.lastrowid})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to add route', 'error': str(err)}), 500

@app.route('/api/buses', methods=['GET'])
def api_buses():
    try:
        cur = get_cursor()
        cur.execute('SELECT * FROM buses ORDER BY bus_name')
        buses = dict_rows(cur)
        if USE_MYSQL:
            MYSQL_CONN.close()
        else:
            cur.connection.close()
        return jsonify({'success': True, 'buses': buses})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to load buses', 'error': str(err)}), 500

@app.route('/api/add-bus', methods=['POST'])
def api_add_bus():
    try:
        data = request.get_json()
        bus_name = data.get('busName')
        bus_type = data.get('busType')
        total_seats = data.get('totalSeats')
        amenities = data.get('amenities')
        param_fmt = '%s' if USE_MYSQL else '?'
        cur = get_cursor()
        cur.execute(f'INSERT INTO buses (bus_name, bus_type, total_seats, amenities) VALUES ({param_fmt},{param_fmt},{param_fmt},{param_fmt})',
                    (bus_name, bus_type, total_seats, amenities))
        if USE_MYSQL:
            MYSQL_CONN.commit()
            MYSQL_CONN.close()
        else:
            cur.connection.commit()
            cur.connection.close()
        return jsonify({'success': True, 'message': 'Bus added successfully', 'busId': cur.lastrowid})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to add bus', 'error': str(err)}), 500

@app.route('/api/add-feedback', methods=['POST'])
def api_add_feedback():
    try:
        data = request.get_json()
        user_id = data.get('userId')
        bus_id = data.get('busId')
        rating = data.get('rating')
        comment = data.get('comment')
        param_fmt = '%s' if USE_MYSQL else '?'
        cur = get_cursor()
        cur.execute(f'INSERT INTO feedback (user_id, bus_id, rating, comment) VALUES ({param_fmt},{param_fmt},{param_fmt},{param_fmt})',
                    (user_id, bus_id, rating, comment))
        if USE_MYSQL:
            MYSQL_CONN.commit()
            MYSQL_CONN.close()
        else:
            cur.connection.commit()
            cur.connection.close()
        return jsonify({'success': True, 'message': 'Feedback submitted', 'feedbackId': cur.lastrowid})
    except Exception as err:
        return jsonify({'success': False, 'message': 'Failed to submit feedback', 'error': str(err)}), 500

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=PORT, debug=True)
