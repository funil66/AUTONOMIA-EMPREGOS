"""
Testes Unitários dos Formatadores e Mensagens (Pilar E)
"""
import uuid
import pytest
from core.schemas import JobOfferBase, MatchResult, CandidateProfileSchema
from notifications.formatters import NotificationFormatter


def test_whatsapp_job_alert_formatting():
    job = JobOfferBase(
        platform_source="linkedin",
        job_title="Advogado Bancário Remoto",
        company_name="Banco Digital X",
        location_text="Remoto",
        modality="remote",
        salary_text="R$ 14.000",
        description="Contencioso estratégico e contratos.",
        apply_url="https://linkedin.com/jobs/view/999"
    )
    match = MatchResult(
        job_offer_id=uuid.uuid4(),
        subscriber_id=uuid.uuid4(),
        match_score=92,
        reasons=["Compatibilidade no título (+40)", "100% Remoto (+30)"],
        is_qualified=True
    )
    
    msg = NotificationFormatter.format_whatsapp_job_alert(job, match)
    assert "92% de aderência" in msg
    assert "Advogado Bancário Remoto" in msg
    assert "Banco Digital X" in msg
    assert "🌐 100% Remoto" in msg
    assert "R$ 14.000" in msg
    assert "https://linkedin.com/jobs/view/999" in msg


def test_cover_letter_prompt_builder():
    candidate = CandidateProfileSchema(
        subscriber_id=uuid.uuid4(),
        target_roles=["Gerente Jurídico"],
        preferred_modality="remote",
        parsed_skills={"keywords": ["Contratos", "Compliance", "M&A"]}
    )
    job = JobOfferBase(
        platform_source="gupy",
        job_title="Gerente Jurídico Corporativo",
        company_name="TechCorp Brasil",
        apply_url="https://techcorp.gupy.io/job/1"
    )
    
    prompt = NotificationFormatter.build_cover_letter_prompt(candidate, job)
    assert "Gerente Jurídico" in prompt
    assert "TechCorp Brasil" in prompt
    assert "Contratos, Compliance, M&A" in prompt
    assert "ESTRUTURA OBRIGATÓRIA" in prompt
