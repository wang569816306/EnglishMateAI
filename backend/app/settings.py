from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    # 服务配置
    SERVICE_NAME: str = "FastAPI + LangChain AI 服务"
    SERVICE_VERSION: str = "1.0.0"

    # OpenAI 配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL")

    # 模型参数
    TEMPERATURE: float = 0.7
    
    # CORS 配置
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")  # 允许的源，多个用逗号分隔
    
    # 请求体大小限制（字节）
    MAX_REQUEST_SIZE: int = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 默认 1MB
    
    # API Key 认证配置
    API_KEY_ENABLED: bool = os.getenv("API_KEY_ENABLED", "false").lower() == "true"
    API_KEYS: str = os.getenv("API_KEYS", "test-key-12345,admin-key-67890")
    
    # JWT 认证配置
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 1天 = 1440分钟
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # 数据库配置
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./english_mate.db")
    
    # 视频下载配置
    MAX_DOWNLOAD_DIR_SIZE_GB: float = float(os.getenv("MAX_DOWNLOAD_DIR_SIZE_GB", "10"))  # 下载目录最大大小（GB）
    DOWNLOAD_FILE_EXPIRE_HOURS: int = int(os.getenv("DOWNLOAD_FILE_EXPIRE_HOURS", "24"))  # 文件过期时间（小时）
    MAX_CONCURRENT_DOWNLOADS: int = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "3"))  # 最大并发下载数
    DOWNLOAD_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("DOWNLOAD_RATE_LIMIT_PER_MINUTE", "10"))  # 每分钟最大下载次数


# 全局单例配置
settings = Settings()