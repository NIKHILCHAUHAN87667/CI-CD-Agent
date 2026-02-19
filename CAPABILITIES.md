# AI DevOps Agent - Capabilities & Error Types

## 📋 Table of Contents
- [Current Implementation Status](#current-implementation-status)
- [Error Types We Can Fix (Rule-Based)](#error-types-we-can-fix-rule-based)
- [Error Types That Need LLM](#error-types-that-need-llm)
- [Error Types We Cannot Fix](#error-types-we-cannot-fix)
- [How The Agent Works](#how-the-agent-works)
- [Future Roadmap](#future-roadmap)

---

## 🎯 Current Implementation Status

### ✅ Fully Implemented (No LLM Required)

#### 1. **SYNTAX Errors**
**What it fixes:**
- Missing colons after function/class definitions
- Missing colons after if/for/while/elif statements

**How it works:**
```python
# Before (ERROR: SyntaxError)
def subtract(a, b)      # Missing colon
    return a - b

# After (FIXED)
def subtract(a, b):     # Colon added
    return a - b
```

**Real Example from Test Run:**
```
Iteration 1: Found SyntaxError in calculator.py:4
✓ Added colon: 'def subtract(a, b) # Missing colon' -> 'def subtract(a, b):'
Committed: [AI-AGENT] Fixed SYNTAX error in calculator.py line 4
```

**Limitations:**
- Only handles missing colons
- Cannot fix complex syntax errors (parentheses mismatch, invalid operators)

---

#### 2. **INDENTATION Errors**
**What it fixes:**
- Wrong indentation levels (too many/few spaces)
- Inconsistent indentation within blocks
- Tab/space mixing

**How it works:**
```python
# Before (ERROR: IndentationError)
def is_valid_email(email: str) -> bool:
    if "@" not in email:
    return False  # Wrong indentation (4 spaces, should be 8)

# After (FIXED)
def is_valid_email(email: str) -> bool:
    if "@" not in email:
        return False  # Corrected to 8 spaces (inside if block)
```

**Context-Aware Logic:**
- Looks at previous line
- If previous line ends with `:`, adds +4 indentation
- Converts tabs to 4 spaces

**Real Example:**
```
Found IndentationError in validator.py:3
✓ Fixed indentation: 4 -> 8 spaces
Committed: [AI-AGENT] Fixed INDENTATION error in validator.py line 3
```

---

#### 3. **TYPE_ERROR (Missing Typing Imports)**
**What it fixes:**
- `NameError: name 'List' is not defined`
- `NameError: name 'Dict' is not defined`
- `NameError: name 'Optional' is not defined`
- Other typing module imports (Set, Tuple, Union, Any, Callable)

**How it works:**
```python
# Before (ERROR: NameError)
def format_list(items: List[str]) -> str:  # List not imported
    return ", ".join(items)

# After (FIXED)
from typing import List  # Import added at top

def format_list(items: List[str]) -> str:
    return ", ".join(items)
```

**Smart Import Handling:**
- Checks if `from typing import` already exists
- Appends to existing import: `from typing import Dict, List`
- Or creates new import at top of file

**Detection Pattern:**
```python
ErrorType.TYPE_ERROR: [
    r"name '(List|Dict|Set|Tuple|Optional|Union|Any|Callable)' is not defined"
]
```

---

#### 4. **IMPORT Errors (Partial)**
**What it can fix:**
- Comment out missing/broken imports
- Remove imports that cause ModuleNotFoundError

**How it works:**
```python
# Before (ERROR: ModuleNotFoundError)
import nonexistent_module
from missing_package import something

# After (FIXED)
# import nonexistent_module  # Commented by AI-AGENT
# from missing_package import something
```

**Limitations:**
- Doesn't install missing packages
- Just comments out problematic imports
- Cannot fix circular imports

---

#### 5. **LINTING Issues (Basic)**
**What it fixes:**
- Unused imports (removes them)
- Imported but unused variables

**Example:**
```python
# Before
import os  # unused
import sys  # used
sys.exit(0)

# After
import sys  # unused import removed
sys.exit(0)
```

---

#### 6. **LOGIC Errors (Very Basic)**
**What it can fix:**
- Undefined variable initialization (adds placeholder)

**Example:**
```python
# Before (ERROR: NameError)
print(undefined_var)

# After (FIXED - but likely wrong logic)
undefined_var = None  # AI-AGENT: Auto-initialized
print(undefined_var)
```

**⚠️ Warning:** This is a BAD fix! It prevents the error but doesn't solve the logic.
**This is where LLM is needed** to understand what the variable should actually be.

---

## ❌ Error Types That NEED LLM

### 1. **Complex Logic Errors**
**Examples:**
```python
# Wrong algorithm
def calculate_average(numbers):
    return sum(numbers)  # Missing division by len(numbers)

# Off-by-one errors
for i in range(len(items) - 1):  # Should be range(len(items))
    process(items[i])

# Wrong comparison
if age > 18:  # Should be >= 18 for voting
    can_vote = True
```

**Why LLM is needed:**
- Requires understanding business logic
- Multiple valid fixes possible
- Context from entire codebase needed

---

### 2. **Semantic Errors**
**Examples:**
```python
# Wrong variable used
def calculate_total(price, quantity):
    return price * price  # Should be price * quantity

# Wrong function called
user.save()  # Should be user.delete()

# Type mismatch
result = "5" + 10  # Should convert string to int first
```

**Why LLM is needed:**
- Requires understanding programmer intent
- Static rules cannot determine "correct" behavior

---

### 3. **API/Library Usage Errors**
**Examples:**
```python
# Deprecated API
requests.get(url, verify=True)  # Old way
# Should use: httpx.get(url)

# Wrong parameters
pd.read_csv('file.csv', header=False)  # Missing required param
# Might need: pd.read_csv('file.csv', header=0, encoding='utf-8')
```

**Why LLM is needed:**
- Requires knowledge of library documentation
- Version-specific fixes
- Understanding developer's goal

---

### 4. **Test Failures (Assertion Errors)**
**Example:**
```python
def test_add():
    assert add(2, 3) == 6  # Expected 5, got 6
    # Is the test wrong or the function wrong?
```

**Why LLM is needed:**
- Cannot determine if test or implementation is incorrect
- Requires understanding requirements
- May need to modify test OR code

---

### 5. **Missing Functionality**
**Example:**
```python
# Test expects function that doesn't exist
def test_user_email_validation():
    assert validate_email("test@example.com") == True
    # ERROR: validate_email() doesn't exist!
```

**Why LLM is needed:**
- Need to GENERATE new code
- Understand requirements from test
- Implement logic from scratch

---

### 6. **Performance Issues**
**Example:**
```python
# Works but times out
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)  # Extremely slow
    # Needs memoization or iterative approach
```

**Why LLM is needed:**
- Requires algorithmic knowledge
- Multiple optimization strategies
- Understanding performance requirements

---

## 🚫 Error Types We Cannot Fix (Even with LLM)

### 1. **Environment/System Issues**
```bash
# Cannot fix:
- Missing Python version
- Operating system incompatibilities  
- Filesystem permissions
- Network connectivity
```

### 2. **External Dependencies**
```bash
# Cannot fix:
- Database down
- API rate limits
- Third-party service outages
- Hardware failures
```

### 3. **Configuration Errors**
```bash
# Cannot fix:
- Missing .env files
- Invalid database credentials
- Firewall blocking ports
- DNS resolution issues
```

### 4. **Binary/Compiled Code Issues**
```bash
# Cannot fix:
- Segmentation faults in C extensions
- Memory corruption
- CPU architecture mismatches
```

---

## 🔄 How The Agent Works

### Execution Flow
```
1. Clone Repository
   ↓
2. Install Dependencies (pip install / npm install)
   ↓
3. Run Tests (pytest / npm test)
   ↓
4. Capture Test Output (stdout + stderr)
   ↓
5. Parse Traceback → Extract Errors
   ├─ File path: "src/calculator.py"
   ├─ Line number: 4
   ├─ Error type: SyntaxError
   └─ Message: "expected ':'"
   ↓
6. Apply Rule-Based Fix
   ├─ Open file at line 4
   ├─ Detect pattern (function definition)
   ├─ Add colon
   └─ Save file
   ↓
7. Git Commit
   ├─ Stage: src/calculator.py
   ├─ Commit: "[AI-AGENT] Fixed SYNTAX error in calculator.py line 4"
   └─ Continue to next error
   ↓
8. Run Tests Again (Iteration 2)
   ↓
9. Repeat Until:
   - All tests pass ✓
   - No fixes applied (stuck)
   - Max iterations reached (default: 5)
   ↓
10. Push Branch to GitHub
    ↓
11. Return Results
```

### Test-Driven Debugging
The agent does **NOT** scan code looking for issues. It:
- ✅ Runs actual tests
- ✅ Reads real failure output
- ✅ Fixes what tests report as broken
- ✅ Verifies fixes work by re-running tests

This is like **automated TDD** - red → green → refactor loop.

---

## 📊 Success Rate by Error Type

### Current Implementation (Rule-Based Only)

| Error Type | Success Rate | Notes |
|------------|--------------|-------|
| **SYNTAX** (missing colons) | ~95% | Very reliable |
| **INDENTATION** | ~90% | Good with context-aware fixing |
| **TYPE_ERROR** (typing imports) | ~85% | Works for standard typing module |
| **IMPORT** (comment out) | ~70% | Crude but prevents crashes |
| **LINTING** (unused imports) | ~60% | Can break if import has side effects |
| **LOGIC** (variable init) | ~20% | Creates more bugs than fixes! |

### With LLM Integration (Planned)

| Error Type | Expected Success Rate | Notes |
|------------|----------------------|-------|
| **Complex Logic** | ~70% | Needs good prompts + context |
| **Semantic Errors** | ~60% | Depends on code quality |
| **API Usage** | ~80% | LLM has training data on APIs |
| **Test Failures** | ~50% | Hard to determine intent |
| **Missing Features** | ~40% | Requires code generation |

---

## 🎯 When to Use Rule-Based vs LLM

### Use Rule-Based Fixes When:
✅ Error pattern is well-defined (e.g., "missing colon")  
✅ Fix is deterministic (only one correct solution)  
✅ No context needed beyond the error line  
✅ Fast execution required (< 1 second)  
✅ Cost-sensitive (no API calls)

**Examples:**
- Add missing colon
- Fix indentation
- Add typing imports
- Remove unused imports

### Use LLM When:
✅ Multiple possible fixes  
✅ Requires understanding intent  
✅ Needs broader code context  
✅ Involves writing new code  
✅ API/library knowledge required

**Examples:**
- Fix wrong algorithm
- Implement missing function
- Refactor for performance
- Update deprecated API calls

### Hybrid Approach (Best Practice):
```
1. Try rule-based fix first (fast, cheap)
2. Run tests again
3. If still failing → Use LLM (slower, costs $$)
4. Validate LLM fix with tests
```

---

## 🚀 Future Roadmap

### Phase 1: Current (Rule-Based Only) ✅
- [x] SYNTAX errors (missing colons)
- [x] INDENTATION errors  
- [x] TYPE_ERROR (typing imports)
- [x] Basic IMPORT errors
- [x] Real-time WebSocket progress
- [x] GitHub integration

### Phase 2: LLM Integration (Next) 🔄
- [ ] OpenAI/Anthropic API integration
- [ ] Context-aware prompting
- [ ] Fallback to LLM when rules fail
- [ ] Cost tracking per run
- [ ] Confidence scoring

### Phase 3: Advanced Features 🔮
- [ ] Multi-file refactoring
- [ ] Test generation for uncovered code
- [ ] Performance optimization suggestions
- [ ] Security vulnerability fixes
- [ ] Documentation generation

### Phase 4: Production Ready 🏭
- [ ] Custom rule creation UI
- [ ] Learning from successful fixes
- [ ] Team collaboration features
- [ ] CI/CD pipeline integration
- [ ] Rollback capabilities

---

## 📝 Configuration Options

### Current Settings
```python
# In AgentRequest model
max_retries: int = 5  # Max iterations before giving up

# In ErrorParser
max_errors: int = 10  # Pytest maxfail limit

# In DockerRunner  
test_timeout: int = 120  # Seconds before test times out
```

### Planned Settings (with LLM)
```python
# Future configuration
use_llm: bool = True  # Enable LLM fallback
llm_provider: str = "openai"  # openai | anthropic | local
max_llm_calls: int = 3  # Limit LLM usage per run
confidence_threshold: float = 0.8  # Min confidence to apply LLM fix
```

---

## 🎓 Examples from Your Test Run

### Run #12 Results

**Starting State:**
```python
# 3 intentional errors:
1. calculator.py:4 - Missing colon (SYNTAX)
2. validator.py:3 - Wrong indentation (INDENTATION)  
3. utils.py:6 - Missing List import (TYPE_ERROR)
```

**Iteration 1:**
```bash
Running pytest...
Found 2 errors (couldn't detect #3 yet - syntax prevents import)

Fixing SYNTAX in calculator.py:4
✓ Added colon: 'def subtract(a, b) # comment:' -> 'def subtract(a, b):'
Committed: [AI-AGENT] Fixed SYNTAX error

Fixing INDENTATION in validator.py:3  
✓ Fixed indentation: 4 -> 8 spaces
Committed: [AI-AGENT] Fixed INDENTATION error

Applied 2 fixes ✅
```

**Iteration 2:**
```bash
Running pytest...
Now Python can import files, found 1 error:

NameError: name 'List' is not defined in utils.py:6

Fixing TYPE_ERROR in utils.py:6
✓ Added import: from typing import List
Committed: [AI-AGENT] Fixed TYPE_ERROR error

Applied 1 fix ✅
```

**Iteration 3:**
```bash
Running pytest...
All tests passed! ✅

Status: PASSED
Total Fixes: 3
Iterations: 3
Branch: TESTTEAM_r3b1e_AI_FIX
```

---

## 🔍 Debugging & Monitoring

### Backend Logs
```bash
# Real-time progress in terminal
🚀 [ASYNC] Started run #12
📡 [Thread] Progress: 🔍 Starting agent
📡 [Thread] Progress: 📥 Cloning repository
📡 [Thread] Progress: 🐍 Detected Python project
📡 [Thread] Progress: 🧪 Running tests (Iteration 1/5)
📡 [Thread] Progress: ⚠️ Found 2 error(s)
📡 [Thread] Progress: 🔧 Fixing SYNTAX in calculator.py:4
📡 [Thread] Progress: ✅ Fixed SYNTAX in calculator.py:4
```

### Frontend Progress UI
- Live connection indicator (green = connected)
- Real-time status updates
- Scrollable progress log with timestamps
- Color-coded by severity (green = success, red = error)
- Auto-navigation when complete

### Database Tracking
```sql
-- Every run is saved
SELECT id, status, total_failures, total_fixes, iterations, duration 
FROM agent_runs 
WHERE user_id = 1 
ORDER BY created_at DESC;
```

---

## 💡 Best Practices

### For Users:
1. **Start with simple repos** - Test with known fixable errors
2. **Review fixes** - Don't blindly merge AI changes
3. **Use test coverage** - More tests = better detection
4. **Set realistic max_retries** - Default 5 is good balance

### For Developers:
1. **Add more rule patterns** - Expand ErrorParser regex
2. **Improve context awareness** - Use AST parsing for indentation
3. **Add LLM fallback** - When rules fail, try LLM
4. **Track metrics** - Success rate per error type

---

## 📚 Technical Details

### Architecture
```
Frontend (React)
  ↓ HTTP + WebSocket
Backend (FastAPI)
  ↓
DockerRunner (Orchestrator)
  ├─ GitHandler (Clone/Commit/Push)
  ├─ ErrorParser (Parse pytest output)
  └─ FixEngine (Apply fixes)
      ├─ _fix_syntax()
      ├─ _fix_indentation()
      ├─ _fix_type_error()
      ├─ _fix_import()
      ├─ _fix_linting()
      └─ _fix_logic()
```

### Technologies
- **Backend:** Python 3.11, FastAPI, SQLAlchemy, GitPython
- **Frontend:** React 18, Vite, TailwindCSS, WebSocket API
- **Database:** PostgreSQL (Neon)
- **Testing:** pytest (Python), Jest (JavaScript)
- **VCS:** GitHub API, OAuth 2.0

---

## 🤝 Contributing

### Adding New Error Fixer

1. **Add pattern to parser:**
```python
# app/parser.py
ErrorType.YOUR_ERROR: [
    r'YourErrorPattern',
    r'Another pattern'
]
```

2. **Implement fixer:**
```python
# app/fixer.py
def _fix_your_error(self, error: ErrorInfo) -> bool:
    # Read file
    # Apply fix
    # Save file
    # Return True if successful
```

3. **Add to dispatch:**
```python
# app/fixer.py
def apply_fix(self, error: ErrorInfo) -> bool:
    if error.type == ErrorType.YOUR_ERROR:
        return self._fix_your_error(error)
```

4. **Test it:**
```bash
# Create test repo with your error
# Run agent
# Verify fix applied
```

---

## 📞 Support & Questions

**What errors can you fix right now?**
- SYNTAX: Missing colons ✅
- INDENTATION: Wrong spacing ✅  
- TYPE_ERROR: Missing typing imports ✅
- IMPORT: Comment out missing imports ✅
- LINTING: Remove unused imports ✅

**What needs LLM?**
- Logic errors (wrong algorithm)
- Missing functionality (generate code)
- Complex refactoring
- Performance optimization

**What can't be fixed?**
- Environment issues
- External service failures
- Hardware problems
- Configuration errors

---

## 📄 License & Disclaimer

**This is an experimental tool.** 

⚠️ **Always review AI-generated fixes before merging!**

The agent can:
- ✅ Fix simple, mechanical errors reliably
- ⚠️ Sometimes break working code (rare with current rules)
- ❌ Not understand complex business logic (yet)

Use in development environments first. Test thoroughly before production.

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0 (Rule-Based)  
**Next Release:** 2.0.0 (LLM Integration)
