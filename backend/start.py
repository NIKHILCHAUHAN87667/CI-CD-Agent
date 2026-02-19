"""
Startup script for the backend server with proper watchfiles configuration
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_excludes=[
            "workspace/*",
            "workspace/**/*",
            "*.db",
            "*.sqlite",
            "*.log"
        ]
    )
