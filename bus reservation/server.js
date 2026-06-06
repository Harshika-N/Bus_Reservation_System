const express = require('express');
const path = require('path');
const { initializeDatabase, getDb } = require('./database');
const app = express();
const PORT = 3000;
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/assets', express.static(path.join(__dirname, 'assets')));
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'index.html'));
});
app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'register.html'));
});
app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'login.html'));
});
app.get('/search', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'search.html'));
});
app.get('/dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'dashboard.html'));
});
app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'admin.html'));
});
app.post('/api/register', (req, res) => {
  try {
    const { name, email, phone, password } = req.body;
    if (!name || !email || !phone || !password) {
      return res.status(400).json({ success: false, message: 'Please complete all registration fields' });
    }
    const db = getDb();
    const stmt = db.prepare('INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)');
    const result = stmt.run(name.trim(), email.trim().toLowerCase(), phone.trim(), password, 'user');
    if (result.changes === 0) {
      return res.json({ success: false, message: 'Email already registered' });
    }
    res.json({ success: true, message: 'Registration successful' });
  } catch (err) {
    console.error('Registration error:', err.message);
    if (err.message.includes('UNIQUE constraint failed')) {
      return res.json({ success: false, message: 'Email already registered' });
    }
    res.status(500).json({ success: false, message: 'Registration failed', error: err.message });
  }
});
app.post('/api/login', (req, res) => {
  try {
    const { email, password } = req.body;
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM users WHERE email = ? AND password = ?');
    const user = stmt.get(email, password);
    if (!user) {
      return res.json({ success: false, message: 'Invalid credentials' });
    }
    res.json({ success: true, message: 'Login successful', user: { id: user.id, name: user.name, email: user.email, role: user.role } });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Login failed', error: err.message });
  }
});
app.get('/api/routes', (req, res) => {
  try {
    const { from, to, date } = req.query;
    const db = getDb();
    let sql = 'SELECT * FROM routes WHERE 1=1';
    const params = [];
    if (from) { sql += ' AND from_city LIKE ?'; params.push(`%${from}%`); }
    if (to) { sql += ' AND to_city LIKE ?'; params.push(`%${to}%`); }
    if (date) { sql += ' AND date = ?'; params.push(date); }
    sql += ' ORDER BY date, departure_time';
    const stmt = db.prepare(sql);
    const routes = stmt.all(...params);
    res.json({ success: true, routes });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load routes', error: err.message });
  }
});
app.post('/api/book', (req, res) => {
  try {
    const { userId, routeId, seats, passengerName, passengerPhone, paymentMethod } = req.body;
    const db = getDb();
    const routeStmt = db.prepare('SELECT * FROM routes WHERE id = ?');
    const route = routeStmt.get(routeId);
    if (!route) {
      return res.status(404).json({ success: false, message: 'Route not found' });
    }
    const totalPrice = route.price * seats;
    const bookingStmt = db.prepare('INSERT INTO bookings (user_id, route_id, seats, total_price, passenger_name, passenger_phone, payment_method, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
    const result = bookingStmt.run(userId, routeId, seats, totalPrice, passengerName, passengerPhone, paymentMethod || 'cash', 'confirmed');
    res.json({ success: true, message: 'Booking confirmed!', bookingId: result.lastInsertRowid, totalPrice });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Booking failed', error: err.message });
  }
});
app.get('/api/bookings/:userId', (req, res) => {
  try {
    const db = getDb();
    const sql = `SELECT b.*, r.from_city, r.to_city, r.date, r.departure_time, r.arrival_time, r.bus_name, r.price as route_price
                 FROM bookings b
                 JOIN routes r ON b.route_id = r.id
                 WHERE b.user_id = ?
                 ORDER BY b.booking_date DESC`;
    const stmt = db.prepare(sql);
    const bookings = stmt.all(req.params.userId);
    res.json({ success: true, bookings });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load bookings', error: err.message });
  }
});
app.post('/api/bookings/cancel', (req, res) => {
  try {
    const { bookingId, userId } = req.body;
    const db = getDb();
    const stmt = db.prepare('UPDATE bookings SET status = ? WHERE id = ? AND user_id = ?');
    const result = stmt.run('cancelled', bookingId, userId);
    if (result.changes === 0) {
      return res.status(404).json({ success: false, message: 'Booking not found' });
    }
    res.json({ success: true, message: 'Booking cancelled' });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Cancellation failed', error: err.message });
  }
});
app.get('/api/stats', (req, res) => {
  try {
    const db = getDb();
    const usersStmt = db.prepare('SELECT COUNT(*) as count FROM users');
    const totalUsers = usersStmt.get().count;
    const routesStmt = db.prepare('SELECT COUNT(*) as count FROM routes');
    const totalRoutes = routesStmt.get().count;
    const bookingsStmt = db.prepare('SELECT COUNT(*) as count FROM bookings WHERE status = ?');
    const totalBookings = bookingsStmt.get('confirmed').count;
    const revenueStmt = db.prepare('SELECT SUM(total_price) as amount FROM bookings WHERE status = ?');
    const revenue = revenueStmt.get('confirmed').amount || 0;
    res.json({ success: true, stats: { totalUsers, totalRoutes, totalBookings, revenue } });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load stats', error: err.message });
  }
});
app.get('/api/all-bookings', (req, res) => {
  try {
    const db = getDb();
    const sql = `SELECT b.*, u.name as user_name, r.from_city, r.to_city, r.date, r.departure_time, r.arrival_time
                 FROM bookings b
                 JOIN users u ON b.user_id = u.id
                 JOIN routes r ON b.route_id = r.id
                 ORDER BY b.booking_date DESC`;
    const stmt = db.prepare(sql);
    res.json({ success: true, bookings: stmt.all() });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load bookings', error: err.message });
  }
});
app.post('/api/add-route', (req, res) => {
  try {
    const { fromCity, toCity, departureTime, arrivalTime, busName, price, seatsAvailable } = req.body;
    const date = req.body.date || req.body.routeDate;
    if (!fromCity || !toCity || !date || !departureTime || !arrivalTime || !busName || !price || !seatsAvailable) {
      return res.status(400).json({ success: false, message: 'Please provide all route fields' });
    }
    const db = getDb();
    const stmt = db.prepare('INSERT INTO routes (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
    const result = stmt.run(fromCity.trim(), toCity.trim(), date, departureTime, arrivalTime, busName.trim(), Number(price), Number(seatsAvailable));
    res.json({ success: true, message: 'Route added successfully', routeId: result.lastInsertRowid });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to add route', error: err.message });
  }
});
app.get('/api/buses', (req, res) => {
  try {
    const db = getDb();
    const stmt = db.prepare('SELECT * FROM buses ORDER BY bus_name');
    res.json({ success: true, buses: stmt.all() });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to load buses', error: err.message });
  }
});
app.post('/api/add-bus', (req, res) => {
  try {
    const { busName, busType, totalSeats, amenities } = req.body;
    if (!busName || !busType || !totalSeats) {
      return res.status(400).json({ success: false, message: 'Please provide bus name, type, and total seats' });
    }
    const db = getDb();
    const stmt = db.prepare('INSERT INTO buses (bus_name, bus_type, total_seats, amenities) VALUES (?, ?, ?, ?)');
    const result = stmt.run(busName.trim(), busType.trim(), Number(totalSeats), amenities ? amenities.trim() : null);
    res.json({ success: true, message: 'Bus added successfully', busId: result.lastInsertRowid });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to add bus', error: err.message });
  }
});
app.post('/api/add-feedback', (req, res) => {
  try {
    const { userId, busId, rating, comment } = req.body;
    const db = getDb();
    const stmt = db.prepare('INSERT INTO feedback (user_id, bus_id, rating, comment) VALUES (?, ?, ?, ?)');
    const result = stmt.run(userId, busId, rating, comment);
    res.json({ success: true, message: 'Feedback submitted', feedbackId: result.lastInsertRowid });
  } catch (err) {
    res.status(500).json({ success: false, message: 'Failed to submit feedback', error: err.message });
  }
});
initializeDatabase().then(() => {
  app.listen(PORT, () => {
    console.log(`Bus Reservation System running at http://localhost:${PORT}`);
  });
});
