# 🎬 Online Cinema API

Backend API for an online cinema platform built with **FastAPI**.  
The project covers user management, movie catalog, shopping cart, orders, and Stripe payments, with background tasks
powered by Celery.

This project is intended as an **educational** and **portfolio** backend showcasing a modular FastAPI architecture.

---

## 🚀 Features

### 👤 Authentication & Users
- Registration with email activation token
- Admin can manually activate accounts
- JWT authentication (access & refresh)
- Refresh tokens stored in database
- Logout revokes refresh token
- Change password & reset via email
- Roles: **User**, **Moderator**, **Admin**

### 🎥 Movies & Interactions
- Browse catalog with pagination
- Filter, sort, and search
- Like / dislike movies
- Comments with email notifications on replies
- Favorites list
- Rate movies (1–10)
- Genres with movie counters
- Browse purchased movies

### 🛒 Shopping Cart
- One cart per user
- Add / remove / clear movies
- Prevent duplicates
- Prevent adding already purchased movies

### 📦 Orders
- Create orders from cart
- Statuses: `pending`, `paid`, `canceled`
- Order history
- Price snapshot per item
- Cancel before payment

### 💳 Payments
- Stripe integration
- Webhook validation
- Payment history
- Refund support
- Email notifications after payment

### ⚙️ Background Tasks
Handled asynchronously with **Celery + Redis**:
- Send activation emails
- Send password reset emails
- Notify about comment replies
- Notify about payment status
- Cleanup of expired tokens
- Cleanup long pending Orders

---

## 🧰 Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Celery + Redis
- Stripe API
- fastapi-mail (SMTP)
- Docker & Docker Compose
- Poetry
- GitHub Actions

---

## 📁 Project Structure

src/
├── core/ # config, db, security, celery, deps
├── crud/ # business logic
├── models/ # SQLAlchemy models
├── routers/ # API endpoints
├── schemas/ # Pydantic schemas
├── services/ # services (payments)
├── tasks/ # Celery tasks
├── utils/ # helpers
└── main.py # FastAPI entrypoint

alembic/ # migrations

makefile
Copy code

---

## ⚙️ Environment Configuration

Create `.env` from the provided `.env.example`:

`env
# --- DATABASE CONFIGURATION ---
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_NAME=cinema_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# --- SECURITY ---
SECRET_KEY=your_secret_random_string_here
JWT_ENCODING_ALGORITHM=HS256

# --- TOKEN EXPIRATION ---
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ACCOUNT_ACTIVATION_HOURS=24
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES=30

# --- CELERY / REDIS ---
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# --- EMAIL CONFIGURATION ---
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_FROM=no-reply@cinema-api.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME="Online Cinema"

# --- INFRASTRUCTURE ---
DOMAIN=http://localhost:8000

# --- STRIPE ---
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret


🐳 Run with Docker
All services are managed via docker-compose.

docker-compose up --build

This starts:

FastAPI app
PostgreSQL
Redis
Celery worker
Celery beat

The web service automatically runs migrations on startup:
alembic upgrade head && uvicorn main:app ...

API will be available at:

http://localhost:8000


Swagger docs:

http://localhost:8000/docs


🗄️ Database Migrations
Migrations are applied automatically when the web container starts.

No manual Alembic commands are required when using Docker.


🔐 Authentication Flow
User registers

Activation token sent via email

User activates account (or admin activates manually)

Login → access & refresh tokens issued

Refresh token used to obtain new access token

Logout → refresh token deleted from DB


👥 Roles
User	Browse, interact, buy movies
Moderator	Manage movies & metadata
Admin	Manage users, roles, activation


🗃️ Database Overview
Main entities:

Users: User, UserProfile, UserGroup

Tokens: ActivationToken, PasswordResetToken, RefreshToken

Movies: Movie, Genre, Star, Director, Certification

Cart: Cart, CartItem

Orders: Order, OrderItem

Payments: Payment, PaymentItem


Key ideas:

One cart per user

Many-to-many relations for movies & metadata

Snapshot prices stored in orders and payments

Tokens persisted and cleaned up by background tasks


🧪 CI/CD
GitHub Actions is used for:

Code quality checks

Linting

Automated validation on push & PR


📖 API Documentation

Interactive API docs:
/docs

Alternative view:
/redoc
