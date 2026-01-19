# 日志工具模块

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional
from datetime import datetime


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """获取或创建日志记录器
    
    Args:
        name: 日志记录器名称（通常使用 __name__）
        level: 日志级别（logging.DEBUG, logging.INFO 等）
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(level or logging.DEBUG)
    
    # 配置格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def setup_file_logger(name: str, log_file: str, 
                     max_bytes: int = 10 * 1024 * 1024,
                     backup_count: int = 5,
                     level: Optional[int] = None) -> logging.Logger:
    """设置文件日志记录器
    
    Args:
        name: 日志记录器名称
        log_file: 日志文件路径
        max_bytes: 单个日志文件最大字节数（默认 10MB）
        backup_count: 保留的备份文件数量
        level: 日志级别
        
    Returns:
        配置好的文件日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(level or logging.DEBUG)
    
    # 创建日志目录
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 配置格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器（带轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


class LogLevel:
    """日志级别常量"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


def get_daily_logger(name: str, log_dir: str = "logs",
                     level: Optional[int] = None) -> logging.Logger:
    """获取按日期分文件的日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录
        level: 日志级别
        
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复配置
    if logger.handlers:
        return logger
    
    # 设置日志级别
    logger.setLevel(level or logging.DEBUG)
    
    # 创建日志目录
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # 生成日志文件名（按日期）
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = log_path / f"{date_str}.log"
    
    # 配置格式化器
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def set_log_level(logger: logging.Logger, level: int):
    """设置日志级别
    
    Args:
        logger: 日志记录器
        level: 日志级别
    """
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)


def log_function_call(logger: logging.Logger, level: int = logging.DEBUG):
    """装饰器：记录函数调用
    
    Args:
        logger: 日志记录器
        level: 日志级别
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"
            logger.log(level, f"调用函数: {func_name}")
            try:
                result = func(*args, **kwargs)
                logger.log(level, f"函数 {func_name} 执行成功")
                return result
            except Exception as e:
                logger.error(f"函数 {func_name} 执行失败: {e}")
                raise
        return wrapper
    return decorator


def log_execution_time(logger: logging.Logger, level: int = logging.INFO):
    """装饰器：记录函数执行时间
    
    Args:
        logger: 日志记录器
        level: 日志级别
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            func_name = f"{func.__module__}.{func.__name__}"
            
            start_time = time.time()
            logger.log(level, f"开始执行: {func_name}")
            
            try:
                result = func(*args, **kwargs)
                elapsed_time = time.time() - start_time
                logger.log(level, f"完成执行: {func_name}, 耗时: {elapsed_time:.2f}秒")
                return result
            except Exception as e:
                elapsed_time = time.time() - start_time
                logger.error(f"执行失败: {func_name}, 耗时: {elapsed_time:.2f}秒, 错误: {e}")
                raise
        return wrapper
    return decorator


class ContextLogger:
    """上下文日志记录器，支持添加上下文信息"""
    
    def __init__(self, logger: logging.Logger, context: Optional[dict] = None):
        """初始化上下文日志记录器
        
        Args:
            logger: 基础日志记录器
            context: 初始上下文信息
        """
        self.logger = logger
        self.context = context or {}
    
    def add_context(self, key: str, value: any):
        """添加上下文信息
        
        Args:
            key: 键
            value: 值
        """
        self.context[key] = value
    
    def remove_context(self, key: str):
        """移除上下文信息
        
        Args:
            key: 键
        """
        self.context.pop(key, None)
    
    def clear_context(self):
        """清空上下文信息"""
        self.context.clear()
    
    def _format_message(self, message: str) -> str:
        """格式化消息，添加上下文
        
        Args:
            message: 原始消息
            
        Returns:
            格式化后的消息
        """
        if not self.context:
            return message
        
        context_str = " | ".join([f"{k}={v}" for k, v in self.context.items()])
        return f"[{context_str}] {message}"
    
    def debug(self, message: str):
        """记录 DEBUG 级别日志"""
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str):
        """记录 INFO 级别日志"""
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str):
        """记录 WARNING 级别日志"""
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str):
        """记录 ERROR 级别日志"""
        self.logger.error(self._format_message(message))
    
    def critical(self, message: str):
        """记录 CRITICAL 级别日志"""
        self.logger.critical(self._format_message(message))
