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
CREATE TABLE IF NOT EXISTS payments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  booking_id INTEGER NOT NULL,
  amount REAL NOT NULL,
  payment_method TEXT NOT NULL,
  payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
  status TEXT DEFAULT 'completed',
  FOREIGN KEY (booking_id) REFERENCES bookings(id)
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
INSERT INTO users (name, email, phone, password, role) VALUES ('Admin', 'admin@bus.com', '9876543210', 'admin123', 'admin');
INSERT INTO buses (bus_name, bus_type, total_seats, amenities) VALUES
  ('Volvo AC', 'AC Seater', 20, 'WiFi, AC, Water Bottle'),
  ('Sleeper', 'Non-AC Sleeper', 15, 'Pillow, Blanket'),
  ('Volvo Sleeper', 'AC Sleeper', 30, 'WiFi, AC, Pillow, Blanket'),
  ('AC Seater', 'AC Seater', 25, 'AC, Charging Point');
INSERT INTO routes (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available) VALUES
  ('Mumbai', 'Pune', date('now', '+1 day'), '08:00', '11:30', 'Volvo AC', 500, 20),
  ('Bengalore', 'Mysore', date('now', '+1 day'), '14:00', '17:30', 'Sleeper', 450, 15),
  ('Mumbai', 'Goa', date('now', '+2 day'), '20:00', '08:00', 'Volvo Sleeper', 1200, 30),
  ('Delhi', 'Chennai', date('now', '+3 day'), '06:00', '10:00', 'AC Seater', 400, 25),
  ('Delhi', 'Jaipur', date('now', '+3 day'), '15:00', '19:00', 'Sleeper', 350, 20);

INSERT INTO feedback (user_id, bus_id, rating, comment) VALUES
  (1, 1, 5, 'Great service and comfortable seat.'),
  (1, 2, 4, 'Good trip, on time arrival.');
