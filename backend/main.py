import sys
import json
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

logger = get_async_logger(__name__)

app = FastAPI(
    title="PolyMind App",
    description="Fast modern AI service framework",
    lifespan=lifespan,
)


async def handle_streaming_response(
    websocket: WebSocket, user_message: str, agent_id: str
):
    """Xử lý phản hồi streaming hiệu quả"""
    await ws_connection_manager.send_personal_message(
        json.dumps({"type": "ai_typing", "agent": agent_id}), websocket
    )

    agent = agent_manager.get_agent(agent_id)
    if not agent:
        logger.error(f"❌ Agent '{agent_id}' not available")
        await ws_connection_manager.send_personal_message(
            json.dumps(
                {
                    "type": "error",
                    "content": f"Agent '{agent_id}' not available",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            websocket,
        )
        return

    total_length = 0
    try:
        stream = await agent.stream_chat(user_message)
        async for chunk in stream:
            total_length += len(chunk)
            await ws_connection_manager.send_personal_message(
                json.dumps({"type": "ai_chunk", "content": chunk, "agent": agent_id}),
                websocket,
            )
    except Exception as e:
        logger.error(f"❌ Streaming error for agent '{agent_id}': {str(e)}")
        await ws_connection_manager.send_personal_message(
            json.dumps(
                {
                    "type": "error",
                    "content": f"Processing error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            websocket,
        )
        return

    # Gửi final response
    await ws_connection_manager.send_personal_message(
        json.dumps(
            {
                "type": "ai_response_complete",
                "timestamp": datetime.now().isoformat(),
                "agent": agent_id,
                "total_length": total_length,
            }
        ),
        websocket,
    )
    logger.info(f"✅ Streaming completed for '{agent_id}' - {total_length} chars")


async def handle_regular_response(
    websocket: WebSocket, user_message: str, agent_id: str
):
    """Xử lý phản hồi thông thường"""
    try:
        response = await agent_manager.chat(user_message, agent_id)
        await ws_connection_manager.send_personal_message(
            json.dumps(
                {
                    "type": "ai_response",
                    "content": response.content,
                    "timestamp": datetime.now().isoformat(),
                    "agent": agent_id,
                    "model": response.model_name,
                }
            ),
            websocket,
        )
        logger.info(
            f"✅ Regular response for '{agent_id}' using '{response.model_name}' - {len(response.content)} chars"
        )
    except Exception as e:
        logger.error(f"❌ Regular response error for '{agent_id}': {str(e)}")
        await ws_connection_manager.send_personal_message(
            json.dumps(
                {
                    "type": "error",
                    "content": f"Processing error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            websocket,
        )


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await ws_connection_manager.connect(websocket)
    agent_id = "deepseek"  # Default value

    try:
        while True:
            data = await websocket.receive_text()

            # Giới hạn kích thước message
            if len(data) > 10240:
                await ws_connection_manager.send_personal_message(
                    json.dumps(
                        {"type": "error", "content": "Message too large (max 10KB)"}
                    ),
                    websocket,
                )
                continue

            try:
                message_data = json.loads(data)
                user_message = message_data.get("content", "")
                agent_id = message_data.get("agent", "deepseek")
                is_streaming = message_data.get("streaming", False)

                # Log incoming message
                logger.info(
                    f"💬 Received message for agent '{agent_id}' (streaming: {is_streaming}): {user_message[:100]}{'...' if len(user_message) > 100 else ''}"
                )

                if is_streaming:
                    await handle_streaming_response(websocket, user_message, agent_id)
                else:
                    await handle_regular_response(websocket, user_message, agent_id)

            except json.JSONDecodeError:
                await ws_connection_manager.send_personal_message(
                    json.dumps({"type": "error", "content": "Invalid JSON format"}),
                    websocket,
                )

    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket client disconnected for agent '{agent_id}'")
    except Exception as e:
        logger.error(f"❌ WebSocket error for agent '{agent_id}': {str(e)}")
    finally:
        await ws_connection_manager.disconnect(websocket)


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
