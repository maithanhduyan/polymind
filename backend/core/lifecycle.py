"""
Application Lifecycle Manager for PolyMind (Optimized)

Cải tiến chính:
1. Tích hợp hệ thống logging hiệu suất cao
2. Xử lý lifecycle chặt chẽ
3. Quản lý tài nguyên tự động
4. Xử lý lỗi toàn diện
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from ..agents.manager import agent_manager
from ..config import config
from backend.utils.logger import AsyncLoggerConfig, get_async_logger
import logging

# Khởi tạo logger với cấu hình nâng cao
logger = get_async_logger(__name__)


class LifecycleManager:
    """
    Quản lý vòng đời ứng dụng với tích hợp logging mạnh mẽ

    Cải tiến:
    - Sử dụng logger đồng bộ hiệu suất cao
    - Xử lý lỗi toàn diện
    - Đảm bảo giải phóng tài nguyên
    - Tích hợp cấu hình logging
    """

    def __init__(self):
        self._logger = logger

    async def startup(self):
        """Xử lý tác vụ khởi động ứng dụng"""
        try:
            self._logger.info("🚀 Starting PolyMind application...")

            # Cấu hình logging nâng cao
            AsyncLoggerConfig.configure_logging(
                level=logging.INFO,
                log_file_path="polymind.log",
                max_bytes=20 * 1024 * 1024,  # 20MB
                backup_count=10,
                buffer_capacity=500,
            )

            # Kiểm tra môi trường
            await self._validate_environment()

            # Khởi tạo agents
            await self._initialize_agents()

            self._logger.info("✅ Application startup completed")
        except Exception as e:
            self._logger.exception("🔥 Critical startup failure")
            raise

    async def shutdown(self):
        """Xử lý tác vụ tắt ứng dụng"""
        try:
            self._logger.info("🛑 Shutting down PolyMind application...")

            # Đóng tất cả agents
            await agent_manager.close_all()
            self._logger.info("✅ All agents closed")

            # DỪNG LOG LISTENER - QUAN TRỌNG!
            AsyncLoggerConfig.stop_listener()
            self._logger.info("✅ Logging system stopped")
        except Exception as e:
            self._logger.exception("⚠️ Graceful shutdown failed")
        finally:
            print("✅ Application shutdown completed")

    async def _validate_environment(self):
        """Kiểm tra biến môi trường và cấu hình"""
        if not config.check_required_env():
            msg = "⚠️ Missing environment variables - Some features may be disabled"
            self._logger.warning(msg)
            print(msg)
        else:
            self._logger.info("✅ Environment validation passed")

    async def _initialize_agents(self):
        """Khởi tạo và cấu hình agents"""
        try:
            await agent_manager.setup_default_agents()
            self._logger.info("✅ Agent system initialized")
        except Exception as e:
            self._logger.error(f"❌ Agent initialization failed: {str(e)}")
            raise


# Global lifecycle manager instance
lifecycle_manager = LifecycleManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Quản lý vòng đời FastAPI với xử lý lỗi toàn diện

    Cải tiến:
    - Bọc toàn bộ lifecycle trong try-finally
    - Xử lý exception chi tiết
    - Đảm bảo giải phóng tài nguyên
    """
    try:
        await lifecycle_manager.startup()
        yield
    except Exception as e:
        logger.exception("💀 Fatal error in application lifespan")
        raise
    finally:
        await lifecycle_manager.shutdown()
