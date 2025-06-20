import sys
import os
import json
import httpx
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.services.health import router as health_router
from backend.agents.manager import agent_manager
from backend.config import config
from backend.core import lifecycle_manager, lifespan
from backend.utils.logger import get_async_logger, get_logging_config
from backend.websocket import ws_connection_manager
from fastapi.middleware.cors import CORSMiddleware

logger = get_async_logger(__name__)

app = FastAPI(
    title="PolyMind App",
    description="Fast modern AI service framework",
    lifespan=lifespan,
)

# Cấu hình CORS (cho phép tất cả nguồn trong ví dụ này)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lấy API key từ biến môi trường
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"


async def get_ai_response(messages: list):
    """Gửi yêu cầu đến Together AI API và trả về phản hồi"""
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        """Gửi yêu cầu đến Together AI API chờ phản hồi 30 giây"""
        try:
            response = await client.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Error: {str(e)}"


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat_history = []

    try:
        while True:
            # Nhận tin nhắn từ client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Thêm tin nhắn người dùng vào lịch sử chat
            user_message = {"role": "user", "content": message_data["message"]}
            chat_history.append(user_message)

            try:
                # Gọi API AI và nhận phản hồi
                ai_response = await get_ai_response(chat_history)

                # Thêm phản hồi AI vào lịch sử chat
                ai_message = {"role": "assistant", "content": ai_response}
                chat_history.append(ai_message)

                # Gửi phản hồi về client
                await websocket.send_text(
                    json.dumps({"sender": "ai", "message": ai_response})
                )
            except Exception as e:
                await websocket.send_text(
                    json.dumps(
                        {"sender": "system", "message": f"AI service error: {str(e)}"}
                    )
                )

    except WebSocketDisconnect:
        logger.info("Client disconnected")
    except Exception as e:
        await websocket.send_text(
            json.dumps({"sender": "system", "message": f"Server error: {str(e)}"})
        )
        await websocket.close()


# Handle Chrome DevTools request to avoid 404
@app.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools_config():
    """Handle Chrome DevTools configuration request to avoid 404."""
    return {"status": "not_configured"}


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
            log_config=get_logging_config(),
            # Tối ưu cho WebSocket
            ws_ping_interval=20,
            ws_ping_timeout=30,
            timeout_keep_alive=5,
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Server shutdown requested by user")
    except Exception as e:
        logger.error(f"💥 Server startup failed: {e}")
        logger.exception("Server startup error details:")
        sys.exit(1)
    finally:
        logger.info("🔚 PolyMind server stopped")


if __name__ == "__main__":
    # logger = get_async_logger("server_main")
    try:
        logger.info("🚀 Starting PolyMind server in development mode")
        main()
    except Exception as e:
        logger.exception("💥 Critical error in main thread")
        sys.exit(1)
