# Cấu trúc Dự án như sau:

```
..\polymind
├── pyproject.toml
├── src
│   ├── __init__.py
│   ├── adapters
│   │   └── .gitkeep
│   ├── agents
│   │   └── .gitkeep
│   ├── config.py
│   ├── main.py
│   └── services
│       └── health.py
└── uv.lock
```

# Danh sách chi tiết các file:

## File ..\polymind\src\config.py:
```python

```

## File ..\polymind\src\main.py:
```python
from fastapi import FastAPI
from src.services.health import router as health_router

app = FastAPI(title="FlashPy App")

app.include_router(health_router)

@app.get("/")
async def root():
    return {"status": "ok"}

```

## File ..\polymind\src\__init__.py:
```python

```

## File ..\polymind\src\services\health.py:
```python
# src/services/health.py
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": "2025-06-20T...",
        "version": "1.0.0"
    }

@router.get("/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "database": "connected",
        "memory_usage": "45%",
        "uptime": "2h 30m"
    }
```

