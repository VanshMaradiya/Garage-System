Garage Management System – API Documentation

Base URL:
http://127.0.0.1:5000

All APIs return JSON responses.

1️⃣ Authentication APIs
Register User

URL:
/api/auth/register

Method:
POST

Request Body:

{
  "username": "admin",
  "email": "admin@gmail.com",
  "password": "admin123",
  "role": "admin"
}


Success Response (201):

{
  "message": "User registered successfully"
}


Error Responses:

400 – Missing fields / Duplicate email

500 – Server error

Login User

URL:
/api/auth/login

Method:
POST

Request Body:

{
  "email": "admin@gmail.com",
  "password": "admin123"
}


Success Response (200):

{
  "message": "Login successful",
  "user_id": 1
}


Error Responses:

401 – Invalid credentials

400 – Missing fields

Logout User

URL:
/api/auth/logout

Method:
POST

Success Response (200):

{
  "message": "Logged out successfully"
}

2️⃣ Customer APIs
Create Customer

URL:
/api/customers

Method:
POST

Request Body:

{
  "name": "Ravi Patel",
  "phone": "9999999999"
}


Success Response (201):

{
  "id": 1,
  "name": "Ravi Patel",
  "phone": "9999999999"
}


Error Responses:

400 – Missing fields

Get All Customers

URL:
/api/customers

Method:
GET

Success Response (200):

[
  {
    "id": 1,
    "name": "Ravi Patel",
    "phone": "9999999999"
  }
]

3️⃣ Vehicle APIs
Create Vehicle

URL:
/api/vehicles

Method:
POST

Request Body:

{
  "customer_id": 1,
  "vehicle_number": "GJ01AB1234",
  "vehicle_type": "Car",
  "brand": "Honda",
  "model": "City"
}


Success Response (201):

{
  "id": 1,
  "vehicle_number": "GJ01AB1234",
  "customer_id": 1
}


Error Responses:

404 – Customer not found

400 – Duplicate vehicle number

Get All Vehicles

URL:
/api/vehicles

Method:
GET

Success Response (200):

[
  {
    "id": 1,
    "vehicle_number": "GJ01AB1234",
    "brand": "Honda",
    "model": "City"
  }
]

4️⃣ Mechanic APIs
Create Mechanic

URL:
/api/mechanics

Method:
POST

Request Body:

{
  "name": "Suresh",
  "phone": "8888888888",
  "specialization": "Engine"
}


Success Response (201):

{
  "id": 1,
  "name": "Suresh"
}

Get All Mechanics

URL:
/api/mechanics

Method:
GET

Success Response (200):

[
  {
    "id": 1,
    "name": "Suresh",
    "specialization": "Engine"
  }
]

5️⃣ Service Request APIs
Create Service Request

URL:
/api/service-requests

Method:
POST

Request Body:

{
  "vehicle_id": 1,
  "service_type": "Brake Repair",
  "service_date": "2025-01-10",
  "problem_description": "Brake noise",
  "assigned_mechanic_id": 1
}


Success Response (201):

{
  "id": 1,
  "status": "Pending"
}


Error Responses:

404 – Vehicle not found

404 – Mechanic not found

400 – Missing fields

Get All Service Requests

URL:
/api/service-requests

Method:
GET

Success Response (200):

[
  {
    "id": 1,
    "vehicle_id": 1,
    "status": "Pending"
  }
]

Update Service Status

URL:
/api/service-requests/<id>

Method:
PUT

Request Body:

{
  "status": "Completed"
}


Success Response (200):

{
  "message": "Service updated successfully"
}

6️⃣ Invoice APIs
Create Invoice

URL:
/api/invoices

Method:
POST

Request Body:

{
  "service_request_id": 1,
  "amount": 4500
}


Success Response (201):

{
  "id": 1,
  "amount": 4500
}


Error Responses:

404 – Service request not found

400 – Duplicate invoice

Get All Invoices

URL:
/api/invoices

Method:
GET

Success Response (200):

[
  {
    "id": 1,
    "service_request_id": 1,
    "amount": 4500
  }
]

7️⃣ Status Values Reference
Service Status

Pending

In Progress

Completed

8️⃣ Backend Freeze Confirmation

APIs finalized

Database schema finalized

No breaking changes allowed before UI

✅ Next Step

You are officially backend-complete.
