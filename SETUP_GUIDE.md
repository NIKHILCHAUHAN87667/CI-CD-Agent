# 🚀 AI DevOps Agent - Complete Setup Guide

## 📋 Prerequisites

Before you begin, make sure you have:
- Python 3.10+ installed
- Node.js 18+ and npm installed
- PostgreSQL 14+ installed and running
- Git installed
- GitHub account

---

## 🔧 Part 1: GitHub OAuth Setup

### Step 1: Create GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click **"New OAuth App"**
3. Fill in the details:
   - **Application name**: AI DevOps Agent
   - **Homepage URL**: `http://localhost:3000`
   - **Authorization callback URL**: `http://localhost:3000/auth/callback`
4. Click **"Register application"**
5. You'll get a **Client ID** - copy this
6. Click **"Generate a new client secret"** - copy this too

⚠️ **Keep these credentials safe! You'll need them for configuration.**

---

## 🗄️ Part 2: Database Setup

### Option 1: Local PostgreSQL

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE aidevops;

# Create user (optional)
CREATE USER aidevops_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE aidevops TO aidevops_user;

# Exit
\q
```

### Option 2: Use Docker PostgreSQL

```bash
docker run --name aidevops-postgres \
  -e POSTGRES_DB=aidevops \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:14
```

### Option 3: Cloud Database (Recommended for Production)

- **Render**: https://render.com/ (Free tier available)
- **Supabase**: https://supabase.com/ (Free tier available)
- **Railway**: https://railway.app/ (Free tier available)

After creating your database, you'll get a connection string like:
```
postgresql://user:password@host:port/database
```

---

## 🔨 Part 3: Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create `.env` file in the backend directory:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aidevops

# GitHub OAuth (from Step 1)
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback

# Security (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-change-in-production
```

### 5. Test database connection
```bash
python
>>> from app.database import engine
>>> engine.connect()
# Should connect without errors
```

### 6. Start the backend server
```bash
# Make sure virtual environment is activated!
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend should now be running at: **http://localhost:8000**

---

## 💻 Part 4: Frontend Setup

### 1. Navigate to frontend directory
```bash
cd../frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment variables

Create `.env` file in the frontend directory:
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
VITE_API_URL=http://localhost:8000
VITE_GITHUB_CLIENT_ID=your_github_client_id_here
VITE_GITHUB_REDIRECT_URI=http://localhost:3000/auth/callback
```

### 4. Start the frontend development server
```bash
npm run dev
```

Frontend should now be running at: **http://localhost:3000**

---

## ✅ Part 5: Verify Installation

### 1. Check Backend
- Open: http://localhost:8000/health
- Should see: `{"status":"healthy"}`
- API Docs: http://localhost:8000/docs

### 2. Check Frontend
- Open: http://localhost:3000
- Should see the AI DevOps Agent homepage
- Click "Login with GitHub"

### 3. Test Authentication Flow
1. Click "Login with GitHub" on frontend
2. Authorize the application on GitHub
3. You should be redirected back and logged in
4. Check your username in the header

---

## 🐳 Part 6: Docker Deployment (Optional)

### Backend
```bash
cd backend
docker build -t ai-devops-backend -f Dockerfile.api .
docker run -p 8000:8000 \
  -e DATABASE_URL=your_database_url \
  -e GITHUB_CLIENT_ID=your_client_id \
  -e GITHUB_CLIENT_SECRET=your_client_secret \
  -e SECRET_KEY=your_secret_key \
  ai-devops-backend
```

### Full Stack with Docker Compose
```bash
docker-compose up --build
```

---

## 🚀 Part 7: Production Deployment

### Backend (Render/Railway/Fly.io)

1. **Push code to GitHub**
2. **Connect repository to platform**
3. **Set environment variables**:
   - DATABASE_URL
   - GITHUB_CLIENT_ID
   - GITHUB_CLIENT_SECRET
   - SECRET_KEY
4. **Deploy!**

### Frontend (Vercel - Recommended)

1. **Push code to GitHub**
2. **Import project on Vercel**: https://vercel.com/new
3. **Set Root Directory**: `frontend`
4. **Set environment variables**:
   - VITE_API_URL (your backend URL)
   - VITE_GITHUB_CLIENT_ID
   - VITE_GITHUB_REDIRECT_URI (your frontend URL + /auth/callback)
5. **Deploy!**

### Update GitHub OAuth URLs
After deployment, update your GitHub OAuth App:
- Homepage URL: Your frontend URL
- Callback URL: Your frontend URL + `/auth/callback`

---

## 🧪 Part 8: Test the Agent

1. **Login to the application**
2. **Go to "Run Agent"**
3. **Enter test repository**:
   ```
   Repo URL: https://github.com/your-username/test-repo.git
   Team: TeamAlpha
   Leader: YourName
   Max Retries: 5
   ```
4. **Click "Run Agent"**
5. **View Results**

---

## 🔧 Troubleshooting

### Backend won't start
- Check if PostgreSQL is running: `pg_isready`
- Verify DATABASE_URL in `.env`
- Check if port 8000 is available: `netstat -ano | findstr :8000`

### Frontend won't start
- Delete `node_modules` and run `npm install` again
- Check if port 3000 is available
- Verify .env variables

### GitHub OAuth not working
- Verify Client ID and Secret
- Check Redirect URI matches exactly
- Make sure both frontend and backend are running

### Database connection errors
- Check PostgreSQL is running
- Verify connection string format
- Check firewall/network settings

---

## 📚 Useful Commands

```bash
# Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Database
psql -U postgres -d aidevops

# Generate secret key
openssl rand -hex 32

# View logs
tail -f backend/logs/app.log
```

---

## 🎯 Quick Start (After Setup)

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Then open http://localhost:3000 in your browser!

---

## 📞 Need Help?

- Check the [README.md](README.md) for project overview
- Review API docs at http://localhost:8000/docs
- Check backend logs for errors

---

## 🎉 You're All Set!

Your AI DevOps Agent is now ready to automatically fix code errors!

**Next Steps**:
1. Try running the agent on a test repository
2. Review the results and fixes
3. Customize error detection rules
4. Deploy to production

Happy Coding! 🚀
