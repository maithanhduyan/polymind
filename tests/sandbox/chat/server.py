import os
import json
import logging
from typing import Any, Dict
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

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
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(
            json.dumps({"sender": "system", "message": f"Server error: {str(e)}"})
        )
        await websocket.close()


def get_logging_config() -> Dict[str, Any]:
    """
    Trả về cấu hình logging với timestamp đầy đủ.

    Returns:
        Dict[str, Any]: Logging configuration dictionary
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {
                "format": "%(asctime)s | %(levelname)-8s | %(message)s",
                "datefmt": "%H:%M:%S",
            },
            "access": {
                "format": "%(asctime)s | ACCESS | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "detailed",
                "stream": "ext://sys.stdout",
            },
            "access_console": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            # Root logger
            "": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            # Uvicorn loggers
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["access_console"],
                "level": "INFO",
                "propagate": False,
            },
            # PolyMind app loggers
            "backend": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", log_config=get_logging_config(), port=8000)
