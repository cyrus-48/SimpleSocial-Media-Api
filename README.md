# Social Media API

A modern social media REST API built with FastAPI, SQLAlchemy, and Alembic. This API provides features similar to popular social media platforms including user authentication, posts, comments, likes, and follower relationships.

## Features

### User Management
- User registration and authentication
- JWT token-based authentication
- User profile management
- Profile picture upload

### Posts
- Create, read, update, and delete posts
- Image attachments support
- Pagination support
- Feed generation based on followed users

### Social Features
- Follow/unfollow users
- Like/unlike posts
- Comment on posts
- User activity feed

## Technology Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation using Python type annotations
- **Python-Jose**: JWT token handling
- **Passlib**: Password hashing
- **Pillow**: Image processing
- **SQLite**: Database (can be easily switched to PostgreSQL)


## Setup and Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd social_media_api

2. Create and activate Virtual Environment
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    # or
    .\venv\Scripts\activate  # Windows

3. Install Deps

    ```bash
    pip install -r requirements.txt



### Main Endpoints

# Authentication
- **POST /api/v1/auth/register:** Register new user

- **POST /api/v1/auth/login:** Login and get access token

- **POST /api/v1/auth/test-token:** Test authentication

# Users
- **GET /api/v1/users/me:** Get current user

- **PUT /api/v1/users/me:** Update current user

- **POST /api/v1/users/me/profile-picture:** Upload profile picture

- **GET /api/v1/users/{username}:** Get user by username

- **POST /api/v1/users/{username}/follow:** Follow user

- **DELETE /api/v1/users/{username}/unfollow:** Unfollow user

# Posts
- **POST /api/v1/posts/:** Create new post

- **GET /api/v1/posts/:** List all posts

- **GET /api/v1/posts/feed:** Get posts from followed users

- **GET /api/v1/posts/{id}:** Get specific post

- **PUT /api/v1/posts/{id}:** Update post

- **DELETE /api/v1/posts/{id}:** Delete post

- **POST /api/v1/posts/{id}/like:** Like post

- **DELETE /api/v1/posts/{id}/unlike:** Unlike post

- **POST /api/v1/posts/{id}/comments:** Add comment

- **GET /api/v1/posts/{id}/comments:** Get post comments




