"""
Configuration module for AI backend
Handles environment variables and application settings
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: Optional[str] = None
    langchain_project: str = "vaani-banking-assistant"
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    ollama_fast_model: str = "llama3.2:3b"
    ollama_timeout: int = 60
    ollama_num_ctx: int = 4096
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_enabled: bool = False
    
    # LLM Provider Selection
    # Options: "ollama" (local) or "openai" (cloud)
    llm_provider: str = "ollama"
    
    # Azure TTS Configuration
    azure_tts_key: Optional[str] = None
    azure_tts_region: str = "centralindia"
    azure_tts_enabled: bool = False
    
    # Database Configuration
    database_url: str = "sqlite:///./vaani_banking.db"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False
    
    # Vector Database (Qdrant)
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "banking_documents"
    qdrant_enabled: bool = False
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8001
    api_reload: bool = True
    api_workers: int = 1
    
    # Security
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Rate Limiting
    rate_limit_per_minute: int = 20
    rate_limit_per_hour: int = 100
    
    # Guardrail Settings
    enable_input_guardrails: bool = True
    enable_output_guardrails: bool = True
    guardrail_rate_limit_per_minute: int = 30
    guardrail_rate_limit_per_hour: int = 500
    guardrail_max_language_mixing_ratio: float = 0.3  # 30% mixing allowed
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/ai_backend.log"
    
    # Application Settings
    app_name: str = "Vaani Banking AI Assistant"
    app_version: str = "1.0.0"
    environment: str = "development"
    
    # Supported Languages
    supported_languages: list[str] = ["en-IN", "hi-IN", "te-IN"]
    default_language: str = "en-IN"
    
    # LLM Settings
    llm_temperature: float = 0.7
    llm_top_p: float = 0.9
    llm_max_tokens: int = 512
    
    # Voice Settings
    voice_config: dict = {
        "en-IN": "en-IN-NeerjaNeural",
        "hi-IN": "hi-IN-SwaraNeural",
        "te-IN": "te-IN-ShrutiNeural"
    }
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
