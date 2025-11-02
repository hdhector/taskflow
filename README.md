# TaskFlow API

## Overview

This project is a simple but complete **Task Management REST API** built with **Django 5.2** and **Django REST Framework (DRF)**.
It provides functionality for creating, editing, listing, and managing tasks with user authentication through JWT tokens.

The API allows users to create and manage their own tasks, organize them by priority and status, and register comments or progress updates. Authentication is handled via JWT tokens to ensure that each user can only manage their own data. Additionally, the system enforces a business rule that limits each user to a maximum of five active (incomplete) tasks.

The project also includes automated tests and a command for generating fake data for testing purposes.

The main purpose of this repository is to demonstrate Django and DRF development skills, including model design, API structure, permissions, and testing.

---

## Dependencies and Technologies Used

**Core Frameworks:**

* Django 5.2
* Django REST Framework (DRF)

**Authentication:**

* djangorestframework-simplejwt

**Database:**

* PostgreSQL (can be replaced with SQLite for local use)

**Other Packages:**

* django-filter (for filtering and searching)
* Faker (for generating fake test data)
* django-unfold (modern admin interface theme)

---

## Project Structure

```
taskflow/
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── tasks/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── management/
│   │   └── commands/
│   │       └── load_tasks.py        # Command to generate fake data
│   ├── migrations/
│   ├── models.py                    # Task and Comment models
│   ├── permissions.py               # Custom permission classes
│   ├── serializers.py               # DRF serializers
│   ├── tests.py                     # Test suite (API and logic)
│   ├── urls.py                      # API routes for the app
│   └── views.py                     # ViewSets for Task and Comment
│
├── Dockerfile                       # Docker image configuration
├── docker-compose.yml               # Docker Compose orchestration
├── entrypoint.sh                    # Startup script for Docker container
├── deploy.sh                        # Automated deployment script
├── .env.example                     # Example environment variables template
├── .dockerignore                    # Files to exclude from Docker build
├── manage.py
└── README.md
```

---

## Installation (Standalone Environment)

1. **Clone the repository**

   ```bash
   git clone https://github.com/hdhector/taskflow.git
   cd taskflow
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate      
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**

   By default, the project expects PostgreSQL.
   Edit the connection parameters in `core/settings.py`:

   ```python
   DATABASES = {
       "default": {
           "ENGINE": "django.db.backends.postgresql",
           "NAME": "taskflow",
           "USER": "postgres",
           "PASSWORD": "postgres",
           "HOST": "localhost",
           "PORT": "5432",
       }
   }
   ```

5. **Run migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**

   ```bash
   python manage.py runserver
   ```

   The API will be available at:
   `http://127.0.0.1:8000/api/`

   The Django admin interface (with django-unfold theme) will be available at:
   `http://127.0.0.1:8000/admin/`

---

## Installation with Docker (Recommended)

The project includes Docker configuration for easy deployment and development. This method automatically sets up PostgreSQL, runs migrations, creates a superuser, and starts the development server.

### Prerequisites

* Docker
* Docker Compose

### Quick Start

1. **Clone the repository**

   ```bash
   git clone https://github.com/hdhector/taskflow.git
   cd taskflow
   ```

2. **Create environment file**

   Create a `.env` file in the project root with the following variables:

   ```env
   # Database configuration
   POSTGRES_DB=taskflow
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_HOST=db
   POSTGRES_PORT=5432

   # Django configuration
   DEBUG=True
   ALLOWED_HOSTS=*
   SECRET_KEY=your-secret-key-here

   # Superuser (optional, defaults shown)
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@example.com
   DJANGO_SUPERUSER_PASSWORD=admin123
   ```

3. **Build and start containers**

   ```bash
   docker compose up --build
   ```

   This will:
   * Build the Django application container
   * Start PostgreSQL database
   * Run database migrations automatically
   * Create a superuser (if it doesn't exist)
   * Start the Django development server

4. **Access the API and Admin**

   The API will be available at:
   `http://localhost:8000/api/`

   The Django admin interface (with django-unfold theme) will be available at:
   `http://localhost:8000/admin/`

### Docker Commands

**Start services in the background:**
```bash
docker compose up -d
```

**Stop services:**
```bash
docker compose down
```

**View logs:**
```bash
docker compose logs -f web
```

**Run management commands:**
```bash
docker compose exec web python manage.py load_tasks
docker compose exec web python manage.py createsuperuser
```

**Run tests:**
```bash
docker compose exec web python manage.py test tasks
```

### Deploy Script

The project includes an automated deployment script (`deploy.sh`) that simplifies initial setup and application deployment.

**Script Features:**

* **Environment file verification**: Automatically checks for `.env` file and creates it from `.env.example` if missing
* **Docker verification**: Validates that Docker is installed and running
* **Docker Compose detection**: Automatically detects and uses `docker-compose` or `docker compose` based on system availability
* **Automatic container building**: Builds all necessary Docker images
* **Background deployment**: Starts services in detached mode (`-d`)

**Using the deployment script:**

```bash
chmod +x deploy.sh
./deploy.sh
```

The script will automatically:

1. **Check and create `.env` file**: If `.env` doesn't exist, it will be created from `.env.example`
2. **Verify Docker installation**: Ensures Docker is installed and the daemon is running
3. **Verify Docker Compose**: Checks for Docker Compose availability (supports both `docker-compose` and `docker compose` commands)
4. **Build containers**: Builds all Docker images required for the application
5. **Start services**: Launches all services in detached mode

**Important Notes:**

* If the script creates `.env` from `.env.example`, you must edit it manually with your configuration values
* **Critical for production**: Change the `SECRET_KEY` in the `.env` file before deploying to production
* The script automatically uses the appropriate Docker Compose command available on your system (`docker-compose` or `docker compose`)

**Post-deployment:**

The application will be available at: `http://localhost:8000`


### Entrypoint Script

The `entrypoint.sh` script automatically handles:

* **Database readiness check**: Waits for PostgreSQL to be available before proceeding
* **Migrations**: Applies all database migrations automatically
* **Superuser creation**: Creates a Django superuser if one doesn't exist (configurable via environment variables)
* **Static files**: Collects static files for the application
* **Server startup**: Launches the Django development server on `0.0.0.0:8000`

The script uses environment variables for configuration, making it easy to customize the setup without modifying the script.

---

## Authentication and Access

Authentication is handled with JWT (JSON Web Tokens) via **SimpleJWT**.

### Obtain a token

```
POST /api/token/
{
  "username": "user1",
  "password": "pass1234"
}
```

### Refresh a token

```
POST /api/token/refresh/
{
  "refresh": "<refresh_token>"
}
```

Include the token in the `Authorization` header for all API requests:

```
Authorization: Bearer <access_token>
```

---

## API Endpoints

| Method                  | Endpoint                    | Description                        |
| ----------------------- | --------------------------- | ---------------------------------- |
| POST                    | `/api/token/`               | Obtain JWT token                   |
| POST                    | `/api/token/refresh/`       | Refresh JWT token                  |
| GET, POST               | `/api/tasks/`               | List or create tasks               |
| GET, PUT, PATCH, DELETE | `/api/tasks/<id>/`          | Retrieve, update or delete a task  |
| GET, POST               | `/api/tasks/<id>/comments/` | List or create comments for a task |

**Filtering and Search Examples**

```
/api/tasks/?status=pending
/api/tasks/?priority=high
/api/tasks/?search=meeting
```

---

## Tests

All tests are implemented in `tasks/tests.py` using Django’s `APITestCase`.

To run the full test suite:
```bash
python manage.py test tasks
```

Example output:

```
Creating test database for alias 'default'...
Found 5 test(s).
System check identified no issues (0 silenced).
.....
----------------------------------------------------------------------
Ran 5 tests in 3.2s
OK
```

This will automatically:

* Create a temporary test database.
* Run all unit and integration tests.
* Destroy the test database when finished.

Tests include:

* Task creation
* Task listing
* Permission enforcement (only owner can edit/delete)
* Business rule validation (max 5 active tasks per user)
* Comment creation and retrieval

---

## Generating Fake Data

For testing and demonstration purposes, a management command is provided to generate fake users, tasks, and comments.

Run the command:

```bash
python manage.py load_tasks
```

This will:

* Create multiple demo users.
* Generate random tasks and comments using the **Faker** library.

After running, you can log in using the generated users (passwords are set to `"demo123"` by default).

---

## Usage with Django REST Framework

### Example: Create a Task

```
POST /api/tasks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Finish Django project",
  "description": "Complete remaining endpoints",
  "priority": "high"
}
```

### Example: List Tasks

```
GET /api/tasks/
Authorization: Bearer <token>
```

### Example: Add Comment to a Task

```
POST /api/tasks/1/comments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "content": "This task is almost done."
}
```
