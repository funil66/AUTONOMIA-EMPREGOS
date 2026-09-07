"""
Adaptador Mock Determinístico para Testes Unitários e Quality Gates
"""
from typing import List
from .base import BaseJobAdapter
from core.schemas import JobOfferBase


class MockJobAdapter(BaseJobAdapter):
    platform_name: str = "mock_board"

    def search(self, search_term: str, location: str = "Brasil", limit: int = 15) -> List[JobOfferBase]:
        return [
            JobOfferBase(
                platform_source="mock_board",
                external_job_id="mock-001",
                job_title="Advogado Sênior Contencioso Bancário",
                company_name="Fintech Brasil Pagamentos S.A.",
                location_text="Remoto - Brasil",
                modality="remote",
                salary_text="R$ 12.000 a R$ 15.000",
                description="Buscamos advogado especialista em contencioso cível e bancário, contratos e LGPD. Trabalho 100% home office. Contato: rh@fintechbrasil.com.br",
                apply_url="https://fintechbrasil.com.br/vagas/advogado-senior",
                contact_email="rh@fintechbrasil.com.br"
            ),
            JobOfferBase(
                platform_source="mock_board",
                external_job_id="mock-002",
                job_title="Estágio em Direito",
                company_name="Banca de Advocacia Geral",
                location_text="São Paulo - SP",
                modality="onsite",
                salary_text="R$ 1.500",
                description="Vaga para estudantes do 2º ao 4º ano de direito. Presencial.",
                apply_url="https://bancageral.com.br/vagas/estagio",
                contact_email=None
            )
        ]
