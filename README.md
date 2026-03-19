# Auth & User Management System

This is a backend project built using FastAPI, MySQL, SQLAlchemy, and JWT.

## Features

- User signup
- User login
- Password hashing
- JWT authentication
- Protected routes
- Role-based authorization
- Refresh token
- Logout

## Tech Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- Passlib
- python-jose

## Endpoints

### Auth
- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

### Users
- `GET /users/me`
- `GET /users/all` (admin only)

## How to Run

1. Create virtual environment  
2. Install requirements  
3. Create `.env` file  
4. Create MySQL database  
5. Run server

```bash
uvicorn app.main:app --reload