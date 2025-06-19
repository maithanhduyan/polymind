from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
import asyncio
from datetime import datetime
from src.services.health import router as health_router
from src.agents.manager import agent_manager
from src.agents import AgentType, AgentResponse
from src.config import config

app = FastAPI(title="PolyMind App", description="Fast modern AI service framework")

@app.on_event("startup")
async def startup_event():
    """Setup agents khi khởi động app."""
    print("🚀 Starting PolyMind...")
    
    # Kiểm tra environment variables
    if not config.check_required_env():
        print("⚠️  Some environment variables are missing. Some features may not work.")
    
    await agent_manager.setup_default_agents()
    print("✅ Agent setup completed")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Include API routers
app.include_router(health_router)


# Serve frontend at root
@app.get("/")
async def serve_frontend():
    """Serve the main frontend page."""
    return FileResponse("frontend/index.html")


@app.get("/chat")
async def serve_chat():
    """Serve the main chat page."""
    return FileResponse("frontend/chat.html")


@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {"status": "ok", "message": "PolyMind API is running"}


@app.get("/api/chat/agents")
async def get_chat_agents():
    """Get available chat agents."""
    agents = []
    for agent_id, agent_instance in agent_manager.agents.items():
        agent_info = agent_instance.info
        agents.append({
            "id": agent_id,
            "name": agent_info["name"],
            "description": agent_info["description"],
            "type": agent_info["type"],
            "conversation_length": agent_info.get("conversation_length", 0)
        })
    
    return {"agents": agents}


@app.get("/api/chat/agents/health")
async def get_agents_health():
    """Kiểm tra health của tất cả agents."""
    return await agent_manager.health_check()


# WebSocket endpoint for chat
@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Lấy thông tin từ message
            user_message = message_data.get('content', '')
            agent_id = message_data.get('agent', 'deepseek')  # Default to deepseek
            is_streaming = message_data.get('streaming', False)
            
            try:
                if is_streaming:
                    # Streaming response
                    await manager.send_personal_message(json.dumps({
                        "type": "ai_typing",
                        "agent": agent_id
                    }), websocket)
                    
                    agent = agent_manager.get_agent(agent_id)
                    if agent:
                        response_content = ""
                        stream = await agent.stream_chat(user_message)
                        async for chunk in stream:
                            response_content += chunk
                            await manager.send_personal_message(json.dumps({
                                "type": "ai_chunk",
                                "content": chunk,
                                "agent": agent_id
                            }), websocket)
                        
                        # Gửi final response
                        await manager.send_personal_message(json.dumps({
                            "type": "ai_response",
                            "content": response_content,
                            "timestamp": datetime.now().isoformat(),
                            "agent": agent_id                        }), websocket)
                    else:
                        await manager.send_personal_message(json.dumps({
                            "type": "error",
                            "content": f"Agent '{agent_id}' không khả dụng",
                            "timestamp": datetime.now().isoformat()
                        }), websocket)
                else:
                    # Regular response
                    response = await agent_manager.chat(user_message, agent_id)
                    
                    await manager.send_personal_message(json.dumps({
                        "type": "ai_response",
                        "content": response.content,
                        "timestamp": datetime.now().isoformat(),
                        "agent": agent_id,
                        "model": response.model_name
                    }), websocket)
                    
            except Exception as e:
                # Gửi error response
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "content": f"Lỗi xử lý: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def main() -> None:
    """Entry point để chạy development server."""
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
