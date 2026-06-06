import sqlite3
from datetime import datetime, timedelta

db_path = 'bus_reservation.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Add missing routes
base_date = datetime.now().date()

new_routes = [
    ('Bangalore', 'Mysore', (base_date + timedelta(days=1)).isoformat(), '07:00', '10:00', 'AC Seater', 300, 25),
    ('Bangalore', 'Mysore', (base_date + timedelta(days=1)).isoformat(), '15:00', '18:00', 'Sleeper', 250, 20),
    ('Delhi', 'Chennai', (base_date + timedelta(days=2)).isoformat(), '06:00', '14:00', 'Volvo AC', 2500, 30),
    ('Delhi', 'Chennai', (base_date + timedelta(days=2)).isoformat(), '18:00', '02:00', 'Sleeper', 2000, 25),
]

for route in new_routes:
    try:
        cur.execute(
            'INSERT INTO routes (from_city, to_city, date, departure_time, arrival_time, bus_name, price, seats_available) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            route
        )
        print(f"✓ Added: {route[0]} → {route[1]} on {route[2]}")
    except Exception as e:
        print(f"✗ Error adding {route[0]} → {route[1]}: {e}")

conn.commit()
conn.close()

print("\n✓ Routes added successfully!")
