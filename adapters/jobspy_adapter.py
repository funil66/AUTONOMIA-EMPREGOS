"""
Adaptador JobSpy Multicanal para Autonomia Empregos
Conformidade: RPA Vagas - Estágio de Ingestão e Descoberta Multicanal (LinkedIn, Indeed, Glassdoor)
"""
import uuid
from typing import List
from jobspy import scrape_jobs
from core.schemas import JobOfferBase
from adapters.base import BaseJobAdapter
from core.config import settings

class JobSpyAdapter(BaseJobAdapter):
    platform_name: str = "jobspy_multichannel"

    def __init__(self, platform: str = "linkedin"):
        """Especifica a plataforma-alvo (linkedin, indeed, glassdoor)."""
        self.target_platform = platform

    def search(self, search_term: str, location: str = "Brasil", limit: int = 15) -> List[JobOfferBase]:
        """
        Executa a varredura multicanal utilizando a biblioteca JobSpy.
        """
        jobs_df = scrape_jobs(
            site_name=[self.target_platform],
            search_term=search_term,
            location=location,
            country_indeed="brazil",
            results_wanted=limit,
            hours_old=48, # Limite pragmático de expiração para não mandar lixo
        )
        
        job_offers = []
        
        if jobs_df is None or jobs_df.empty:
            return job_offers

        for _, row in jobs_df.iterrows():
            title = str(row.get("title", ""))
            company = str(row.get("company", ""))
            location_text = str(row.get("location", ""))
            description = str(row.get("description", ""))
            url = str(row.get("job_url", ""))
            salary = str(row.get("interval", ""))
            is_remote = bool(row.get("is_remote", False))
            
            # Ajuste de modalidade
            modality = "remote" if is_remote else "onsite"
            if "hybrid" in title.lower() or "híbrido" in title.lower() or "hybrid" in description.lower():
                modality = "hybrid"
                
            job_offer = JobOfferBase(
                platform_source=self.target_platform,
                external_job_id=str(row.get("id", uuid.uuid4())),
                job_title=title,
                company_name=company,
                location_text=location_text,
                modality=modality,
                salary_text=salary if salary and salary.lower() != "nan" else "Compatível com o mercado",
                description=description,
                apply_url=url,
                contact_email=""
            )
            job_offers.append(job_offer)
            
        return job_offers

