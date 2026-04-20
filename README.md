# Robotaxi Passenger Feedback Management Platform

A full-stack web application for managing Robotaxi passenger feedback, including AI-powered analysis, ticket management, and operational dashboards.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React_19-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![Ant Design](https://img.shields.io/badge/Ant_Design_5-0170FE?style=flat&logo=antdesign&logoColor=white)

## Features

- **Feedback Management** — Browse, filter, and export passenger feedback with full pagination and search
- **Ticket System** — Create, assign, and track tickets with SLA monitoring and priority management
- **Data Dashboard** — Interactive charts (ECharts) showing trends, distributions, and key metrics
- **AI Analysis** — LLM-powered feedback analysis with categorization, theme extraction, and actionable suggestions
- **AI Report Generation** — Automated daily/weekly/monthly operational reports based on dashboard data
- **Role-Based Access Control** — 4 roles (admin, supervisor, operator, analyst) with granular permissions
- **JWT Authentication** — Secure login with token-based auth

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.11+** | Runtime |
| **FastAPI** | Web framework |
| **SQLAlchemy 2.0** | Async ORM |
| **SQLite + aiosqlite** | Database (async) |
| **Alembic** | Database migrations |
| **Pydantic v2** | Data validation & settings |
| **python-jose** | JWT authentication |
| **passlib + bcrypt** | Password hashing |
| **OpenAI SDK** | LLM integration (OpenAI-compatible) |
| **httpx** | HTTP client |
| **openpyxl** | Excel export |

### Frontend
| Technology | Purpose |
|---|---|
| **React 19** | UI framework |
| **TypeScript 6** | Type safety |
| **Vite 8** | Build tool & dev server |
| **Ant Design 5** | UI component library |
| **ECharts 6** | Data visualization |
| **Axios** | HTTP client |
| **React Router 7** | Client-side routing |
| **Day.js** | Date handling |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── api/                  # Route handlers
│   │   │   ├── auth_routes.py
│   │   │   ├── feedback_routes.py
│   │   │   └── dashboard_routes.py
│   │   ├── core/                 # Config, auth, database
│   │   ├── models/               # SQLAlchemy models
│   │   ├── schemas/              # Pydantic schemas
│   │   └── services/             # Business logic & AI
│   ├── migrations/               # Alembic migrations
│   ├── scripts/                  # Seed data (JSON)
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/                  # API client & types
│   │   ├── pages/                # Page components
│   │   │   ├── dashboard/
│   │   │   ├── feedback/
│   │   │   ├── tickets/
│   │   │   └── login/
│   │   ├── layouts/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
├── build.sh                      # Production build script
├── render.yaml                   # Render deployment config
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- npm

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd comate-zulu-demo
```

### 2. Backend setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env and fill in your OPENAI_API_KEY and SECRET_KEY

# Run database migrations (creates SQLite DB + seed data)
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend setup
```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

### 4. Access the application
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Default Login Credentials

| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin |
| supervisor01 | pass123 | Supervisor |
| op01 | pass123 | Operator |
| analyst01 | pass123 | Analyst |

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing key | `dev-secret-key-change-in-production` |
| `OPENAI_API_KEY` | OpenAI API key (required for AI features) | — |
| `OPENAI_BASE_URL` | OpenAI-compatible API base URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | LLM model name | `gpt-4o-mini` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite+aiosqlite:///./robotaxi.db` |
| `DEBUG` | Enable debug mode | `true` |

## Deployment (Render)

This project includes a `render.yaml` blueprint for one-click deployment to [Render](https://render.com):

1. Push this repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**
3. Connect your GitHub repo and select this project
4. Render will auto-detect `render.yaml` and configure the service
5. Set the `OPENAI_API_KEY` environment variable in the Render dashboard
6. Deploy!

The build script (`build.sh`) automatically:
- Installs Python dependencies
- Runs database migrations
- Builds the frontend
- The FastAPI server serves both the API and the built frontend static files

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/auth/login` | Login |
| `GET` | `/api/auth/me` | Current user info |
| `GET` | `/api/feedbacks` | List feedbacks (paginated + filtered) |
| `GET` | `/api/feedbacks/{id}` | Feedback detail |
| `GET` | `/api/feedbacks/ids` | All feedback IDs matching filters |
| `GET` | `/api/feedbacks/export` | Export feedbacks as Excel |
| `POST` | `/api/feedbacks/ai-analyze` | AI feedback analysis |
| `GET` | `/api/tickets` | List tickets |
| `POST` | `/api/tickets` | Create ticket |
| `PUT` | `/api/tickets/{id}` | Update ticket |
| `POST` | `/api/tickets/batch-create` | Batch create tickets |
| `POST` | `/api/tickets/batch-assign` | Batch assign tickets |
| `GET` | `/api/dashboard/overview` | Dashboard overview metrics |
| `GET` | `/api/dashboard/trends` | Trend data |
| `GET` | `/api/dashboard/distribution` | Distribution data |
| `GET` | `/api/dashboard/ticket-metrics` | Ticket processing metrics |
| `GET` | `/api/dashboard/route-trends` | Route trend data |
| `POST` | `/api/dashboard/ai-report` | AI-generated operational report |

## License

MIT
