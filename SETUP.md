# PhishLense Setup Guide

## Quick Start (2-Day Hackathon)

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API Key

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run migrations
python manage.py migrate

# Create superuser (optional, for admin panel)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Backend will run on `http://localhost:8000`

### Step 2: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will run on `http://localhost:3000`

### Step 3: Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/

## API Endpoints

- `GET /api/threats/` - List all threats
- `POST /api/threats/` - Create and analyze new threat
- `GET /api/threats/{id}/` - Get threat details
- `POST /api/threats/{id}/execute/` - Execute threat in sandbox
- `POST /api/threats/{id}/reanalyze/` - Re-analyze threat
- `GET /api/threats/stats/` - Get statistics

## Example API Request

```bash
curl -X POST http://localhost:8000/api/threats/ \
  -H "Content-Type: application/json" \
  -d '{
    "threat_type": "url",
    "content": "https://suspicious-site.com/phishing",
    "source": "unknown",
    "execute_in_sandbox": true
  }'
```

## Features Implemented

✅ Django REST API backend
✅ React TypeScript frontend
✅ OpenAI integration for threat analysis
✅ Sandbox execution (simplified for hackathon)
✅ Security dashboard with visualizations
✅ Threat timeline tracking
✅ Real-time updates

## Notes for Hackathon

- The sandbox environment is simplified for demonstration
- For production, you'd want a more robust sandbox (Docker containers, VMs, etc.)
- OpenAI API key is required - get one from https://platform.openai.com
- The system analyzes threats synchronously - for production, consider async processing with Celery

## Troubleshooting

**Backend won't start:**

- Check if port 8000 is available
- Ensure virtual environment is activated
- Verify all dependencies are installed

**Frontend won't start:**

- Check if port 3000 is available
- Ensure Node.js 16+ is installed
- Try deleting node_modules and running `npm install` again

**OpenAI API errors:**

- Verify your API key is correct in `.env`
- Check your OpenAI account has credits
- Ensure API key has proper permissions

