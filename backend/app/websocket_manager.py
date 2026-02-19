"""WebSocket connection manager for real-time progress updates"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor


class ConnectionManager:
    """Manages WebSocket connections for agent runs"""
    
    def __init__(self):
        # Map of run_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
        # Store the main event loop reference
        self.main_loop = None
        # Progress queue for thread-safe communication
        self.progress_queue: Dict[str, list] = {}
    
    def set_loop(self, loop):
        """Set the main event loop reference"""
        self.main_loop = loop
    
    async def connect(self, websocket: WebSocket, run_id: str):
        """Accept a new WebSocket connection for a specific run"""
        await websocket.accept()
        
        if run_id not in self.active_connections:
            self.active_connections[run_id] = set()
            self.locks[run_id] = asyncio.Lock()
            self.progress_queue[run_id] = []
        
        self.active_connections[run_id].add(websocket)
        print(f"✅ WebSocket connected for run #{run_id}")
        
        # Send any queued messages
        if self.progress_queue[run_id]:
            for msg in self.progress_queue[run_id]:
                try:
                    await websocket.send_json(msg)
                except:
                    pass
    
    def disconnect(self, websocket: WebSocket, run_id: str):
        """Remove a WebSocket connection"""
        if run_id in self.active_connections:
            self.active_connections[run_id].discard(websocket)
            
            # Clean up if no more connections
            if not self.active_connections[run_id]:
                del self.active_connections[run_id]
                if run_id in self.locks:
                    del self.locks[run_id]
                # Keep queue for a while in case client reconnects
        
        print(f"❌ WebSocket disconnected for run #{run_id}")
    
    async def send_progress(self, run_id: str, message: dict):
        """Send progress update to all connections for a specific run"""
        if run_id not in self.active_connections:
            # Queue the message if no connections yet
            if run_id not in self.progress_queue:
                self.progress_queue[run_id] = []
            self.progress_queue[run_id].append(message)
            print(f"📦 Queued message for run #{run_id} (no active connections)")
            return
        
        async with self.locks[run_id]:
            disconnected = set()
            
            for connection in self.active_connections[run_id]:
                try:
                    await connection.send_json(message)
                    print(f"📤 Sent to WebSocket for run #{run_id}: {message['message'][:50]}")
                except Exception as e:
                    print(f"Error sending to WebSocket: {e}")
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for connection in disconnected:
                self.active_connections[run_id].discard(connection)
    
    def send_progress_sync(self, run_id: str, status: str, message: str, data: dict = None):
        """Thread-safe synchronous wrapper for sending progress from background tasks"""
        msg = {
            "status": status,
            "message": message,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        if data:
            msg["data"] = data
        
        print(f"📡 [Thread] Progress for run #{run_id}: {message}")
        
        # If we have the main loop, schedule the coroutine
        if self.main_loop and self.main_loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(
                    self.send_progress(str(run_id), msg),
                    self.main_loop
                )
                print(f"✅ Scheduled progress send for run #{run_id}")
            except Exception as e:
                print(f"❌ Failed to schedule progress: {e}")
                # Fallback: queue the message
                if str(run_id) not in self.progress_queue:
                    self.progress_queue[str(run_id)] = []
                self.progress_queue[str(run_id)].append(msg)
        else:
            # No loop available, queue the message
            print(f"⚠️ No event loop, queuing message for run #{run_id}")
            if str(run_id) not in self.progress_queue:
                self.progress_queue[str(run_id)] = []
            self.progress_queue[str(run_id)].append(msg)


# Global instance
ws_manager = ConnectionManager()
