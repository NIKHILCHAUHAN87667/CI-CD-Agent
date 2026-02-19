# 🧪 Test Repository Setup Guide

## Purpose
Create a simple Python repository with **known, fixable errors** to test the AI DevOps Agent **without LLM** integration.

---

## 📁 Test Repository Structure

Create a new GitHub repo called `ai-agent-test-python` with this structure:

```
ai-agent-test-python/
├── .github/
│   └── workflows/
│       └── test.yml          # GitHub Actions CI
├── src/
│   ├── __init__.py
│   ├── calculator.py         # Has syntax error
│   ├── utils.py              # Has import error
│   └── validator.py          # Has logic error
├── tests/
│   ├── __init__.py
│   ├── test_calculator.py
│   ├── test_utils.py
│   └── test_validator.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📝 File Contents with Intentional Errors

### 1. `requirements.txt`
```txt
pytest==7.4.3
pytest-cov==4.1.0
```

### 2. `.gitignore`
```
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
venv/
.venv/
```

### 3. `src/calculator.py` - **SYNTAX ERROR**
```python
def add(a, b):
    return a + b

def subtract(a, b)      # Missing colon - AGENT SHOULD FIX THIS
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### 4. `src/utils.py` - **IMPORT ERROR** 
```python
import os
import sys
from datetime import datetime
# Missing import: from typing import List - AGENT SHOULD ADD THIS

def format_list(items: List[str]) -> str:  # Uses List but not imported
    return ", ".join(items)

def get_timestamp():
    return datetime.now().isoformat()
```

### 5. `src/validator.py` - **INDENTATION ERROR**
```python
def is_valid_email(email: str) -> bool:
    if "@" not in email:
    return False  # Wrong indentation - AGENT SHOULD FIX THIS
    if "." not in email.split("@")[1]:
        return False
    return True

def is_positive(num: int) -> bool:
    return num > 0
```

### 6. `tests/test_calculator.py`
```python
import pytest
from src.calculator import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5

def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6

def test_divide():
    assert divide(10, 2) == 5
    with pytest.raises(ValueError):
        divide(10, 0)
```

### 7. `tests/test_utils.py`
```python
from src.utils import format_list, get_timestamp

def test_format_list():
    assert format_list(["a", "b", "c"]) == "a, b, c"
    assert format_list([]) == ""

def test_get_timestamp():
    result = get_timestamp()
    assert "T" in result  # ISO format includes T
```

### 8. `tests/test_validator.py`
```python
from src.validator import is_valid_email, is_positive

def test_is_valid_email():
    assert is_valid_email("test@example.com") == True
    assert is_valid_email("invalid") == False
    assert is_valid_email("no@domain") == False

def test_is_positive():
    assert is_positive(5) == True
    assert is_positive(-1) == False
    assert is_positive(0) == False
```

### 9. `src/__init__.py` and `tests/__init__.py`
```python
# Empty files - required for Python packages
```

### 10. `README.md`
```markdown
# AI Agent Test Python

Simple Python project for testing AI DevOps Agent fixes.

## Tests
Run tests with:
```bash
pytest -v
```

Expected errors to be fixed by AI:
1. Syntax error in calculator.py (missing colon)
2. Import error in utils.py (missing typing.List)  
3. Indentation error in validator.py

---

## 🎯 Expected Agent Behavior

### Run 1 - Initial Errors
```
❌ Found 3 errors:
  - calculator.py:5 - SYNTAX: Missing colon
  - utils.py:6 - TYPE_ERROR: List not defined
  - validator.py:4 - INDENTATION: Expected indent
```

### Iteration 1 - Fixes Applied
```
✅ Fix 1: Add colon to function definition
✅ Fix 2: Add 'from typing import List' import
✅ Fix 3: Fix indentation of return statement

Branch created: <TEAM>_<LEADER>_AI_FIX
Commits: 3
Status: PASSED
```

---

## 🚀 How to Use

1. **Create the repo** on GitHub with above files
2. **Push to GitHub**
3. **In your UI**: 
   - Select this test repo
   - Team: "TESTTEAM"
   - Leader: "YOURUSERNAME"
   - Max Retries: 3
4. **Watch the agent**:
   - Clone repo
   - Detect Python project
   - Run pytest
   - Parse 3 errors
   - Apply 3 fixes
   - Commit each fix
   - Push branch
   - Return success

---

## 📊 Scoring Expected

- **Base Score**: 100 (for completing)
- **Speed Bonus**: +10 (if < 5 min)
- **Efficiency**: -0 (3 errors / 3 fixes = 100%)
- **Total**: 110 points

---

## 🔄 Test Variations

### Easy Test (1 error):
Only include syntax error in calculator.py

### Medium Test (3 errors):
Use all 3 errors above

### Hard Test (5+ errors):
Add:
- Missing import in validator.py
- Logic error (wrong comparison operator)
- Unused variable warning

---

## ⚡ Quick Setup Script

```bash
# Create repo locally
mkdir ai-agent-test-python
cd ai-agent-test-python
git init

# Create structure
mkdir -p src tests .github/workflows
touch src/__init__.py tests/__init__.py

# Copy files from above
# ... (create each file)

# Push to GitHub
git add .
git commit -m "Initial commit with test errors"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-agent-test-python.git
git push -u origin main
```

---

## ✅ Success Criteria

1. ✅ Agent detects all 3 errors
2. ✅ Agent applies 3 correct fixes
3. ✅ All tests pass after fixes
4. ✅ Branch pushed to GitHub
5. ✅ UI shows results correctly
6. ✅ Can re-run on same repo

---

## 🎓 Next Steps After This Works

1. **Add more error types**:
   - Unused imports
   - Missing docstrings
   - Type annotation errors

2. **Add LLM integration** for:
   - Complex logic errors
   - API usage fixes
   - Refactoring suggestions

3. **Add scoring system**:
   - Track fix accuracy
   - Measure performance
   - Compare runs

4. **Add real-time WebSocket updates**:
   - Show progress live
   - Stream test output
   - Display git operations
