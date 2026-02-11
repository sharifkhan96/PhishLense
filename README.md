# PhishLense: AI Security Copilot

A web-based AI security product that acts as a frontline agent for organizations by safely interacting with suspicious external traffic instead of exposing humans to risk.

## Features

- **User Authentication**: Sign up, sign in, and secure access to your organization's security data
- **Traffic Receiver**: Automatically receives and analyzes incoming traffic from external sources
- **Dual Analysis**: 
  - **ML Model**: Trained model for fast classification (normal/malicious)
  - **OpenAI API**: Deep analysis and human-readable explanations
- **Threat Analysis**: Analyzes emails, URLs, text, and links using LLMs and ML models
- **Sandbox Execution**: Automatically executes risky actions in isolated environment
- **Security Dashboard**: Real-time dashboard with traffic statistics and event monitoring
- **Event Details**: Detailed pages showing what happened, when, what the app did, and what to do next
- **Landing Page**: Public-facing page with app information and dashboard preview

## Tech Stack

- **Backend**: Django + Django REST Framework
- **Frontend**: React + TypeScript
- **AI/ML**: OpenAI API for analysis and explanation
- **Sandbox**: Isolated execution environment for safe interaction

## Project Structure

```
imperial-ai-hackathon/
├── backend/          # Django backend
├── frontend/         # React frontend
├── sandbox/          # Sandbox execution environment
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API Key (get one from https://platform.openai.com)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file from example
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

python manage.py migrate
python manage.py runserver
```

Backend runs on `http://localhost:8000`

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

Frontend runs on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/me/` - Get current user
- `POST /api/auth/refresh/` - Refresh access token

### Traffic Events
- `GET /api/traffic/` - List all traffic events (requires auth)
- `POST /api/traffic/receive/` - Receive traffic from external sources (no auth required)
- `GET /api/traffic/{id}/` - Get traffic event details
- `POST /api/traffic/{id}/execute_sandbox/` - Execute event in sandbox
- `GET /api/traffic/stats/` - Get traffic statistics

### Threats (Legacy)
- `GET /api/threats/` - List all threats
- `POST /api/threats/` - Create and analyze new threat
- `GET /api/threats/{id}/` - Get threat details
- `POST /api/threats/{id}/execute/` - Execute threat in sandbox

## Example Usage

### Receive Traffic Event (External Integration):
```bash
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.100",
    "destination_ip": "10.0.0.1",
    "port": 80,
    "payload": "GET /vulnerabilities/sqli/?id=%27+OR+%27x%27%3D%27x",
    "payload_type": "sqli",
    "organization": "my-org"
  }'
```

### Register User:
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user123",
    "email": "user@example.com",
    "password": "securepass123",
    "password2": "securepass123"
  }'
```

## Features

✅ **User Authentication**: JWT-based authentication with sign up and sign in
✅ **Traffic Monitoring**: Receives and analyzes incoming traffic automatically
✅ **ML Model Integration**: Fast classification using trained ML model (ready for your model)
✅ **AI-Powered Analysis**: Uses OpenAI GPT-4 for deep analysis and explanations
✅ **Sandbox Execution**: Safely executes URLs and emails in isolated environment
✅ **Real-time Dashboard**: Visual dashboard with traffic statistics (All/Normal/Malicious)
✅ **Event Details**: Detailed pages showing what happened, when, actions taken, and recommendations
✅ **Landing Page**: Public-facing page with app information
✅ **Security Reports**: Clear, human-readable reports with actionable recommendations

## ML Model Integration

To integrate your trained ML model:

1. Place your trained model file as `backend/ml_model/model.pkl`
2. Update `backend/.env`:
   ```
   ML_MODEL_ENABLED=True
   ML_MODEL_PATH=ml_model/model.pkl
   ```
3. The model should accept features from: source_ip, destination_ip, payload, payload_type, port, date_time
4. See `backend/ml_model/README.md` for details

## Development Notes

This is a hackathon MVP. The sandbox environment is simplified for demonstration purposes. For production, you'd want:
- More robust sandbox (Docker containers, VMs)
- Async processing (Celery + Redis)
- Enhanced security features
- Multi-tenancy improvements

## Routes

- `/` - Landing page (public)
- `/login` - Sign in page
- `/signup` - Sign up page
- `/dashboard` - Main dashboard (requires auth)
- `/eventsHappened/:id` - Event detail page (requires auth)

See `SETUP.md` for detailed setup instructions.


<img width="1805" height="1020" alt="prdouct" src="https://github.com/user-attachments/assets/6041e847-f9af-42ea-bbf6-0b3f459a85f2" />


