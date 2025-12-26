Online Cinema API 🎬
An asynchronous, high-concurrency backend engine for digital content distribution.
This system handles complex relational metadata, multi-tiered access control, and atomic financial transactions
through a decoupled, event-driven architecture.


🏗 Project Architecture & Structure
The codebase is organized into a modular hierarchy to maintain strict separation between
the transport layer, business logic, and background processing.

├── alembic/                # Schema versioning and migration history
├── src/
│   ├── core/               # System Kernel: Security, Async Engine, Global Config
│   ├── crud/               # Domain Engine: Complex SQLAlchemy query builders
│   ├── models/             # Data Layer: Async models with M2M associations
│   ├── routers/            # Interface Layer: API endpoints and RBAC dependencies
│   ├── schemas/            # Validation Layer: Pydantic V2 serialization shapes
│   ├── services/           # Integration Layer: Stripe SDK
│   ├── tasks/              # Event Layer: Celery tasks (SMTP & Maintenance)
│   └── utils/              # Shared Utilities: Pagination and async helpers
├── main.py                 # Application entry point and router orchestration
├── seed.py                 # Idempotent database seeding utility
└── docker-compose.yml      # Service orchestration (App, Worker, Beat, Redis, DB)


⚙️ Core System Setup
These commands are specific to the initialization and state management of the online-cinema-api environment.

1. Environment Initialization
The system validates the .env configuration on startup via Pydantic Settings. 

    cp .env.example .env 

2. Dependency Management (Poetry)

    poetry install
    poetry shell

3. Database State Management
To synchronize the PostgreSQL container with the current SQLAlchemy models:

    docker-compose exec app alembic upgrade head

    docker-compose exec app python seed.py


🔐 Identity & Access Management
Access is managed through a hierarchical dependency chain in src/core/deps.py that validates
JWT claims and UserGroup membership.

Standard Access: get_current_active_user validates the sub claim and is_active status.

Privileged Access:

Moderator: Grants CRUD access to movie, people, and metadata routers.

Admin: High-level access for user role elevation and financial auditing.

Security Architecture: Implements Refresh Token Rotation to mitigate session hijacking and
Argon2 hashing for credential entropy.


🎞 Discovery Engine: Deep Relational Filtering
The search logic in src/crud/movie.py is designed for high-dimensional metadata discovery.

Query Optimization: Implements joinedload for one-to-one (Certification) and selectinload for
many-to-many (Genres, Stars) to eliminate the N+1 problem.

Unified Search: A single search parameter executes a case-insensitive scan across
Movie Titles, Descriptions, Stars, and Directors using optimized outer joins.

Filtering Parameters: Support for temporal (Year), physical (Runtime), and financial (Price) ranges, alongside
IMDb and Meta Score thresholds.


💳 Financial Engine & Fulfillment
The Stripe integration is built as a non-blocking, event-driven pipeline.

Checkout Session: Generates a secure, Stripe-hosted checkout linked to a PENDING order.

Cryptographic Webhook: The /webhook endpoint in src/routers/payment.py verifies the Stripe-Signature.

Atomic Fulfillment: On success, the payment_service.py executes an atomic transaction that:

Transitions Order status to PAID or CANCELED.

Maps the User to the Movie in the user_movies association table.

Dispatches an asynchronous send_payment_notification_email_task.


📧 Automated Lifecycle (Celery & Beat)
Background operations are offloaded to Celery with Redis as the message broker.

Transactional Tasks: SMTP operations for account activation, password resets, and purchase receipts.

Scheduled Maintenance (Beat):

cleanup_expired_tokens: Periodic purging of the activation_tokens table.

cancel_pending_orders: Automatic cancellation of PENDING orders older than 24 hours to ensure accurate financial reporting.


📖 API Reference & Inspection
Interactive Documentation (Swagger): http://localhost:8000/docs

Static Technical Docs (ReDoc): http://localhost:8000/redoc
