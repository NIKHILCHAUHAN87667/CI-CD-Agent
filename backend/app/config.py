import os
from dotenv import load_dotenv

load_dotenv()

# Workspace directory for cloned repos
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "workspace")

# Results file
RESULTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results.json")

# Max retries for fixing errors
MAX_RETRIES = 5

# Test command
TEST_COMMAND = ["pytest", "--maxfail=10", "-v"]

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/aidevops")

# GitHub OAuth
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/auth/callback")

# JWT Secret
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# Ensure workspace directory exists
os.makedirs(WORKSPACE_DIR, exist_ok=True)
