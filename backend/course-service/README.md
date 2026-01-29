# E-Learning Platform Backend API

A FastAPI-based backend service for an e-learning platform with PostgreSQL database and MinIO object storage.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **PostgreSQL Database**: Robust relational database for data persistence
- **MinIO Object Storage**: S3-compatible object storage for course materials, videos, and attachments
- **SQLAlchemy ORM**: SQL toolkit and Object-Relational Mapping
- **Pydantic Models**: Data validation using Python type annotations
- **Docker Support**: Containerized deployment with Docker Compose

## Project Structure

```
elearning-platform/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── users.py          # User endpoints
│   │   │   └── courses.py        # Course endpoints
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py             # Configuration settings
│   │   └── __init__.py
│   ├── db/
│   │   ├── session.py            # Database session setup
│   │   └── __init__.py
│   ├── models/
│   │   ├── models.py             # SQLAlchemy models
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── schemas.py            # Pydantic schemas
│   │   └── __init__.py
│   ├── services/
│   │   ├── user_service.py       # User business logic
│   │   ├── course_service.py     # Course business logic
│   │   └── __init__.py
│   ├── storage/
│   │   ├── minio.py              # MinIO client setup
│   │   └── __init__.py
│   ├── main.py                   # FastAPI application entry point
│   └── __init__.py
├── migrations/                   # Alembic database migrations (future)
├── tests/                        # Test files (future)
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker image configuration
├── docker-compose.yml            # Docker Compose services
└── README.md                     # This file
```

## Data Models

### User
- username (unique)
- email (unique)
- password (hashed)
- full_name
- is_active
- is_superuser
- created_at, updated_at

### Course
- title
- description
- instructor_id (foreign key to User)
- thumbnail_url
- is_published
- created_at, updated_at

### Module
- course_id (foreign key to Course)
- title
- description
- order
- created_at, updated_at

### Lesson
- module_id (foreign key to Module)
- title
- content
- video_url
- attachment_url
- order
- created_at, updated_at

### Enrollment
- user_id (foreign key to User)
- course_id (foreign key to Course)
- enrolled_at
- progress (percentage)

## Setup Instructions

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for containerized setup)
- PostgreSQL 16+ (if running without Docker)
- MinIO (if running without Docker)

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd elearning-platform

# Copy environment file
cp .env.example .env

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup (without Docker)

```bash
# Create PostgreSQL database
createdb elearning_db

# Run migrations (when using Alembic)
alembic upgrade head
```

### 3. Running the Application

#### Option A: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- MinIO Console: `http://localhost:9001` (Username: minioadmin, Password: minioadmin)

#### Option B: Local Development

```bash
# Ensure PostgreSQL and MinIO are running

# Update .env with local credentials
# DATABASE_URL=postgresql://user:password@localhost:5432/elearning_db
# MINIO_URL=http://localhost:9000

# Run the server
uvicorn app.main:app --reload

# Or use Python
python -m app.main
```

## API Endpoints

### Users
- `POST /users/register` - Register a new user
- `GET /users/{user_id}` - Get user by ID

### Courses
- `POST /courses/` - Create a new course
- `GET /courses/` - List all courses
- `GET /courses/{course_id}` - Get course by ID
- `PUT /courses/{course_id}` - Update a course
- `DELETE /courses/{course_id}` - Delete a course

### Health Check
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint

## Environment Variables

Create a `.env` file in the project root based on `.env.example`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/elearning_db
MINIO_URL=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=elearning
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
```

## Development

### Running Tests

```bash
pytest tests/

# With coverage
pytest --cov=app tests/
```

### Code Style

```bash
# Format code with black
black app/

# Lint with flake8
flake8 app/

# Type checking with mypy
mypy app/
```

## Database Migrations

Using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Revert to previous revision
alembic downgrade -1
```

## MinIO Integration

The application includes MinIO client for object storage operations:

```python
from app.storage import minio_client

# Upload file
url = minio_client.upload_file(file_path, object_name, content_type)

# Upload bytes
url = minio_client.upload_bytes(data, object_name, content_type)

# Download file
minio_client.download_file(object_name, file_path)

# Delete file
minio_client.delete_file(object_name)

# List files
files = minio_client.list_files(prefix)
```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is running on the correct host and port
- Check DATABASE_URL in .env file
- Verify database credentials

### MinIO Connection Issues
- Ensure MinIO is running and accessible
- Check MINIO_URL, MINIO_ACCESS_KEY, and MINIO_SECRET_KEY
- Verify MinIO bucket exists

### Port Conflicts
- Change PORT in .env if 8000 is in use
- Change container ports in docker-compose.yml if needed

## Future Enhancements

- [ ] User authentication (JWT tokens)
- [ ] Role-based access control (RBAC)
- [ ] Course enrollment management
- [ ] Student progress tracking
- [ ] Video streaming optimization
- [ ] Caching with Redis
- [ ] WebSocket support for real-time notifications
- [ ] Comprehensive test suite
- [ ] API versioning
- [ ] GraphQL support

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or contributions, please open an issue on the project repository.
