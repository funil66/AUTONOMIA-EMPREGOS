"""
Testes Unitários do Normalizador e Sanitizador de Vagas (Pilar E)
"""
import pytest
from core.normalizer import JobNormalizer


def test_url_hash_stability():
    url1 = "https://linkedin.com/jobs/view/12345?refId=xyz&utm_source=feed"
    url2 = "https://linkedin.com/jobs/view/12345"
    
    hash1 = JobNormalizer.compute_url_hash(url1)
    hash2 = JobNormalizer.compute_url_hash(url2)
    
    # Ambos devem gerar o mesmo hash por conta da limpeza de query params
    assert hash1 == hash2
    assert len(hash1) == 64


def test_classify_modality_remote():
    mod = JobNormalizer.classify_modality(
        title="Desenvolvedor Python",
        location="Brasil",
        description="Trabalho 100% home office e flexível"
    )
    assert mod == "remote"


def test_classify_modality_hybrid():
    mod = JobNormalizer.classify_modality(
        title="Advogado Cível",
        location="São Paulo",
        description="Regime híbrido com 2 dias de comparecimento no escritório"
    )
    assert mod == "hybrid"


def test_classify_modality_onsite():
    mod = JobNormalizer.classify_modality(
        title="Recepcionista",
        location="Campinas - SP",
        description="Atendimento presencial ao público"
    )
    assert mod == "onsite"


def test_extract_contact_email():
    desc = "Envie seu currículo com pretensão para carreiras@empresa.com.br ou fale com nosso time."
    email = JobNormalizer.extract_contact_email(desc)
    assert email == "carreiras@empresa.com.br"


def test_sanitize_text():
    dirty = "<p>Vaga de <strong>Gerente</strong> Jurídico.&nbsp;&nbsp;Venha crescer!</p>"
    clean = JobNormalizer.sanitize_text(dirty)
    assert "<p>" not in clean
    assert "<strong>" not in clean
    assert "Gerente Jurídico." in clean
