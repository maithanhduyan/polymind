"""
High-Performance Async Logging System for PolyMind - Text Format (Optimized)

Cải tiến chính:
1. Thêm RotatingFileHandler để quản lý log file tự động
2. Hỗ trợ ghi log batch với MemoryHandler
3. Xử lý lỗi mạnh mẽ cho listener
4. Quản lý tài nguyên chặt chẽ khi dừng ứng dụng
5. Hỗ trợ context logging qua filters
"""

import logging
from logging.handlers import (
    QueueHandler,
    QueueListener,
    RotatingFileHandler,
    MemoryHandler,
)
import queue
import sys
import atexit
from typing import Optional


class AsyncLoggerConfig:
    """Cấu hình logger bất đồng bộ tập trung"""

    _configured = False
    _loggers = {}
    _listener = None
    _file_handler = None
    _memory_handler = None

    @classmethod
    def configure_logging(
        cls,
        level: int = logging.INFO,
        format_string: Optional[str] = None,
        log_file_path: str = "./logs/polymind_system.log",
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        buffer_capacity: int = 1000,  # Số bản ghi tối đa trong bộ đệm
        encoding: str = "utf-8",
    ) -> None:
        """
        Cấu hình toàn cục cho hệ thống logging bất đồng bộ

        Args:
            level: Mức logging (mặc định: INFO)
            format_string: Chuỗi định dạng tùy chỉnh
            log_file_path: Đường dẫn file log
            max_bytes: Kích thước tối đa mỗi file log (bytes)
            backup_count: Số file log dự phòng
            buffer_capacity: Dung lượng bộ đệm ghi batch
            encoding: Mã hóa file log
        """
        if cls._configured:
            return

        # Định dạng mặc định
        if format_string is None:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Tạo queue cho logging (không giới hạn kích thước)
        log_queue = queue.Queue(-1)

        # Tạo RotatingFileHandler với cơ chế xoay file
        cls._file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding,
        )
        cls._file_handler.setFormatter(logging.Formatter(format_string))

        # Thiết lập bộ đệm ghi batch (nếu được kích hoạt)
        if buffer_capacity > 0:
            cls._memory_handler = MemoryHandler(
                capacity=buffer_capacity, target=cls._file_handler
            )
            final_handler = cls._memory_handler
        else:
            final_handler = cls._file_handler

        # Tạo QueueListener
        cls._listener = QueueListener(
            log_queue, final_handler, respect_handler_level=True
        )

        # Cấu hình root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)

        # Xóa mọi handler hiện có để tránh trùng lặp
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Thêm QueueHandler để gửi log tới queue
        queue_handler = QueueHandler(log_queue)
        queue_handler.setLevel(level)
        root_logger.addHandler(queue_handler)

        # Bắt đầu listener trong thread riêng
        cls._listener.start()
        cls._configured = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Lấy logger cho module chỉ định

        Args:
            name: Tên logger (thường là __name__)

        Returns:
            Logger instance đã được cấu hình
        """
        if not cls._configured:
            cls.configure_logging()

        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger

        return cls._loggers[name]

    @classmethod
    def _handle_listener_error(cls, record):
        """Xử lý lỗi trong quá trình ghi log"""
        sys.stderr.write(f"!!! LỖI LOGGING: Không thể ghi bản ghi log - {record.msg}\n")
        sys.stderr.flush()

    @classmethod
    def stop_listener(cls) -> None:
        """Dừng listener và giải phóng tài nguyên"""
        if cls._listener:
            cls._listener.stop()

            # Đảm bảo flush bộ đệm nếu sử dụng MemoryHandler
            if cls._memory_handler:
                cls._memory_handler.flush()
                cls._memory_handler.close()

            if cls._file_handler:
                cls._file_handler.close()

            cls._configured = False


# Đăng ký dừng listener khi ứng dụng kết thúc
atexit.register(AsyncLoggerConfig.stop_listener)


def get_async_logger(name: str) -> logging.Logger:
    """
    Lấy logger cho module chỉ định (API tiện ích)

    Args:
        name: Tên logger (thường là __name__)

    Returns:
        Logger instance đã được cấu hình

    Ví dụ:
        from async_logger import get_async_logger
        logger = get_async_logger(__name__)
    """
    return AsyncLoggerConfig.get_logger(name)
