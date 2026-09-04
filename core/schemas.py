"""
Modelos e Schemas Canônicos Pydantic do Autonomia Empregos
Validação estrita de contratos de dados em conformidade com as tabelas do Supabase.
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class JobOfferBase(BaseModel):
    platform_source: str
    external_job_id: Optional[str] = None
    job_title: str
    company_name: str
    location_text: Optional[str] = None
    modality: str = Field(default="remote", description="remote, hybrid, onsite")
    salary_text: Optional[str] = None
    description: str = ""
    apply_url: str
    contact_email: Optional[str] = None


class JobOfferCreate(JobOfferBase):
    url_hash: str


class JobOfferInDB(JobOfferCreate):
    id: uuid.UUID
    is_active: bool = True
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CandidateProfileSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    subscriber_id: uuid.UUID
    target_roles: List[str] = Field(default_factory=list)
    preferred_modality: str = Field(default="remote")
    target_city: Optional[str] = None
    target_state: Optional[str] = None
    min_salary: Optional[float] = None
    parsed_skills: Dict[str, Any] = Field(default_factory=dict)
    negative_keywords: List[str] = Field(default_factory=list)


class MatchResult(BaseModel):
    job_offer_id: uuid.UUID
    subscriber_id: uuid.UUID
    match_score: int = Field(ge=0, le=100)
    reasons: List[str] = Field(default_factory=list)
    is_qualified: bool
