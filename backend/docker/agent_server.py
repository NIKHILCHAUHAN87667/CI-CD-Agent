#!/usr/bin/env python3
"""
Sandbox agent service for isolated test execution.
Runs in a separate container and executes tests on a cloned repo.
"""
import os
import subprocess
import tempfile
from typing import Optional

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="AI DevOps Agent Sandbox", version="1.0.0")

SANDBOX_TOKEN = os.getenv("SANDBOX_TOKEN", "").strip()


class RunTestsRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = None
    timeout_sec: int = 120


@app.get("/health")
def health():
    return {"status": "ok"}


def _check_auth(x_sandbox_token: Optional[str]):
    if SANDBOX_TOKEN and x_sandbox_token != SANDBOX_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _run_cmd(cmd, cwd, timeout_sec):
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout_sec,
        shell=False,
    )


@app.post("/run-tests")
def run_tests(
    req: RunTestsRequest,
    x_sandbox_token: Optional[str] = Header(None),
):
    _check_auth(x_sandbox_token)

    with tempfile.TemporaryDirectory(prefix="agent-workspace-") as tmpdir:
        repo_path = os.path.join(tmpdir, "repo")

        clone_cmd = ["git", "clone", "--depth", "1"]
        if req.branch:
            clone_cmd += ["--branch", req.branch]
        clone_cmd += [req.repo_url, repo_path]

        try:
            _run_cmd(clone_cmd, cwd=tmpdir, timeout_sec=60)
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": "git clone timed out",
                "returncode": 1,
                "timed_out": True,
                "project_type": "unknown",
            }

        project_type = "unknown"
        if os.path.exists(os.path.join(repo_path, "package.json")):
            project_type = "javascript"
        elif os.path.exists(os.path.join(repo_path, "requirements.txt")):
            project_type = "python"

        timed_out = False
        stdout = ""
        stderr = ""
        returncode = 1

        try:
            if project_type == "javascript":
                _run_cmd(["npm", "install"], cwd=repo_path, timeout_sec=req.timeout_sec)
                result = _run_cmd(
                    ["npm", "test", "--", "--passWithNoTests"],
                    cwd=repo_path,
                    timeout_sec=req.timeout_sec,
                )
            else:
                if os.path.exists(os.path.join(repo_path, "requirements.txt")):
                    _run_cmd(
                        ["python", "-m", "pip", "install", "-r", "requirements.txt"],
                        cwd=repo_path,
                        timeout_sec=req.timeout_sec,
                    )
                result = _run_cmd(
                    ["pytest", "--maxfail=10", "-v", "--tb=short"],
                    cwd=repo_path,
                    timeout_sec=req.timeout_sec,
                )

            stdout = result.stdout
            stderr = result.stderr
            returncode = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            stderr = "test execution timed out"

        return {
            "stdout": stdout,
            "stderr": stderr,
            "returncode": returncode,
            "timed_out": timed_out,
            "project_type": project_type,
        }
