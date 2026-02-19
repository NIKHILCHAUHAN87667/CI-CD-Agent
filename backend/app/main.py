from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Header, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import json
from app.models import AgentRequest, AgentResponse
from app.docker_runner import DockerRunner
from app.database import engine, get_db
from app.db_models import Base, User, AgentRun
from app.auth import (
    exchange_code_for_token,
    get_github_user,
    create_access_token,
    get_current_user
)
from app.websocket_manager import ws_manager
from pydantic import BaseModel
import uvicorn
import httpx
import asyncio

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI DevOps Agent API",
    description="Automated test fixing and deployment agent",
    version="1.0.0"
)

# Startup event to capture event loop
@app.on_event("startup")
async def startup_event():
    """Capture the main event loop for WebSocket manager"""
    loop = asyncio.get_running_loop()
    ws_manager.set_loop(loop)
    print(f"✅ Event loop captured for WebSocket manager")
    
    # Ensure workspace directory exists
    import os
    from app.config import WORKSPACE_DIR
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    print(f"✅ Workspace directory ready: {WORKSPACE_DIR}")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth Models
class GitHubCallbackRequest(BaseModel):
    code: str


class AuthResponse(BaseModel):
    token: str
    user: dict


@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "running",
        "service": "AI DevOps Agent",
        "version": "1.0.0"
    }


@app.websocket("/ws/runs/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    """WebSocket endpoint for real-time progress updates during agent runs"""
    await ws_manager.connect(websocket, run_id)
    try:
        print(f"🔌 WebSocket connection established for run #{run_id}")
        # Keep connection alive and listen for client messages
        while True:
            try:
                # Wait for client message with timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                print(f"📨 Received from client (run #{run_id}): {data}")
                # Echo back to confirm connection
                await websocket.send_json({"type": "ping", "data": "pong"})
            except asyncio.TimeoutError:
                # Send keepalive ping every 30 seconds
                try:
                    await websocket.send_json({"type": "keepalive", "timestamp": __import__('datetime').datetime.now().isoformat()})
                    print(f"💓 Sent keepalive to run #{run_id}")
                except:
                    print(f"❌ Failed to send keepalive to run #{run_id}, closing connection")
                    break
    except WebSocketDisconnect:
        print(f"🔌 Client disconnected from run #{run_id}")
        ws_manager.disconnect(websocket, run_id)
    except Exception as e:
        print(f"❌ WebSocket error for run #{run_id}: {e}")
        ws_manager.disconnect(websocket, run_id)


@app.post("/auth/github/callback", response_model=AuthResponse)
async def github_callback(request: GitHubCallbackRequest, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    try:
        # Exchange code for access token
        access_token = await exchange_code_for_token(request.code)
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Get GitHub user info
        github_user = await get_github_user(access_token)
        
        # Validate GitHub user response
        if not github_user or "id" not in github_user:
            raise HTTPException(status_code=400, detail="Failed to get GitHub user info")
        
        # Create or update user in database
        user = db.query(User).filter(User.github_id == str(github_user["id"])).first()
        
        if not user:
            user = User(
                github_id=str(github_user["id"]),
                login=github_user.get("login", "unknown"),
                email=github_user.get("email"),
                avatar_url=github_user.get("avatar_url"),
                access_token=access_token
            )
            db.add(user)
        else:
            user.access_token = access_token
            user.login = github_user.get("login", user.login)
            user.avatar_url = github_user.get("avatar_url", user.avatar_url)
            if github_user.get("email"):
                user.email = github_user["email"]
        
        db.commit()
        db.refresh(user)
        
        # Create JWT token
        token = create_access_token({"sub": str(user.id)})
        
        return {
            "token": token,
            "user": {
                "id": user.id,
                "github_id": user.github_id,
                "login": user.login,
                "email": user.email,
                "avatar_url": user.avatar_url,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user"""
    return {
        "id": current_user.id,
        "github_id": current_user.github_id,
        "login": current_user.login,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
    }


@app.get("/debug/token")
async def debug_token(authorization: str = Header(None)):
    """Debug endpoint to check if token is being received"""
    return {
        "authorization_header": authorization,
        "has_bearer": "Bearer " in (authorization or ""),
        "message": "Check if Authorization header is present"
    }


@app.get("/repos")
async def get_user_repos(current_user: User = Depends(get_current_user)):
    """Fetch user's GitHub repositories"""
    try:
        async with httpx.AsyncClient() as client:
            # Fetch user's repositories
            response = await client.get(
                "https://api.github.com/user/repos",
                headers={
                    "Authorization": f"token {current_user.access_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                params={
                    "per_page": 100,
                    "sort": "updated",
                    "affiliation": "owner,collaborator,organization_member"
                }
            )
            response.raise_for_status()
            repos = response.json()
            
            # Format repositories for frontend
            formatted_repos = []
            for repo in repos:
                formatted_repos.append({
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "html_url": repo["html_url"],
                    "clone_url": repo["clone_url"],
                    "description": repo.get("description"),
                    "private": repo["private"],
                    "language": repo.get("language"),
                    "updated_at": repo["updated_at"],
                    "default_branch": repo.get("default_branch", "main")
                })
            
            return {"repositories": formatted_repos}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch repositories")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching repositories: {str(e)}")


@app.post("/run-agent", response_model=AgentResponse)
async def run_agent(
    request: AgentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Main endpoint to run the AI DevOps agent
    
    This endpoint:
    1. Clones the repository
    2. Installs dependencies
    3. Runs tests
    4. Parses errors
    5. Applies fixes
    6. Commits changes
    7. Pushes to new branch
    8. Returns results
    """
    start_time = datetime.utcnow()
    
    # Create database record FIRST with RUNNING status to avoid timeout
    repo_name = request.repo_url.split('/')[-1].replace('.git', '')
    agent_run = AgentRun(
        user_id=current_user.id,
        repo=request.repo_url,
        repo_name=repo_name,
        branch="",  # Will update after branch creation
        team=request.team,
        leader=request.leader,
        status="RUNNING",
        total_failures=0,
        total_fixes=0,
        iterations=0,
        fixes=[],
        duration="0:00:00"
    )
    db.add(agent_run)
    db.commit()
    db.refresh(agent_run)
    
    run_id = agent_run.id
    print(f"🚀 Started run #{run_id} for {repo_name}")
    
    # Send initial progress update
    ws_manager.send_progress_sync(run_id, "started", f"🚀 Starting agent run for {repo_name}")
    
    try:
        # Initialize and run the agent
        runner = DockerRunner(
            repo_url=request.repo_url,
            team=request.team,
            leader=request.leader,
            max_retries=request.max_retries,
            ws_manager=ws_manager,
            run_id=run_id
        )
        
        # Execute the agent
        result = runner.run()
        
        # Calculate duration
        duration = str(datetime.utcnow() - start_time).split('.')[0]
        
        # Update existing database record with results
        agent_run.branch = result.branch
        agent_run.status = result.status
        agent_run.total_failures = result.total_failures
        agent_run.total_fixes = result.total_fixes
        agent_run.iterations = result.iterations
        agent_run.fixes = [fix.dict() for fix in result.fixes]
        agent_run.duration = duration
        
        db.commit()
        db.refresh(agent_run)
        
        # Debug logging
        print(f"✅ Run #{run_id} completed with status: {result.status}")
        
        # Update result with database fields
        result.id = agent_run.id
        result.created_at = agent_run.created_at.isoformat()
        result.duration = duration
        result.repo_name = agent_run.repo_name
        
        # Debug logging - print full response
        print(f"📤 Returning response with ID: {result.id}")
        print(f"📦 Response: {result.model_dump()}")
        
        return result
        
    except Exception as e:
        # Update run status to FAILED
        duration = str(datetime.utcnow() - start_time).split('.')[0]
        agent_run.status = "FAILED"
        agent_run.duration = duration
        db.commit()
        
        print(f"❌ Run #{run_id} failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@app.post("/run-agent-async")
async def run_agent_async(
    request: AgentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Asynchronous version - runs agent in background with WebSocket progress
    Returns immediately with run ID for WebSocket connection
    """
    start_time = datetime.utcnow()
    
    # Create database record FIRST
    repo_name = request.repo_url.split('/')[-1].replace('.git', '')
    agent_run = AgentRun(
        user_id=current_user.id,
        repo=request.repo_url,
        repo_name=repo_name,
        branch="",
        team=request.team,
        leader=request.leader,
        status="RUNNING",
        total_failures=0,
        total_fixes=0,
        iterations=0,
        fixes=[],
        duration="0:00:00"
    )
    db.add(agent_run)
    db.commit()
    db.refresh(agent_run)
    
    run_id = agent_run.id
    print(f"🚀 [ASYNC] Started run #{run_id} for {repo_name}")
    
    # Send initial progress
    ws_manager.send_progress_sync(run_id, "started", f"🚀 Starting agent run for {repo_name}")
    
    def run_in_background():
        """Execute agent in background with progress updates"""
        print(f"🎬 [BACKGROUND] Task started for run #{run_id}")
        try:
            from app.database import SessionLocal
            bg_db = SessionLocal()
            
            print(f"🔧 [BACKGROUND] Initializing DockerRunner for run #{run_id}")
            ws_manager.send_progress_sync(run_id, "initializing", f"🔧 Initializing agent...")
            
            try:
                runner = DockerRunner(
                    repo_url=request.repo_url,
                    team=request.team,
                    leader=request.leader,
                    max_retries=request.max_retries,
                    ws_manager=ws_manager,
                    run_id=run_id
                )
                print(f"🏃 [BACKGROUND] Running agent for run #{run_id}")
                result = runner.run()
                
                # Update database
                duration = str(datetime.utcnow() - start_time).split('.')[0]
                bg_run = bg_db.query(AgentRun).filter(AgentRun.id == run_id).first()
                if bg_run:
                    bg_run.branch = result.branch
                    bg_run.status = result.status
                    bg_run.total_failures = result.total_failures
                    bg_run.total_fixes = result.total_fixes
                    bg_run.iterations = result.iterations
                    bg_run.fixes = [fix.dict() for fix in result.fixes]
                    bg_run.duration = duration
                    bg_db.commit()
                
                print(f"✅ [ASYNC] Run #{run_id} completed: {result.status}")
            finally:
                bg_db.close()
        except Exception as e:
            import traceback
            print(f"❌ [ASYNC] Run #{run_id} failed with exception:")
            traceback.print_exc()
            ws_manager.send_progress_sync(run_id, "error", f"❌ Failed: {str(e)}")
            from app.database import SessionLocal
            bg_db = SessionLocal()
            try:
                duration = str(datetime.utcnow() - start_time).split('.')[0]
                bg_run = bg_db.query(AgentRun).filter(AgentRun.id == run_id).first()
                if bg_run:
                    bg_run.status = "FAILED"
                    bg_run.duration = duration
                    bg_db.commit()
                ws_manager.send_progress_sync(run_id, "error", f"❌ Failed: {str(e)}")
            finally:
                bg_db.close()
    
    background_tasks.add_task(run_in_background)
    
    return {
        "id": run_id,
        "status": "RUNNING",
        "message": "Agent started. Connect to WebSocket for live progress.",
        "ws_url": f"/ws/runs/{run_id}",
        "repo_name": repo_name
    }


@app.get("/runs", response_model=List[dict])
async def get_runs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all runs for the current user"""
    runs = db.query(AgentRun).filter(AgentRun.user_id == current_user.id).order_by(AgentRun.created_at.desc()).all()
    
    return [
        {
            "id": run.id,
            "repo": run.repo,
            "repo_name": run.repo_name,
            "branch": run.branch,
            "team": run.team,
            "leader": run.leader,
            "status": run.status,
            "total_failures": run.total_failures,
            "total_fixes": run.total_fixes,
            "iterations": run.iterations,
            "duration": run.duration,
            "created_at": run.created_at.isoformat(),
        }
        for run in runs
    ]


@app.get("/runs/{run_id}")
async def get_run(
    run_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific run by ID"""
    run = db.query(AgentRun).filter(
        AgentRun.id == run_id,
        AgentRun.user_id == current_user.id
    ).first()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return {
        "id": run.id,
        "repo": run.repo,
        "repo_name":run.repo_name,
        "branch": run.branch,
        "team": run.team,
        "leader": run.leader,
        "status": run.status,
        "total_failures": run.total_failures,
        "total_fixes": run.total_fixes,
        "iterations": run.iterations,
        "fixes": run.fixes,
        "duration": run.duration,
        "created_at": run.created_at.isoformat(),
    }


@app.get("/debug/ws-manager")
def debug_ws_manager():
    """Debug endpoint to check WebSocket manager state"""
    return {
        "has_loop": ws_manager.main_loop is not None,
        "loop_running": ws_manager.main_loop.is_running() if ws_manager.main_loop else False,
        "active_connections": {run_id: len(conns) for run_id, conns in ws_manager.active_connections.items()},
        "queued_messages": {run_id: len(msgs) for run_id, msgs in ws_manager.progress_queue.items()}
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
