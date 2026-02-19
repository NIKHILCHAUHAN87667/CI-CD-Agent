#!/usr/bin/env python3
"""
Agent entrypoint for sandboxed test execution
This script runs inside the agent Docker container
"""
import sys
import subprocess
import json
import os


def main():
    """
    This script is called from within the Docker agent container
    It receives the repo path and runs tests in isolation
    """
    if len(sys.argv) < 2:
        print("Usage: agent_entrypoint.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    
    # Change to repo directory
    os.chdir(repo_path)
    
    # Install dependencies if requirements.txt exists
    if os.path.exists('requirements.txt'):
        print("Installing dependencies...")
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'])
    
    # Run tests
    print("Running tests...")
    result = subprocess.run(
        ['pytest', '--maxfail=10', '-v'],
        capture_output=True,
        text=True
    )
    
    # Output results
    output = {
        'stdout': result.stdout,
        'stderr': result.stderr,
        'returncode': result.returncode
    }
    
    print(json.dumps(output))


if __name__ == '__main__':
    main()
