"""
Testes Unitários do Motor de Matching de Vagas (Pilar E)
"""
import uuid
import pytest
from core.schemas import JobOfferBase, CandidateProfileSchema
from core.matcher import CareerMatcher


@pytest.fixture
def senior_candidate_profile():
    return CandidateProfileSchema(
        subscriber_id=uuid.uuid4(),
        target_roles=["Advogado Sênior", "Gerente Jurídico", "Head of Legal"],
        preferred_modality="remote",
        min_salary=10000.0,
        parsed_skills={
            "keywords": ["bancário", "contencioso", "contratos", "LGPD"]
        },
        negative_keywords=["estágio", "estagio", "júnior", "junior"]
    )


def test_matcher_high_qualification(senior_candidate_profile):
    job = JobOfferBase(
        platform_source="linkedin",
        job_title="Advogado Sênior Contencioso Bancário",
        company_name="Fintech S.A.",
        location_text="Remoto",
        modality="remote",
        description="Especialista em bancário, contencioso e contratos. 100% home office.",
        apply_url="https://linkedin.com/jobs/view/100"
    )
    
    result = CareerMatcher.evaluate(job, senior_candidate_profile)
    assert result.is_qualified is True
    assert result.match_score >= 80
    assert "Compatibilidade exata no título" in result.reasons[0]


def test_matcher_negative_keyword_hard_veto(senior_candidate_profile):
    job = JobOfferBase(
        platform_source="indeed",
        job_title="Estágio em Direito",
        company_name="Escritório XYZ",
        location_text="Remoto",
        modality="remote",
        description="Auxiliar na redação de peças cíveis.",
        apply_url="https://indeed.com/jobs/view/200"
    )
    
    result = CareerMatcher.evaluate(job, senior_candidate_profile)
    assert result.is_qualified is False
    assert result.match_score == 0
    assert "Desqualificado: termo proibido" in result.reasons[0]


def test_matcher_modality_mismatch_penalty(senior_candidate_profile):
    job = JobOfferBase(
        platform_source="indeed",
        job_title="Advogado Sênior Cível",
        company_name="Banca Tradicional",
        location_text="Curitiba - PR",
        modality="onsite",
        description="Presencial no centro de Curitiba.",
        apply_url="https://indeed.com/jobs/view/300"
    )
    
    result = CareerMatcher.evaluate(job, senior_candidate_profile)
    # Sem a pontuação de remoto (30 pontos a menos), o score não deve atingir qualificação máxima
    assert result.match_score < 70
    assert result.is_qualified is False
