# RIFT: Rebel AI Fixer for Tests

RIFT is an AI-powered agent designed to automatically find and fix errors in Python test repositories. It intelligently analyzes `pytest` output, identifies failures, and applies targeted, rule-based fixes to your code.

## ✨ Features

- **Automated Error Detection**: Runs `pytest` in a sandboxed environment to identify test failures.
- **Intelligent Error Parsing**: Parses complex `pytest` output to pinpoint the exact error type and location.
- **Rule-Based Fixes**: Applies deterministic fixes for common Python errors:
  - `SyntaxError`: Adds missing colons.
  - `IndentationError`: Corrects improper indentation.
  - `TypeError`: Adds missing `from typing import ...` statements.
- **Real-Time Progress**: A sleek web interface provides live updates on the agent's activities via WebSockets.
- **Version Control Integration**: Automatically creates a new branch, commits each fix, and pushes to your GitHub repository.
- **Secure & Isolated**: Uses Docker to run tests in an isolated environment, preventing interference with your local setup.

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.11, Uvicorn, SQLAlchemy
- **Frontend**: React, Vite, TailwindCSS, Zustand
- **Real-time**: WebSockets
- **Database**: PostgreSQL (Neon)
- **VCS**: GitPython
- **Containerization**: Docker

## 🚀 Getting Started

Follow these steps to set up and run the RIFT agent locally.

### 1. Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/en/download)
- [Docker](https://www.docker.com/products/docker-desktop/)
- A GitHub account

### 2. GitHub OAuth Application

Before you begin, you need to create a GitHub OAuth application to handle authentication.

1.  Go to [GitHub Developer Settings](https://github.com/settings/developers).
2.  Click **"New OAuth App"**.
3.  Fill in the details:
    - **Application name**: `RIFT Agent` (or any name you prefer)
    - **Homepage URL**: `http://localhost:3001`
    - **Authorization callback URL**: `http://localhost:3001/auth/callback`
4.  Click **"Register application"**.
5.  On the next page, generate a **new client secret**. Copy the **Client ID** and the **Client Secret**. You will need them soon.

### 3. Backend Setup

The backend server runs on **port 8000**.

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    - Rename `.env.example` to `.env`.
    - Open the new `.env` file and fill in the values:
      - `DATABASE_URL`: Your PostgreSQL connection string (e.g., from Neon).
      - `GITHUB_CLIENT_ID`: The Client ID from your GitHub OAuth App.
      - `GITHUB_CLIENT_SECRET`: The Client Secret from your GitHub OAuth App.
      - `JWT_SECRET`: A long, random string for signing tokens.

5.  **Run database migrations:**
    ```bash
    alembic upgrade head
    ```

6.  **Start the backend server:**
    ```bash
    # IMPORTANT: Use --reload-dir app to prevent workspace changes from restarting the server
    python -m uvicorn app.main:app --reload --port 8000 --reload-dir app
    ```
    The backend is now running at `http://localhost:8000`.

### 4. Frontend Setup

The frontend development server runs on **port 3001**.

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure environment variables:**
    - Rename `.env.example` to `.env`.
    - Open the new `.env` file and fill in the `VITE_GITHUB_CLIENT_ID` with the Client ID from your GitHub OAuth App.

4.  **Start the frontend server:**
    ```bash
    npm run dev -- --port 3001
    ```
    The frontend is now running at `http://localhost:3001`.

## ⚙️ How to Use

1.  Open your browser and navigate to `http://localhost:3001`.
2.  Click **"Login with GitHub"** and authorize the application.
3.  You will be redirected to the main page. Paste the URL of a public GitHub repository containing Python tests you want to fix.
4.  Click **"Run Agent"**.
5.  Watch the real-time progress as the agent clones the repo, runs tests, and fixes errors.
6.  Once the run is complete, you will be redirected to the results page, which shows a summary of the fixes and a link to the new branch on GitHub.

## 📄 Capabilities

For a detailed breakdown of what errors the agent can currently resolve and what is planned for the future, please see the [CAPABILITIES.md](CAPABILITIES.md) file.
