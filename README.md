Online Cinema API 🎬
Online Cinema API is a high-performance, asynchronous digital platform built with FastAPI.
It serves as a robust backend engine for a movie streaming and distribution service, allowing users to
browse, rate, and purchase access to video content through a secure and scalable architecture.


🚀 Key Features
Advanced Authentication & RBAC: Secure JWT-based authentication with three distinct permission levels (User, Moderator, Admin).

Financial Integration: Complete checkout flow integrated with Stripe, including webhook handling for secure order fulfillment.

Complex Content Discovery: Optimized filtering and searching through large movie libraries and metadata (actors, genres, etc.).

Asynchronous Background Tasks: Utilizes Celery and Redis for transactional emails and periodic database cleanup.

Social Interactions: Full support for likes/dislikes, comments, and personal "Favorite" collections.


🛠 Tech Stack
Framework: FastAPI (Python 3.12)

Database: PostgreSQL + SQLAlchemy (Async)

Migrations: Alembic

Task Queue: Celery + Redis

Payments: Stripe API

Dependency Management: Poetry

Containerization: Docker & Docker Compose


📂 Project Structure
The project follows a modular architecture designed for maintainability:

├── alembic/          # Database migration history
├── src/
│   ├── core/         # Security, Database config, Celery init
│   ├── crud/         # Decoupled business logic (Create, Read, Update, Delete)
│   ├── models/       # SQLAlchemy models
│   ├── routers/      # API endpoints (Auth, Movies, Stripe, etc.)
│   ├── schemas/      # Pydantic validation models
│   ├── services/     # Third-party integrations (Stripe Service)
│   ├── tasks/        # Celery background tasks (Emails, Cleanups)
│   └── utils/        # Pagination and helpers
├── main.py           # Application entry point
└── seed.py           # Database seeding script


⚙️ Installation & Setup

1. Prerequisites

Docker and Docker Compose
Stripe Account (for API keys)

2. Environment Setup Clone the repository and create a .env file:

cp .env.example .env 
(Fill in your database credentials, Stripe keys, and SMTP settings)

3. Run with Docker 

docker-compose up --build

4. Database Seeding To populate the database with initial movies and metadata: 

docker-compose exec web python seed.py


📖 API Documentation
Once the server is running, you can explore the interactive API documentation:

Swagger UI: http://localhost:8000/docs

ReDoc: http://localhost:8000/redoc


🔒 Permissions Overview
User: Read movies, Post comments, Rate, Buy access, Manage Profile.
Moderator: All User perms + Create/Update/Delete Movies & People.
Admin: All Moderator perms + User Management.
