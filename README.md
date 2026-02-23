
# 🚗 GaragePro – Vehicle Service Management System

## 📌 Project Overview
GaragePro is a web-based vehicle service management system designed for garages and automobile service centers.
It helps manage customers, vehicles, service bookings, mechanics, and invoices with proper backend validation
and role-based access control.

---

## 🎯 Project Statement
GaragePro is a web-based application designed for garages and automobile service centers to manage customer vehicles,
service bookings, mechanic assignments, spare parts usage, and invoice generation. The system streamlines daily
operations, improves service accuracy, and helps the garage maintain digital records.

---

## 🛠️ Tools & Technologies
- Python 3.x
- Flask Framework
- HTML, CSS
- PostgreSQL
- SQLAlchemy ORM
- pgAdmin
- GitHub
- VS Code
- thunder client

---

## 📚 Python Libraries
- Flask
- Flask-Login
- Flask-Session
- SQLAlchemy
- psycopg2
- Werkzeug Security
- ReportLab
- datetime
- python-dotenv

---

## 🏗️ Project Structure
```
garage-management/
│
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
│
├── models/
│   ├── user.py
│   ├── customer.py
│   ├── vehicle.py
│   ├── mechanic.py
│   ├── service_request.py
│   └── invoice.py
│
├── routes/
│   ├── auth_routes.py
│   ├── customer_routes.py
│   ├── vehicle_routes.py
│   ├── mechanic_routes.py
│   ├── service_routes.py
│   ├── invoice_routes.py
│   └── ui_routes.py
│
├── templates/
├── static/
└── README.md
```

---

## 🔐 User Roles
- Admin
- Staff

---

## 🔄 System Workflow
1. Admin login
2. Create customer
3. Add vehicle
4. Add mechanic
5. Create service request
6. Assign mechanic
7. Generate invoice
8. Update payment status

---

## 🧪 Testing
- API testing using Thunder Clent
- UI testing via browser
- Validation testing for duplicates and constraints

---


