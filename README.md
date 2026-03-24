# Auth and Task Management API

This is a backend project built using FastAPI that provides authentication, user management, and task management with proper access control.

## Features

### Authentication
- User signup and login
- Password hashing
- JWT-based authentication (access and refresh tokens)
- Protected routes
- Logout functionality

### User Management
- Get current user details
- Update user profile
- Role-based access control (admin and user)
- Admin can view all users
- Admin can delete users

### Task Management
- Create tasks for logged-in users
- Get tasks for the current user only
- Update tasks with ownership validation
- Delete tasks with ownership validation
- Filter tasks by completion status

## Tech Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- Passlib
- python-jose

## API Endpoints

### Auth
- POST /auth/signup
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout

### Users
- GET /users/me
- PUT /users/me
- GET /users/all (admin only)
- DELETE /users/{id} (admin only)

### Tasks
- POST /tasks
- GET /tasks
- PUT /tasks/{id}
- DELETE /tasks/{id}

## How to Run

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd auth_user_management
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the environment:

   Windows:
   ```bash
   venv\Scripts\activate
   ```

   Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a .env file and add:
   ```
   DATABASE_URL=your_database_url
   SECRET_KEY=your_secret_key
   ```

6. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Key Concepts

- JWT authentication
- Role-based access control
- Database relationships (user and tasks)
- Ownership validation for secure data access

## Author

Salman