# AI DevOps Agent - Backend

Automated test fixing and deployment agent that clones repositories, runs tests, identifies errors, applies rule-based fixes, and creates pull requests.

## 🏗️ Architecture

```
Client → FastAPI → Docker Runner
                        ↓
                 Clone Repo
                        ↓
                 Install deps
                        ↓
                   Run pytest
                        ↓
                 Parse errors
                        ↓
                   Apply fixes
                        ↓
                 Commit + push
                        ↓
                 Return results.json
```

## 📦 Project Structure

```
backend/
├── app/
│   ├── main.py           # FastAPI application
│   ├── docker_runner.py  # Main orchestrator
│   ├── parser.py         # Error parser
│   ├── fixer.py          # Fix engine
│   ├── git_utils.py      # Git operations
│   ├── models.py         # Data models
│   └── config.py         # Configuration
│
├── docker/
│   ├── Dockerfile.agent       # Agent container
│   └── agent_entrypoint.py    # Agent script
│
├── workspace/            # Cloned repositories
├── results.json          # Execution results
├── requirements.txt      # Python dependencies
├── Dockerfile.api        # API container
└── README.md            # This file
```

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the API server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. **Test the endpoint:**
```bash
curl -X POST "http://localhost:8000/run-agent" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo.git",
    "team": "TeamA",
    "leader": "John",
    "max_retries": 5
  }'
```

### Docker Deployment

1. **Build the Docker image:**
```bash
docker build -t ai-devops-agent -f Dockerfile.api .
```

2. **Run the container:**
```bash
docker run -p 8000:8000 ai-devops-agent
```

## 🔧 How It Works

### 1. Clone Repository
Uses GitPython to clone the target repository into the workspace directory.

### 2. Install Dependencies
Automatically installs dependencies from `requirements.txt` if present.

### 3. Run Tests
Executes `pytest --maxfail=10 -v` and captures output.

### 4. Parse Errors
Identifies errors using regex patterns:
- **LINTING**: Unused imports
- **SYNTAX**: Missing colons, syntax errors
- **INDENTATION**: Tab/space issues
- **IMPORT**: ModuleNotFoundError
- **LOGIC**: NameError (undefined variables)
- **TYPE_ERROR**: Type mismatches

### 5. Apply Fixes
Rule-based fixes for common issues:
- Remove unused imports
- Add missing colons
- Fix indentation (tabs → spaces)
- Comment out missing imports
- Initialize undefined variables
- (Type errors: basic support)

### 6. Commit Changes
Each fix is committed individually with format:
```
[AI-AGENT] Fixed {error_type} error in {file} line {line}
```

### 7. Create Branch
Branch naming format:
```
{TEAM}_{LEADER}_AI_FIX
```
Example: `TEAMA_JOHN_AI_FIX`

### 8. Push & Generate Results
Pushes to new branch and generates `results.json`:
```json
{
  "repo": "https://github.com/user/repo.git",
  "branch": "TEAMA_JOHN_AI_FIX",
  "total_failures": 4,
  "total_fixes": 3,
  "iterations": 2,
  "status": "PARTIAL",
  "fixes": [
    {
      "file": "src/utils.py",
      "line": 15,
      "type": "LINTING",
      "commit_message": "[AI-AGENT] Fixed LINTING error in utils.py line 15",
      "status": "Fixed"
    }
  ]
}
```

## 📡 API Endpoints

### `POST /run-agent`
Run the agent synchronously (waits for completion)

**Request:**
```json
{
  "repo_url": "https://github.com/user/repo.git",
  "team": "TeamA",
  "leader": "John",
  "max_retries": 5
}
```

**Response:**
```json
{
  "repo": "...",
  "branch": "TEAMA_JOHN_AI_FIX",
  "total_failures": 4,
  "total_fixes": 3,
  "iterations": 2,
  "status": "PARTIAL",
  "fixes": [...]
}
```

### `POST /run-agent-async`
Run the agent asynchronously (returns immediately)

### `GET /health`
Health check endpoint

## ⚠️ Limitations

**Current Version (Stage 1):**
- ✅ Python repositories only
- ✅ pytest-based testing only
- ✅ Rule-based fixes (simple cases)
- ❌ Complex logic bugs
- ❌ Multi-language support
- ❌ AI-powered fixes

## 🔒 Security

**Important:** The agent executes arbitrary code from cloned repositories. In production:
- Use Docker containers for isolation
- Implement proper sandboxing
- Restrict network access
- Use separate execution environments

## 📊 Status Codes

- **PASSED**: All errors fixed successfully
- **PARTIAL**: Some errors fixed, some remain
- **FAILED**: No errors could be fixed

## 🛠️ Development

### Running Tests
```bash
pytest
```

### Code Structure
- `main.py`: FastAPI routes and API logic
- `docker_runner.py`: Main orchestration logic
- `parser.py`: Error detection and parsing
- `fixer.py`: Fix application logic
- `git_utils.py`: Git operations (clone, branch, commit, push)
- `models.py`: Pydantic models for request/response
- `config.py`: Configuration constants

## 📝 License

MIT License

## 🤝 Contributing

This is a hackathon project. Contributions welcome!
