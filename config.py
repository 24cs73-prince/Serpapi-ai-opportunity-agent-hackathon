"""
OpportunityIQ — Configuration Management

Loads environment variables and provides typed configuration
for all application components.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_PROJECT_ROOT = Path(__file__).parent
load_dotenv(_PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class SerpApiConfig:
    """SerpApi configuration."""
    api_key: str = ""
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class LLMConfig:
    """LLM provider configuration."""
    provider: str = "gemini"
    api_key: str = ""
    model_name: str = "gemini-2.0-flash"
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass(frozen=True)
class AppConfig:
    """Application-wide configuration."""
    app_name: str = "OpportunityIQ"
    app_tagline: str = "Discover. Verify. Analyze. Act."
    version: str = "0.1.0"
    
    # Sub-configs
    serpapi: SerpApiConfig = field(default_factory=SerpApiConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    
    # File upload limits
    max_upload_size_mb: int = 10
    allowed_file_types: tuple = (".pdf", ".docx", ".txt")
    
    # Matching weights (configurable)
    match_weight_skills: float = 0.50
    match_weight_experience: float = 0.20
    match_weight_education: float = 0.10
    match_weight_location: float = 0.10
    match_weight_preferences: float = 0.10

    def has_serpapi_key(self) -> bool:
        return self.serpapi.is_configured

    def has_llm_key(self) -> bool:
        return self.llm.is_configured

    @property
    def SERPAPI_API_KEY(self) -> str:
        return self.serpapi.api_key

    @property
    def LLM_PROVIDER(self) -> str:
        return self.llm.provider

    @property
    def LLM_API_KEY(self) -> str:
        return self.llm.api_key

    @property
    def MODEL_NAME(self) -> str:
        return self.llm.model_name


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    return AppConfig(
        serpapi=SerpApiConfig(
            api_key=os.getenv("SERPAPI_API_KEY", ""),
        ),
        llm=LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "gemini"),
            api_key=os.getenv("LLM_API_KEY", ""),
            model_name=os.getenv("MODEL_NAME", "gemini-2.0-flash"),
        ),
    )


# Singleton config instance
config = load_config()

def get_config() -> AppConfig:
    """Helper function to return AppConfig singleton."""
    return config
