import logging
import logging.config
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
import asyncio
from datetime import datetime
from backend.services.health import router as health_router
from backend.agents.manager import agent_manager
from backend.agents import AgentType, AgentResponse
from backend.config import config
from backend.utils.logger import get_async_logger


# Quan trọng: Import LifecycleManager và lifespan
from backend.core import lifecycle_manager, lifespan

logger = get_async_logger(__name__)

# Sử dụng lifespan trong khởi tạo FastAPI
app = FastAPI(
    title="PolyMind App",
    description="Fast modern AI service framework",
    lifespan=lifespan,  # Tích hợp lifecycle manager
)

# WebSocket connection manager (giữ nguyên phần này nếu có)

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
        agents.append(
            {
                "id": agent_id,
                "name": agent_info["name"],
                "description": agent_info["description"],
                "type": agent_info["type"],
                "conversation_length": agent_info.get("conversation_length", 0),
            }
        )

    return {"agents": agents}


@app.get("/api/chat/agents/health")
async def get_agents_health():
    """Kiểm tra health của tất cả agents."""
    return await agent_manager.health_check()


def main() -> None:
    """Entry point để chạy development server."""
    import uvicorn

    try:
        logger.info(f"🚀 Starting server at {config.HOST}:{config.PORT}")
        logger.info(f"🔧 Debug mode: {'ON' if config.DEBUG else 'OFF'}")

        uvicorn.run(
            "backend.main:app",
            host=config.HOST,
            port=config.PORT,
            reload=config.DEBUG,
            log_config=None,  # Sử dụng logging của chúng ta, không dùng của Uvicorn
        )

    except KeyboardInterrupt:
        # Người dùng nhấn Ctrl+C để dừng server
        logger.info("\n🛑 Server shutdown requested by user")

    except Exception as e:
        # Lỗi nghiêm trọng khi khởi động server
        logger.error(f"💥 Server startup failed: {e}")
        logger.exception("Server startup error details:")
        sys.exit(1)

    finally:
        # Luôn chạy phần này dù có lỗi hay không
        logger.info("🔚 PolyMind server stopped")


if __name__ == "__main__":
    # Chỉ khởi tạo logger ở main thread
    logger = get_async_logger("server_main")

    try:
        logger.info("🚀 Starting PolyMind server in development mode")
        main()
    except Exception as e:
        logger.exception("💥 Critical error in main thread")
        sys.exit(1)
