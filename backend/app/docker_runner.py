import os
import subprocess
import json
import threading
import time
import sys
import venv
import httpx
from typing import List, Dict
from app.models import ErrorInfo, FixResult, AgentResponse, ErrorType
from app.parser import ErrorParser
from app.fixer import FixEngine
from app.git_utils import GitHandler
from app.config import WORKSPACE_DIR, RESULTS_FILE, TEST_COMMAND


class DockerRunner:
    """Main orchestrator for the AI DevOps agent"""
    
    def __init__(self, repo_url: str, team: str, leader: str, max_retries: int = 5, ws_manager=None, run_id=None):
        self.repo_url = repo_url
        self.team = team
        self.leader = leader
        self.max_retries = max_retries
        self.ws_manager = ws_manager
        self.run_id = run_id
        
        # Initialize components
        self.git_handler = GitHandler(WORKSPACE_DIR)
        self.parser = ErrorParser()
        self.fixer: FixEngine = None
        
        # Project type detection
        self.project_type = None  # 'python', 'javascript', or 'unknown'
        self.test_command = None
        self.venv_path = None
        self.venv_python = None
        
        # Tracking
        self.fixes: List[FixResult] = []
        self.total_failures = 0
        self.iterations = 0
        self.branch_name = None
        self.sandbox_url = os.getenv("SANDBOX_URL", "").strip()
        self.sandbox_token = os.getenv("SANDBOX_TOKEN", "").strip()
    
    def _emit_progress(self, status: str, message: str, data: dict = None):
        """Emit progress update via WebSocket"""
        if self.ws_manager and self.run_id:
            self.ws_manager.send_progress_sync(self.run_id, status, message, data)
        print(f"📡 {message}")
    
    def run(self) -> AgentResponse:
        """Main execution flow"""
        self._emit_progress("info", f"🔍 Starting AI DevOps Agent for {self.repo_url}")
        print(f"Starting AI DevOps Agent for {self.repo_url}")
        
        # Step 1: Clone repository
        self._emit_progress("cloning", "📥 Cloning repository...")
        repo_path = self.git_handler.clone_repo(self.repo_url)
        self.fixer = FixEngine(repo_path)
        self._emit_progress("success", "✅ Repository cloned successfully")
        
        # Step 1.5: Detect project type
        self._emit_progress("analyzing", "🔍 Detecting project type...")
        self._detect_project_type(repo_path)
        self._emit_progress("info", f"📋 Detected {self.project_type} project")
        # Step 2.5: Create virtual environment for Python projects (local mode only)
        if not self.sandbox_url and self.project_type == 'python':
            self._emit_progress("venv", "🔧 Creating isolated Python environment...")
            self._create_venv(repo_path)
            self._emit_progress("success", "✅ Virtual environment created")
        # Step 2: Install dependencies (local mode only)
        if not self.sandbox_url:
            self._emit_progress("installing", "📦 Installing dependencies...")
            self._install_dependencies(repo_path)
            self._emit_progress("success", "✅ Dependencies installed")
        
        # Step 3: Create new branch
        self._emit_progress("info", "🌿 Creating feature branch...")
        branch_name = self.git_handler.create_branch(self.team, self.leader)
        self.branch_name = branch_name
        self._emit_progress("success", f"✅ Branch created: {branch_name}")
        
        # If sandbox is enabled, push branch so the sandbox can clone it
        if self.sandbox_url:
            self._emit_progress("info", "📤 Pushing branch for sandbox access...")
            if not self.git_handler.push_branch(branch_name):
                raise Exception("Failed to push branch for sandbox access")
        
        # Step 4: Iterative fix loop
        for iteration in range(self.max_retries):
            self.iterations = iteration + 1
            print(f"\n=== Iteration {self.iterations} ===")
            self._emit_progress("testing", f"🧪 Running tests (Iteration {self.iterations}/{self.max_retries})...")
            
            # If sandbox is enabled, ensure latest commits are pushed before testing
            if self.sandbox_url:
                if not self.git_handler.push_branch(branch_name):
                    self._emit_progress("error", "❌ Failed to push branch updates for sandbox")
                    raise Exception("Failed to push branch updates for sandbox")
            
            # Run tests
            test_output = self._run_tests(repo_path)
            
            # Parse errors (pass repo_path to filter out system library errors)
            errors = self.parser.parse_errors(test_output, repo_path=repo_path)
            
            if not errors:
                print("No errors found! Tests passed.")
                self._emit_progress("success", "✅ All tests passed!")
                break
            
            print(f"Found {len(errors)} errors")
            self.total_failures = len(errors)
            self._emit_progress("warning", f"⚠️ Found {len(errors)} error(s) to fix")
            
            # Apply fixes
            self._emit_progress("fixing", f"🔧 Applying fixes to {len(errors)} error(s)...")
            fixed_count = 0
            for error in errors:
                if self._apply_and_commit_fix(error):
                    fixed_count += 1
            
            print(f"Applied {fixed_count} fixes in iteration {self.iterations}")
            self._emit_progress("info", f"✅ Applied {fixed_count} fix(es) in iteration {self.iterations}")
            
            # If no fixes were applied, break to avoid infinite loop
            if fixed_count == 0:
                print("No fixes could be applied. Stopping.")
                self._emit_progress("error", "❌ No fixes could be applied. Stopping iterations.")
                break
        
        # Step 5: Push branch (only if fixes were applied)
        if len(self.fixes) > 0:
            self._emit_progress("pushing", "📤 Pushing changes to GitHub...")
            try:
                self.git_handler.push_branch(branch_name)
                self._emit_progress("success", f"✅ Branch pushed: {branch_name}")
            except Exception as e:
                self._emit_progress("error", f"❌ Failed to push branch: {str(e)}")
                print(f"Error pushing branch: {e}")
        else:
            self._emit_progress("warning", "⚠️ No fixes were applied, skipping push")
            print("No fixes applied, skipping push")
        
        # Step 6: Generate response
        self._emit_progress("completing", "📊 Generating final report...")
        response = self._generate_response(branch_name)
        self._emit_progress("completed", f"✅ Agent run completed! Status: {response.status}", {
            "status": response.status,
            "total_fixes": response.total_fixes,
            "total_failures": response.total_failures,
            "iterations": response.iterations,
            "branch": branch_name
        })
        
        # Step 7: Save results.json
        self._save_results(response)
        
        return response
    
    def _detect_project_type(self, repo_path: str):
        """Detect if project is Python or JavaScript/React"""
        package_json = os.path.join(repo_path, 'package.json')
        requirements_txt = os.path.join(repo_path, 'requirements.txt')
        
        if os.path.exists(package_json):
            self.project_type = 'javascript'
            self.test_command = ['npm', 'test', '--', '--passWithNoTests']
            print("📦 Detected JavaScript/React project (package.json found)")
        elif os.path.exists(requirements_txt):
            self.project_type = 'python'
            self.test_command = ['pytest', '--maxfail=10', '-v']
            print("🐍 Detected Python project (requirements.txt found)")
        else:
            # Default to Python with pytest
            self.project_type = 'unknown'
            self.test_command = ['pytest', '--maxfail=10', '-v']
            print("⚠️  Could not detect project type, defaulting to Python/pytest")
    
    def _create_venv(self, repo_path: str):
        """Create a virtual environment for the Python project"""
        self.venv_path = os.path.join(repo_path, '.venv')
        
        # Check if venv already exists
        if os.path.exists(self.venv_path):
            print(f"Virtual environment already exists at {self.venv_path}")
        else:
            print(f"Creating virtual environment at {self.venv_path}...")
            try:
                venv.create(self.venv_path, with_pip=True)
                print("✅ Virtual environment created successfully")
            except Exception as e:
                print(f"⚠️  Error creating venv: {e}, will use system Python")
                self.venv_path = None
                self.venv_python = None
                return
        
        # Set path to venv's python executable
        if sys.platform == "win32":
            self.venv_python = os.path.join(self.venv_path, 'Scripts', 'python.exe')
        else:
            self.venv_python = os.path.join(self.venv_path, 'bin', 'python')
        
        print(f"✅ Using Python: {self.venv_python}")
    
    def _install_dependencies(self, repo_path: str):
        """Install dependencies based on project type"""
        if self.project_type == 'javascript':
            package_json = os.path.join(repo_path, 'package.json')
            if os.path.exists(package_json):
                print("Installing npm dependencies...")
                try:
                    # Run npm install (shell=True for Windows to find npm in PATH)
                    result = subprocess.run(
                        'npm install',
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        shell=True,
                        timeout=300  # 5 minute timeout
                    )
                    if result.returncode == 0:
                        print("✅ npm dependencies installed successfully")
                    else:
                        print(f"⚠️  npm install had warnings: {result.stderr[:200]}")
                except subprocess.TimeoutExpired:
                    print("❌ npm install timed out")
                except Exception as e:
                    print(f"❌ Error installing npm dependencies: {e}")
        elif self.project_type == 'python':
            requirements_file = os.path.join(repo_path, 'requirements.txt')
            if os.path.exists(requirements_file):
                print("Installing pip dependencies in virtual environment...")
                try:
                    # Use venv's pip if available, otherwise system pip
                    pip_cmd = [self.venv_python, '-m', 'pip'] if self.venv_python else ['pip']
                    
                    subprocess.run(
                        pip_cmd + ['install', '-r', 'requirements.txt'],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minute timeout
                    )
                    print("✅ Dependencies installed successfully in isolated environment")
                except subprocess.TimeoutExpired:
                    print("❌ Dependency installation timed out")
                except Exception as e:
                    print(f"❌ Error installing dependencies: {e}")
        else:
            print("⚠️  No dependencies file found, skipping installation")
    
    def _run_tests(self, repo_path: str) -> str:
        """Run tests based on project type and return output"""
        test_cmd_str = ' '.join(self.test_command)
        print(f"Running tests with: {test_cmd_str}")
        
        # If sandbox is configured, run tests remotely
        if self.sandbox_url:
            try:
                url = self.sandbox_url.rstrip("/") + "/run-tests"
                headers = {"X-Sandbox-Token": self.sandbox_token} if self.sandbox_token else {}
                payload = {
                    "repo_url": self.repo_url,
                    "branch": self.branch_name,
                    "timeout_sec": 120,
                }
                resp = httpx.post(url, json=payload, headers=headers, timeout=150)
                resp.raise_for_status()
                data = resp.json()
                stdout = data.get("stdout", "")
                stderr = data.get("stderr", "")
                if data.get("timed_out"):
                    self._emit_progress("warning", "⚠️ Sandbox tests timed out")
                return stdout + "\n" + stderr
            except Exception as e:
                self._emit_progress("error", f"❌ Sandbox test execution failed: {str(e)}")
                return ""
        
        # Flag to track if process is still running
        process_running = {'status': True}
        
        # Function to send periodic progress updates
        def send_progress_updates():
            elapsed = 0
            while process_running['status'] and elapsed < 120:
                time.sleep(10)  # Send update every 10 seconds
                elapsed += 10
                if process_running['status']:
                    self._emit_progress("info", f"⏳ Tests still running... ({elapsed}s elapsed)")
        
        # Start progress update thread
        progress_thread = threading.Thread(target=send_progress_updates, daemon=True)
        progress_thread.start()
        
        try:
            # For Python projects, use venv's python if available
            if self.project_type == 'python':
                # Use venv's python -m pytest to isolate from system packages
                python_exe = self.venv_python if self.venv_python else 'python'
                cmd = [python_exe, '-m', 'pytest', '--maxfail=10', '-v', '--tb=short']
                print(f"Using Python: {python_exe}")
            elif self.project_type == 'javascript':
                cmd = ' '.join(self.test_command)
            else:
                cmd = self.test_command
            
            # Use Popen for better control and to avoid output buffering issues
            process = subprocess.Popen(
                cmd,
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=(self.project_type == 'javascript'),  # Use shell for npm on Windows
                bufsize=1  # Line buffered
            )
            
            # Wait for process with timeout
            try:
                stdout, stderr = process.communicate(timeout=120)
                returncode = process.returncode
            except subprocess.TimeoutExpired:
                print("⏱️  Test execution timed out (120s limit), terminating process...")
                process.kill()
                stdout, stderr = process.communicate()
                self._emit_progress("warning", "⚠️ Test execution timed out")
                return ""
            finally:
                process_running['status'] = False
            
            # Combine stdout and stderr
            output = stdout + "\n" + stderr
            
            # Log test result
            if returncode == 0:
                print("✅ Tests passed")
                self._emit_progress("success", "✅ Tests completed successfully")
            else:
                print(f"❌ Tests failed with exit code {returncode}")
                self._emit_progress("info", f"📋 Tests completed with {returncode} failures")
            
            return output
        except Exception as e:
            process_running['status'] = False
            print(f"❌ Error running tests: {e}")
            self._emit_progress("error", f"❌ Error running tests: {str(e)}")
            return ""
        finally:
            process_running['status'] = False
    
    def _apply_and_commit_fix(self, error: ErrorInfo) -> bool:
        """Apply fix and commit if successful"""
        print(f"Attempting to fix {error.type} in {error.file}:{error.line}")
        self._emit_progress("fixing", f"🔧 Fixing {error.type.value} in {os.path.basename(error.file)}:{error.line}")
        
        # Apply fix
        success = self.fixer.apply_fix(error)
        
        if success:
            # Commit the fix
            try:
                commit_message = self.git_handler.commit_fix(
                    error.file,
                    error.type.value,
                    error.line,
                    error.message
                )
                
                self._emit_progress("success", f"✅ Fixed {error.type.value} in {os.path.basename(error.file)}:{error.line}")
                
                # Track the fix
                self.fixes.append(FixResult(
                    file=error.file,
                    line=error.line,
                    type=error.type.value,
                    commit_message=commit_message,
                    status="Fixed"
                ))
                
                print(f"✓ Fixed and committed")
                return True
            except Exception as e:
                print(f"Error committing fix: {e}")
                return False
        else:
            # Track failed fix
            self.fixes.append(FixResult(
                file=error.file,
                line=error.line,
                type=error.type.value,
                commit_message="",
                status="Failed"
            ))
            print(f"✗ Could not apply fix")
            return False
    
    def _generate_response(self, branch_name: str) -> AgentResponse:
        """Generate final response"""
        # Count successful fixes
        successful_fixes = sum(1 for fix in self.fixes if fix.status == "Fixed")
        
        # Determine overall status
        status = "PASSED" if successful_fixes > 0 and successful_fixes == len(self.fixes) else "PARTIAL"
        if successful_fixes == 0:
            status = "FAILED"
        
        return AgentResponse(
            repo=self.repo_url,
            branch=branch_name,
            total_failures=self.total_failures,
            total_fixes=successful_fixes,
            iterations=self.iterations,
            status=status,
            fixes=self.fixes
        )
    
    def _save_results(self, response: AgentResponse):
        """Save results to results.json"""
        try:
            with open(RESULTS_FILE, 'w') as f:
                json.dump(response.dict(), f, indent=2)
            print(f"Results saved to {RESULTS_FILE}")
        except Exception as e:
            print(f"Error saving results: {e}")
