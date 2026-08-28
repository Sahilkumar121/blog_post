# Blog Post API

An asynchronous RESTful API for a blogging platform, built with **FastAPI** and **SQLAlchemy (async)**. It supports user registration and authentication via **JWT (OAuth2 Password Flow)**, full CRUD on blog posts, per-endpoint rate limiting, and paginated post listings.

## Features

- 🔐 **Authentication** — Register/login with hashed passwords (`pwdlib`) and JWT access tokens (`pyjwt`)
- 📝 **Posts** — Create, read, update, and delete blog posts, scoped to their owning user
- 👤 **User management** — View, update, and delete the authenticated user's account
- 🚦 **Rate limiting** — Request throttling via `slowapi`
- 📄 **Pagination** — Paginated, sorted post listings on the home route
- ⚡ **Fully async** — Async SQLAlchemy engine/session and async route handlers throughout
- ⚙️ **Env-based config** — Settings loaded from `.env` via `pydantic-settings`

## Tech Stack

| Layer          | Technology                          |
|----------------|--------------------------------------|
| Framework      | FastAPI                             |
| ORM            | SQLAlchemy 2.0 (async)               |
| Auth           | OAuth2PasswordBearer + JWT (`pyjwt`) |
| Password hashing | `pwdlib`                          |
| Rate limiting  | `slowapi`                           |
| Config         | `pydantic-settings`                 |
| Server         | Uvicorn (ASGI)                      |

## Project Structure

```
app/
├── api/
│   ├── dependencies.py     # get_db, get_current_user, OAuth2 scheme
│   └── routers/
│       ├── user.py         # /user routes — register, login, me, update, delete
│       └── post.py         # /post routes — get, create, update, delete
├── core/
│   ├── config.py           # Settings (env vars)
│   ├── security.py         # password hashing, JWT create/decode
│   └── rate_limiting.py    # slowapi Limiter
├── db/
│   └── database.py         # async engine, session factory, declarative Base
├── models.py                # Users, Posts ORM models
├── schemas.py                # Pydantic request/response models
└── main.py                   # FastAPI app, lifespan, middleware, home route
```

> Note: `schemas.py` and `routers/__init__.py` (the `api_router` aggregator) are referenced by the code but weren't included in this export — recreate them to match your `PostBase`, `PostResponse`, `UserBase`, `UserResponse`, etc.

## Getting Started

### Prerequisites

- Python 3.11+
- A database supported by your async SQLAlchemy driver (e.g. PostgreSQL with `asyncpg`, or SQLite with `aiosqlite`)

### Installation

```bash
git clone <your-repo-url>
cd <your-repo-name>

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install fastapi uvicorn "sqlalchemy[asyncio]" alembic \
            pydantic-settings pyjwt pwdlib slowapi python-multipart
```

Add the appropriate async DB driver for your database, e.g.:

```bash
pip install asyncpg      # PostgreSQL
# or
pip install aiosqlite    # SQLite
```

### Environment Variables

Create a `.env` file in the project root:

```env
DB_URL=postgresql+asyncpg://user:password@localhost:5432/blogdb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTE=30
```

### Database Setup

If using Alembic for migrations:

```bash
alembic upgrade head
```

Otherwise, tables can be created directly from the `Base` metadata in `database.py`.

### Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

## API Endpoints

### Auth / Users (`/user`)

| Method | Endpoint             | Description                          | Auth Required |
|--------|-----------------------|--------------------------------------|:--------------:|
| POST   | `/user/api/register`  | Register a new user                  | ❌             |
| POST   | `/user/api/login`     | Log in, returns a JWT access token    | ❌             |
| GET    | `/user/me`            | Get the current authenticated user    | ✅             |
| PATCH  | `/user/api/update/`   | Update the current user's account     | ✅             |
| DELETE | `/user/api/delete`    | Delete the current user's account     | ✅             |

### Posts (`/post`)

| Method | Endpoint                    | Description                        | Auth Required |
|--------|------------------------------|-------------------------------------|:--------------:|
| GET    | `/post/api/{post_id}`        | Get a single post by ID              | ❌             |
| POST   | `/post/api/post`             | Create a new post                    | ✅             |
| PATCH  | `/post/api/update/{post_id}` | Update a post (owner only)           | ✅             |
| DELETE | `/post/api/delete/{post_id}` | Delete a post (owner only)           | ✅             |

### Home

| Method | Endpoint | Description                                           |
|--------|----------|--------------------------------------------------------|
| GET    | `/`      | Paginated list of posts (`skip`, `limit` query params) |
| GET    | `/post`  | Same as above                                          |

## Authentication Flow

1. `POST /user/api/register` — create an account with a username, email, and password.
2. `POST /user/api/login` — submit username/password as an OAuth2 password form; receive a JWT `access_token`.
3. Send the token as a Bearer token (`Authorization: Bearer <token>`) on any protected route.
4. `get_current_user` decodes and validates the token on each request, loading the corresponding user from the database.

## Rate Limiting

Requests are throttled using `slowapi`, keyed by client IP, with a default limit of **5 requests per minute** (configurable in `rate_limiting.py`). Exceeding the limit returns an HTTP `429 Too Many Requests`.

## License

Add your preferred license here (e.g. MIT).
