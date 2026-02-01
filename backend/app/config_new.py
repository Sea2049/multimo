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
    # SECRET_KEY 不再使用硬编码默认值，需要在环境变量中配置或由系统自动生成
    SECRET_KEY: str = ""
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
    
    # Zep 图谱服务配置（使用专用的 Zep Cloud API Key）
    ZEP_API_KEY: Optional[str] = None
    ZEP_API_TIMEOUT: int = 60  # Zep API 调用超时（秒），默认 60 秒
    
    # 存储配置
    STORAGE_TYPE: str = "memory"  # 可选: memory, database
    DATABASE_URL: Optional[str] = None
    DATABASE_PATH: str = "storage.db"
    # 将 tasks.db 放在 uploads/ 目录下，避免触发 Flask watchdog 重启
    TASKS_DATABASE_PATH: str = str(project_root / "backend" / "uploads" / "tasks.db")
    
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
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_MAX_AGE: int = 3600  # 预检请求缓存时间（秒）
    
    # 安全配置
    MAX_REQUEST_SIZE: int = 100 * 1024 * 1024  # 100MB
    SESSION_COOKIE_SECURE: bool = False  # 生产环境应设为 True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"
    
    # API Key 认证配置
    API_KEY_ENABLED: bool = False  # 是否启用 API Key 认证（默认关闭以保持向后兼容）
    API_KEYS: list = []  # API Key 配置列表 [{"id": "key1", "key": "xxx", "name": "Name", "permissions": []}]
    API_KEY_HEADER: str = "X-API-Key"  # API Key 请求头名称
    
    # 请求签名配置（用于高安全场景）
    SIGNATURE_ENABLED: bool = False  # 是否启用请求签名验证
    SIGNATURE_SECRET: str = "your-signature-secret-key"  # 签名密钥
    SIGNATURE_MAX_AGE: int = 300  # 签名有效期（秒）
    
    # 限流配置
    RATE_LIMIT_ENABLED: bool = True  # 是否启用请求限流
    RATE_LIMIT_STORAGE: str = "memory"  # 限流存储类型（memory/redis）
    RATE_LIMIT_REDIS_URL: Optional[str] = None  # Redis 连接 URL（可选）
    RATE_LIMIT_STRATEGY: str = "moving-window"  # 限流策略
    
    # 限流策略配置
    RATE_LIMIT_DEFAULT: str = "200/hour"  # 默认限流策略
    RATE_LIMIT_UPLOAD: str = "5/minute"  # 文件上传端点限流
    RATE_LIMIT_QUERY: str = "100/minute"  # 查询端点限流
    RATE_LIMIT_LLM: str = "10/hour"  # LLM 调用端点限流（本体生成、报告生成等）
    RATE_LIMIT_SIMULATION: str = "3/hour"  # 模拟运行端点限流
    
    # 安全响应头配置
    SECURITY_HEADERS_ENABLED: bool = True  # 是否启用安全响应头
    X_CONTENT_TYPE_OPTIONS: str = "nosniff"
    X_FRAME_OPTIONS: str = "DENY"
    X_XSS_PROTECTION: str = "1; mode=block"
    REFERRER_POLICY: str = "strict-origin-when-cross-origin"
    CONTENT_SECURITY_POLICY: str = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.openai.com https://*.openai.azure.com;"
    
    class Config:
        """Pydantic 配置"""
        env_file = str(env_file)
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略额外的环境变量（用于兼容旧的 .env 文件）
    
    def __init__(self, **kwargs):
        """初始化配置"""
        import secrets
        
        super().__init__(**kwargs)
        
        # SECRET_KEY 安全处理：
        # - 如果已配置（非空），直接使用
        # - 如果未配置且为开发模式，自动生成随机密钥
        # - 如果未配置且为生产模式，抛出异常
        if not self.SECRET_KEY:
            if self.DEBUG:
                # 开发环境自动生成随机密钥
                self.SECRET_KEY = secrets.token_hex(32)
            else:
                # 生产环境必须配置 SECRET_KEY
                raise ValueError(
                    "SECRET_KEY must be set in production environment. "
                    "Please set SECRET_KEY in your .env file or environment variables."
                )
        
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        directories = [
            self.UPLOAD_FOLDER,
            self.SIMULATION_DATA_DIR,
            self.LOG_DIR,
            str(Path(self.TASKS_DATABASE_PATH).parent)
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
        
        # 生产环境必须配置 SECRET_KEY
        if not self.DEBUG and not self.SECRET_KEY:
            errors.append("生产环境必须配置 SECRET_KEY")
        
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
            "max_age": self.CORS_MAX_AGE,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "headers": ["Content-Type", "Authorization", "X-API-Key"]
        }
    
    def get_security_headers(self) -> dict:
        """获取安全响应头配置
        
        Returns:
            安全响应头字典
        """
        return {
            "X-Content-Type-Options": self.X_CONTENT_TYPE_OPTIONS,
            "X-Frame-Options": self.X_FRAME_OPTIONS,
            "X-XSS-Protection": self.X_XSS_PROTECTION,
            "Referrer-Policy": self.REFERRER_POLICY,
            "Content-Security-Policy": self.CONTENT_SECURITY_POLICY if not self.DEBUG else None
        }
    
    def get_rate_limit_config(self) -> dict:
        """获取限流配置字典
        
        Returns:
            限流配置字典
        """
        return {
            "enabled": self.RATE_LIMIT_ENABLED,
            "storage": self.RATE_LIMIT_STORAGE,
            "redis_url": self.RATE_LIMIT_REDIS_URL,
            "strategy": self.RATE_LIMIT_STRATEGY,
            "default": self.RATE_LIMIT_DEFAULT,
            "upload": self.RATE_LIMIT_UPLOAD,
            "query": self.RATE_LIMIT_QUERY,
            "llm": self.RATE_LIMIT_LLM,
            "simulation": self.RATE_LIMIT_SIMULATION
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
