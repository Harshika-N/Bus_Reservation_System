const Database = require('better-sqlite3');
const path = require('path');
const dbPath = path.join(__dirname, 'bus_reservation.db');
const db = new Database(dbPath);
let initialized = false;
function initializeDatabase() {
  if (initialized) return Promise.resolve();
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      email TEXT UNIQUE NOT NULL,
      phone TEXT NOT NULL,
      password TEXT NOT NULL,
      role TEXT DEFAULT 'user',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  db.exec(`
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
    )
  `);
  db.exec(`
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
    )
  `);
  db.exec(`
    CREATE TABLE IF NOT EXISTS buses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      bus_name TEXT NOT NULL,
      bus_type TEXT NOT NULL,
      total_seats INTEGER NOT NULL,
      amenities TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  db.exec(`
    CREATE TABLE IF NOT EXISTS payments (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      booking_id INTEGER NOT NULL,
      amount REAL NOT NULL,
      payment_method TEXT NOT NULL,
      payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
      status TEXT DEFAULT 'completed',
      FOREIGN KEY (booking_id) REFERENCES bookings(id)
    )
  `);
  db.exec(`
    CREATE TABLE IF NOT EXISTS feedback (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      bus_id INTEGER NOT NULL,
      rating INTEGER NOT NULL,
      comment TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id),
      FOREIGN KEY (bus_id) REFERENCES buses(id)
    )
  `);
  const adminCheck = db.prepare('SELECT * FROM users WHERE email = ?').get('admin@bus.com');
  if (!adminCheck) {
    db.prepare('INSERT INTO users (name, email, phone, password, role) VALUES (?, ?, ?, ?, ?)').run('Admin', 'admin@bus.com', '9876543210', 'admin123', 'admin');
  }
  const busExists = db.prepare('SELECT COUNT(*) as count FROM buses').get();
  if (busExists.count === 0) {
    const insertBus = db.prepare('INSERT INTO buses (bus_name, bus_type, total_seats, amenities) VALUES (?, ?, ?, ?)');
    insertBus.run('Volvo AC', 'AC Seater', 20, 'WiFi, AC, Water Bottle');
    insertBus.run('Sleeper', 'Non-AC Sleeper', 15, 'Pillow, Blanket');
    insertBus.run('Volvo Sleeper', 'AC Sleeper', 30, 'WiFi, AC, Pillow, Blanket');
    insertBus.run('AC Seater', 'AC Seater', 25, 'AC, Charging Point');
  }
  const routeExists = db.prepare('SELECT COUNT(*) as count FROM routes').get();
  if (routeExists.count === 0) {
    const insertRoute = db.prepare('INSERT INTO routes (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)');
    const today = new Date();
    const formatDate = date => date.toISOString().split('T')[0];
    insertRoute.run('Mumbai', 'Pune', formatDate(new Date(today.getTime() + 1 * 24 * 60 * 60 * 1000)), '08:00', '11:30', 'Volvo AC', 500, 20);
    insertRoute.run('Mumbai', 'Pune', formatDate(new Date(today.getTime() + 1 * 24 * 60 * 60 * 1000)), '14:00', '17:30', 'Sleeper', 450, 15);
    insertRoute.run('Mumbai', 'Goa', formatDate(new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000)), '20:00', '08:00', 'Volvo Sleeper', 1200, 30);
    insertRoute.run('Delhi', 'Jaipur', formatDate(new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000)), '06:00', '10:00', 'AC Seater', 400, 25);
    insertRoute.run('Delhi', 'Jaipur', formatDate(new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000)), '15:00', '19:00', 'Sleeper', 350, 20);
  }
  initialized = true;
  return Promise.resolve();
}
function getDb() {
  if (!initialized) {
    throw new Error('Database not initialized. Call initializeDatabase() first.');
  }
  return db;
}
module.exports = { initializeDatabase, getDb, db };
