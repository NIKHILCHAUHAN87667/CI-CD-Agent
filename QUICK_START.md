# 🚀 AI DevOps Agent - Quick Reference

## ✅ Current Status

### ✅ Backend Running
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

### ✅ Frontend Running
- **URL**: http://localhost:3000
- **Framework**: React + Vite
- **UI**: TailwindCSS

---

## 📋 What You Need to Do Next

### 1. ⚙️ Configure Environment Variables

#### Backend (.env in `/backend/`)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/aidevops
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback
SECRET_KEY=your-secret-key-here
```

#### Frontend (.env in `/frontend/`)
```env
VITE_API_URL=http://localhost:8000
VITE_GITHUB_CLIENT_ID=your_github_client_id
VITE_GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback
```

### 2. 🗄️ Setup PostgreSQL Database

**Option A: Local PostgreSQL**
```bash
# Create database
createdb aidevops

# Or using psql
psql -U postgres
CREATE DATABASE aidevops;
\q
```

**Option B: Docker PostgreSQL**
```bash
docker run --name aidevops-pg \
  -e POSTGRES_DB=aidevops \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:14
```

**Option C: Cloud Database (Easiest)**
- **Render**: https://render.com/ (Free tier)
- **Supabase**: https://supabase.com/ (Free tier)
- Copy the connection string they provide

### 3. 🔐 Setup GitHub OAuth App

1. Go to: https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in:
   - Name: `AI DevOps Agent`
   - Homepage: `http://localhost:3000`
   - Callback: `http://localhost:3000/auth/callback`
4. Click **"Register application"**
5. Copy **Client ID** and generate **Client Secret**
6. Add them to your .env files

---

## 🎯 Testing the Application  

### Step 1: Create .env files
```bash
# Backend
cd backend
cp .env.example .env
# Edit with your values

# Frontend
cd ../frontend
cp .env.example .env
# Edit with your values
```

### Step 2: Restart servers (if needed)
```bash
# Backend (Terminal 1)
cd backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Linux/Mac
python -m uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### Step 3: Test the app
1. Open http://localhost:3000
2. Click "Login with GitHub"
3. Authorize the app
4. You'll be redirected to the dashboard!

---

## 🏗️ Project Structure

```
RFIT_PUNE_HACK122/
│
├── backend/                 ✅ FastAPI + PostgreSQL
│   ├── app/
│   │   ├── main.py         # API endpoints (GitHub OAuth, runs)
│   │   ├── models.py       # Pydantic models
│   │   ├── db_models.py    # Database models
│   │   ├── auth.py         # GitHub OAuth handler
│   │   ├── parser.py       # Error detection
│   │   ├── fixer.py        # Auto-fix engine
│   │   ├── git_utils.py    # Git operations
│   │   └── docker_runner.py # Main orchestrator
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                ✅ React + TailwindCSS
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Pages (Login, Dashboard, etc.)
│   │   ├── services/       # API client
│   │   ├── store/          # Zustand state management
│   │   └── App.jsx
│   ├── package.json
│   └── .env.example
│
├── SETUP_GUIDE.md          📚 Detailed setup instructions
└── README.md               📖 Project overview
```

---

## 🎨 Features Overview

### Backend Features ✅
- ✅ GitHub OAuth authentication
- ✅ PostgreSQL database with SQLAlchemy
- ✅ Run history tracking
- ✅ Error detection (6 types)
- ✅ Automatic fixes
- ✅ Git operations (clone, branch, commit, push)
- ✅ RESTful API with FastAPI

### Frontend Features ✅
- ✅ Modern React with hooks
- ✅ TailwindCSS responsive design
- ✅ GitHub OAuth integration
- ✅ Real-time dashboard
- ✅ Run history with search/filter
- ✅ Detailed results view
- ✅ Mobile-friendly
- ✅ Zustand state management

---

## 📡 API Endpoints

### Authentication
- `POST /auth/github/callback` - Handle OAuth callback
- `GET /auth/me` - Get current user

### Agent Operations
- `POST /run-agent` - Run agent synchronously
- `POST /run-agent-async` - Run in background
- `GET /runs` - Get all runs for user
- `GET /runs/{id}` - Get specific run

### Utility
- `GET /` - Service info
- `GET /health` - Health check

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if PostgreSQL is running
pg_isready

# Check if port 8000 is free
netstat -ano | findstr :8000

# View backend logs in terminal
```

### Frontend won't start
```bash
# Check if port 3000 is free
netstat -ano | findstr :3000

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Database connection error
- Verify PostgreSQL is running
- Check DATABASE_URL in backend/.env
- Test connection: `psql -U user -d aidevops`

### GitHub OAuth not working
- Verify Client ID and Secret in .env files
- Check callback URL matches exactly
- Ensure both servers are running

---

## 🚀 Quick Commands

```bash
# Start backend
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload

# Start frontend  
cd frontend
npm run dev

# Create database
createdb aidevops

# Generate secret key
openssl rand -hex 32

# View API docs
# Open: http://localhost:8000/docs
```

---

## 📚 Documentation

- **Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete detailed setup
- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)

---

## 🎯 Next Steps  

1. ✅ ~~Create .env files~~ (Backend & Frontend)
2. ✅ ~~Setup PostgreSQL database~~
3. ✅ ~~Create GitHub OAuth App~~
4. ❌ Add credentials to .env files
5. ❌ Restart servers
6. ❌ Test login
7. ❌ Run your first agent!

---

## 🎉 You're Almost There!

Just configure the environment variables and you're ready to go!

**Need Help?**  
Check [SETUP_GUIDE.md](SETUP_GUIDE.md) for step-by-step instructions.

---

Built with ❤️ for RIFT PUNE HACK 122 🚀
