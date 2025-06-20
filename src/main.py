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
from src.utils.logger import get_logger

app = FastAPI(title="PolyMind App", description="Fast modern AI service framework")

# Initialize logger
logger = None

async def get_app_logger():
    """Get or initialize global logger for the application."""
    global logger
    if logger is None:
        logger = await get_logger("polymind_main")
        await logger.info("📝 Logger initialized for PolyMind main application")
    return logger

@app.on_event("startup")
async def startup_event():
    """Setup agents khi khởi động app."""
    # Initialize logger first
    app_logger = await get_app_logger()
    
    await app_logger.info("🚀 Starting PolyMind application...")
    
    # Kiểm tra environment variables
    if not config.check_required_env():
        await app_logger.warning("⚠️  Some environment variables are missing. Some features may not work.")
        print("⚠️  Some environment variables are missing. Some features may not work.")
    else:
        await app_logger.info("✅ All required environment variables found")
    
    await agent_manager.setup_default_agents()
    await app_logger.info("✅ Agent setup completed")
    print("✅ Agent setup completed")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Log connection
        if logger:
            await logger.info(f"🔌 New WebSocket connection established. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # Log disconnection (using sync logging for simplicity in sync method)
        if logger:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(logger.info(f"🔌 WebSocket connection closed. Remaining connections: {len(self.active_connections)}"))
            except:
                pass  # Failsafe if no event loop

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
    app_logger = await get_app_logger()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Lấy thông tin từ message
            user_message = message_data.get('content', '')
            agent_id = message_data.get('agent', 'deepseek')  # Default to deepseek
            is_streaming = message_data.get('streaming', False)
            
            # Log incoming message
            await app_logger.info(f"💬 Received message for agent '{agent_id}' (streaming: {is_streaming}): {user_message[:100]}{'...' if len(user_message) > 100 else ''}")
            
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
                            "agent": agent_id                        
                        }), websocket)
                        
                        # Log successful streaming response
                        await app_logger.info(f"✅ Streaming response completed for agent '{agent_id}' - {len(response_content)} characters")
                    else:
                        await app_logger.error(f"❌ Agent '{agent_id}' không khả dụng")
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
                      # Log successful regular response
                    await app_logger.info(f"✅ Regular response completed for agent '{agent_id}' using model '{response.model_name}' - {len(response.content)} characters")
                    
            except Exception as e:
                # Log error details
                await app_logger.error(f"❌ Error processing message for agent '{agent_id}': {str(e)}")
                # Gửi error response
                await manager.send_personal_message(json.dumps({
                    "type": "error",
                    "content": f"Lỗi xử lý: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }), websocket)
            
    except WebSocketDisconnect:
        await app_logger.info("🔌 WebSocket client disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        await app_logger.error(f"❌ WebSocket error: {str(e)}")
        manager.disconnect(websocket)


def main() -> None:
    """Entry point để chạy development server."""
    import uvicorn

    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
