# Bus Reservation System

DBNS Mini Project - Bus Reservation System built with Node.js, Express, and SQLite (better-sqlite3). A Flask alternative is also included.

## Features

- User registration and login
- Search buses by city, route, and date
- Book tickets with seat selection and payment method
- View and cancel previous bookings
- Admin panel for managing routes and buses
- Feedback and ratings for buses
- Responsive dashboard for users and admins

## Tech Stack

- **Backend:** Node.js, Express
- **Database:** SQLite (`better-sqlite3`)
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Alternative:** Python/Flask (`server.py`) + SQLite (requires `mysql.connector` for MySQL support)

## Getting Started

### Prerequisites

- Node.js (v14+)
- npm

### Installation

```powershell
cd "bus reservation"
npm install
```

### Run the Server

```powershell
npm start
```

Open your browser and go to `http://localhost:3000`

## Default Credentials

- **Admin:** `admin@bus.com` / `admin123`
- **User:** Register a new account via `/register`

## Project Structure

```
bus reservation/
├── server.js          # Express server and API routes
├── database.js        # SQLite database initialization and helpers
├── server.py          # Flask alternative server
├── add_routes.py      # Python utility to add sample routes
├── check_db.py        # Python utility to verify database
├── database.sql       # SQL schema
├── package.json
├── assets/
│   └── style.css
└── views/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── search.html
    ├── dashboard.html
    └── admin.html
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register a new user |
| POST | `/api/login` | User login |
| GET | `/api/routes` | Search available routes |
| POST | `/api/book` | Book a ticket |
| GET | `/api/bookings/:userId` | Get user bookings |
| POST | `/api/bookings/cancel` | Cancel a booking |
| GET | `/api/stats` | Admin statistics |
| GET | `/api/all-bookings` | Admin: all bookings |
| POST | `/api/add-route` | Admin: add route |
| GET | `/api/buses` | Get all buses |
| POST | `/api/add-bus` | Admin: add bus |
| POST | `/api/add-feedback` | Submit feedback |

## Flask Alternative

To run with Flask instead:

```powershell
pip install flask
python server.py
```

Set `USE_MYSQL=1` environment variable along with `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_DB` for MySQL support.

## Author
Harshika N
