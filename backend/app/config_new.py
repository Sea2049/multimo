"""
配置管理
统一从项目根目录的 .env 文件加载配置
重构版本：移除对第三方受版权保护的依赖
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


# 加载项目根目录的 .env 文件
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
    load_dotenv(env_file)
else:
    # 如果根目录没有 .env，尝试加载环境变量（用于生产环境）
    load_dotenv()


class AppConfig(BaseSettings):
    """应用配置类
    
    使用 Pydantic 进行配置验证和类型转换
    """
    
    # Flask 配置
    SECRET_KEY: str = "mirofish-secret-key"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 5001
    
    # JSON 配置 - 禁用 ASCII 转义，让中文直接显示
    JSON_AS_ASCII: bool = False
    
    # LLM 配置（统一使用 OpenAI 格式的任意 LLM）
    LLM_API_KEY: str
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL_NAME: str = "gpt-4o-mini"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT: int = 300  # LLM 调用超时（秒），默认 5 分钟
    
    # 存储配置
    STORAGE_TYPE: str = "memory"  # 可选: memory, database
    DATABASE_URL: Optional[str] = None
    DATABASE_PATH: str = "storage.db"
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_FOLDER: str = str(project_root / "backend" / "uploads")
    ALLOWED_EXTENSIONS: set = {"pdf", "md", "txt", "markdown"}
    
    # 文本处理配置
    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_CHUNK_OVERLAP: int = 50
    
    # 模拟配置（重构后的实现）
    DEFAULT_SIMULATION_ROUNDS: int = 10
    MAX_AGENTS: int = 100
    SIMULATION_DATA_DIR: str = str(project_root / "backend" / "uploads" / "simulations")
    
    # 平台可用动作配置（重构后的实现）
    TWITTER_ACTIONS: list = [
        "create_post", "like_post", "repost", "follow", "do_nothing", "quote_post"
    ]
    REDDIT_ACTIONS: list = [
        "like_post", "dislike_post", "create_post", "create_comment",
        "like_comment", "dislike_comment", "search_posts", "search_user",
        "trend", "refresh", "do_nothing", "follow", "mute"
    ]
    
    # 报告生成配置（重构后的实现）
    REPORT_MAX_TOOL_CALLS: int = 5
    REPORT_MAX_REFLECTION_ROUNDS: int = 2
    REPORT_TEMPERATURE: float = 0.5
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = str(project_root / "backend" / "logs")
    LOG_FILE_ROTATION_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # 安全配置
    MAX_REQUEST_SIZE: int = 100 * 1024 * 1024  # 100MB
    SESSION_COOKIE_SECURE: bool = False  # 生产环境应设为 True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    class Config:
        """Pydantic 配置"""
        env_file = str(env_file)
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量（用于兼容旧的 .env 文件）
    
    def __init__(self, **kwargs):
        """初始化配置"""
        super().__init__(**kwargs)
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.UPLOAD_FOLDER,
            self.SIMULATION_DATA_DIR,
            self.LOG_DIR
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def validate_required_fields(self) -> list[str]:
        """验证必填字段
        
        Returns:
            错误消息列表，空列表表示验证通过
        """
        errors = []
        
        if not self.LLM_API_KEY:
            errors.append("LLM_API_KEY 未配置")
        
        if not self.LLM_BASE_URL:
            errors.append("LLM_BASE_URL 未配置")
        
        if not self.LLM_MODEL_NAME:
            errors.append("LLM_MODEL_NAME 未配置")
        
        return errors
    
    def get_llm_config(self) -> dict:
        """获取 LLM 配置字典
        
        Returns:
            LLM 配置字典
        """
        return {
            "api_key": self.LLM_API_KEY,
            "base_url": self.LLM_BASE_URL,
            "model_name": self.LLM_MODEL_NAME,
            "temperature": self.LLM_TEMPERATURE,
            "max_tokens": self.LLM_MAX_TOKENS,
            "timeout": self.LLM_TIMEOUT
        }
    
    def get_flask_config(self) -> dict:
        """获取 Flask 配置字典
        
        Returns:
            Flask 配置字典
        """
        return {
            "SECRET_KEY": self.SECRET_KEY,
            "DEBUG": self.DEBUG,
            "JSON_AS_ASCII": self.JSON_AS_ASCII,
            "MAX_CONTENT_LENGTH": self.MAX_UPLOAD_SIZE,
            "UPLOAD_FOLDER": self.UPLOAD_FOLDER,
            "SESSION_COOKIE_SECURE": self.SESSION_COOKIE_SECURE,
            "SESSION_COOKIE_HTTPONLY": self.SESSION_COOKIE_HTTPONLY,
            "SESSION_COOKIE_SAMESITE": self.SESSION_COOKIE_SAMESITE
        }
    
    def get_cors_config(self) -> dict:
        """获取 CORS 配置字典
        
        Returns:
            CORS 配置字典
        """
        return {
            "origins": self.CORS_ORIGINS,
            "allow_credentials": self.CORS_ALLOW_CREDENTIALS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "headers": ["Content-Type", "Authorization"]
        }
    
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.DEBUG
    
    def is_production(self) -> bool:
        """是否为生产环境"""
        return not self.DEBUG


# 创建全局配置实例
config = AppConfig()


def get_config() -> AppConfig:
    """获取全局配置实例
    
    Returns:
        配置实例
    """
    return config


def validate_config() -> list[str]:
    """验证配置
    
    Returns:
        错误消息列表
    """
    return config.validate_required_fields()


if __name__ == "__main__":
    # 测试配置加载
    print("=== Multimo 配置信息 ===")
    print(f"调试模式: {config.DEBUG}")
    print(f"LLM 模型: {config.LLM_MODEL_NAME}")
    print(f"LLM 基础 URL: {config.LLM_BASE_URL}")
    print(f"存储类型: {config.STORAGE_TYPE}")
    print(f"上传文件夹: {config.UPLOAD_FOLDER}")
    print(f"模拟数据目录: {config.SIMULATION_DATA_DIR}")
    print(f"日志目录: {config.LOG_DIR}")
    
    # 验证配置
    errors = validate_config()
    if errors:
        print("\n⚠️  配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("\n✅ 配置验证通过")
