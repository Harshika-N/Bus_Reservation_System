import sqlite3
import os

db_path = 'bus_reservation.db'

if os.path.exists(db_path):
    print("✓ Database file exists")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cur.fetchall()]
        print(f"✓ Tables found: {tables}")
        
        # Check users table
        if 'users' in tables:
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            print(f"✓ Users in database: {user_count}")
        
        conn.close()
    except Exception as e:
        print(f"✗ Database error: {e}")
else:
    print("✗ Database file NOT found")
