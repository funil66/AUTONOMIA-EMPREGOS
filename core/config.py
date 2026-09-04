"""
Configurações Centrais do Micro-SaaS Autonomia Empregos
Conformidade: Constituição JARVIS - Pilar E (Configurações Centralizadas e Validadas)
"""
import os
from typing import List
from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "Autonomia Empregos Career Copilot"
    version: str = "1.0.0"
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "production"))
    
    # Database
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:JarvisPostgresPass2026!@localhost:5432/postgres"
        )
    )
    
    # Scoring Defaults
    default_match_threshold: int = 70
    max_daily_alerts_tier1: int = 30
    max_daily_dispatches_tier2: int = 15
    
    # Anti-Ban / Rate Limiting
    request_timeout_seconds: int = 20
    min_scrape_delay_seconds: float = 2.0
    max_scrape_delay_seconds: float = 5.0
    
    # Allowed platforms for v1.0
    supported_platforms: List[str] = [
        "linkedin",
        "indeed",
        "glassdoor",
        "gupy"
    ]


settings = Settings()
