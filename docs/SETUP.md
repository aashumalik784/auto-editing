# Setup Guide

## Prerequisites

1. **Python 3.9+**
```bash
   python --version
```

2. **FFmpeg**
```bash
   # Ubuntu/Debian
   sudo apt-get install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
```

3. **Git**
```bash
   git --version
```

## Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/auto-editing.git
cd auto-editing
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

### 3. Frontend Setup

The frontend is static HTML/CSS/JS, no build step required.

```bash
cd frontend
# Just open index.html in browser or use Live Server
```

### 4. Database Setup (Optional)

If you want to use PostgreSQL:

```bash
# Install PostgreSQL
sudo apt-get install postgresql

# Create database
sudo -u postgres createdb auto_editing

# Run schema
psql -U postgres -d auto_editing -f database/schema.sql

# Run seed data
psql -U postgres -d auto_editing -f database/seed.sql
```

## Configuration

Create a `.env` file in the backend directory:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=True

UPLOAD_DIR=storage/uploads
PROCESSED_DIR=storage/processed
TEMP_DIR=storage/temp
MAX_FILE_SIZE=524288000

WHISPER_MODEL=baseWHISPER_LANGUAGE=en

LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Running the Application

### Backend
```bash
cd backend
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
# Option 1: Open directly
open index.html

# Option 2: Use Python HTTP server
python -m http.server 3000
# Then open http://localhost:3000
```

## Docker Setup (Optional)

```bash
cd backend
docker build -t auto-editing-backend .
docker run -p 8000:8000 -v ./storage:/app/storage auto-editing-backend
```

## Testing

```bash
# Test backend
curl http://localhost:8000/

# Expected response:
# {"status":"healthy","service":"Auto-Editing API","version":"1.0.0"}
```

## Troubleshooting

### FFmpeg not found
```bash
# Check if FFmpeg is installed
ffmpeg -version
# If not installed, install it (see Prerequisites)
```

### Port already in use
```bash
# Change port in .env or command
uvicorn server:app --port 8001
```

### Permission errors
```bash
# Make sure storage directories are writable
chmod -R 755 storage/
```

## Next Steps

1. Configure your backend URL in `frontend/js/api.js`
2. Deploy to production (see DEPLOYMENT.md)
3. Set up database (optional)
4. Configure authentication (optional)
