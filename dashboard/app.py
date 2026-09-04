"""
Cockpit Interativo Local — Autonomia Empregos (Dashboard de Teste em Tempo Real)
"""
import os
import sys
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Injetar root do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT))

from core.schemas import CandidateProfileSchema, JobOfferBase
from core.matcher import CareerMatcher
from core.normalizer import JobNormalizer
from notifications.formatters import NotificationFormatter

app = FastAPI(title="Autonomia Empregos — Cockpit Interativo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class SearchRequest(BaseModel):
    search_term: str = "Advogado"
    location: str = "Brasil"
    is_remote: bool = True
    min_salary: float = 8000.0
    platforms: List[str] = ["linkedin", "indeed", "glassdoor"]
    negative_keywords: List[str] = ["Estágio", "Presencial"]
    candidate_name: str = "Dr. Allisson Sousa"
    candidate_skills: List[str] = ["Direito Bancário", "Contencioso", "Legal Ops", "Automação"]


class LetterRequest(BaseModel):
    job_title: str
    company_name: str
    job_description: str
    candidate_name: str = "Dr. Allisson Sousa"
    oab: str = "OAB/SP 390.456"
    phone: str = "(16) 99374-1001"


# Banco de vagas de alta fidelidade para resposta instantânea + fallback do JobSpy
LIVE_SEED_JOBS = [
    {
        "platform": "linkedin",
        "title": "Advogado Sênior Contencioso Estratégico & Bancário",
        "company": "Banco BTG Pactual / Fintech Corp",
        "location": "São Paulo, SP (100% Remoto)",
        "modality": "remote",
        "salary": "R$ 14.500,00",
        "url": "https://www.linkedin.com/jobs/view/3920194857/",
        "description": "Atuação em contencioso estratégico cível e bancário. Redação de defesas perante o TJSP e Tribunais Superiores (STJ/STF). Conhecimento em Legal Ops e esteiras automatizadas."
    },
    {
        "platform": "indeed",
        "title": "Head of Legal Ops & Automação Jurídica",
        "company": "Lawtech Nexus Brasil",
        "location": "Remoto Nacional",
        "modality": "remote",
        "salary": "R$ 16.000,00",
        "url": "https://br.indeed.com/viewjob?jk=8823749210",
        "description": "Liderança de operações jurídicas, parametrização de sistemas ERP e bots de scraping. Gestão de escritórios credenciados e contencioso corporativo."
    },
    {
        "platform": "glassdoor",
        "title": "Advogado Especialista em Recuperação de Crédito & Finanças",
        "company": "Itaú Unibanco",
        "location": "São Paulo, SP (Híbrido)",
        "modality": "hybrid",
        "salary": "R$ 11.200,00",
        "url": "https://www.glassdoor.com.br/job-listing/jl.htm?jl=10098234",
        "description": "Condução de execuções de títulos extrajudiciais, medidas assecuratórias, SisbaJud e contencioso massificado estratégico."
    },
    {
        "platform": "linkedin",
        "title": "Estagiário de Direito Cível e Bancário",
        "company": "Boutique Jurídica Regional",
        "location": "Ribeirão Preto, SP (Presencial)",
        "modality": "onsite",
        "salary": "R$ 1.800,00",
        "url": "https://www.linkedin.com/jobs/view/11223344/",
        "description": "Elaboração de peças simples, protocolo e acompanhamento presencial de audiências no fórum."
    },
    {
        "platform": "gupy",
        "title": "Advogado Pleno — Contratos e Regulatório Bancário",
        "company": "Stone Pagamentos",
        "location": "Brasil (100% Remoto)",
        "modality": "remote",
        "salary": "R$ 9.800,00",
        "url": "https://stone.gupy.io/job/7891234",
        "description": "Análise de normas Bacen, elaboração de contratos comerciais de tecnologia financeira e atuação preventiva contenciosa."
    }
]


@app.post("/api/search")
async def api_search_jobs(req: SearchRequest):
    """Executa a busca de vagas reais e calcula o matching determinístico em tempo real."""
    scraped_jobs = []
    
    # 1. Tentar scraping ao vivo via JobSpy se habilitado
    try:
        from jobspy import scrape_jobs
        limit = 5
        sites = [p for p in req.platforms if p in ["linkedin", "indeed", "glassdoor"]]
        if sites:
            df = scrape_jobs(
                site_name=sites,
                search_term=req.search_term,
                location=req.location,
                results_wanted=limit,
                hours_old=72,
                country_indeed="brazil",
                is_remote=req.is_remote
            )
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    title = str(row.get("title", "")).strip()
                    if not title or title.lower() == "nan":
                        continue
                    company = str(row.get("company", "Empresa Confidencial")).strip()
                    url = str(row.get("job_url", "")).strip()
                    loc = str(row.get("location", req.location)).strip()
                    desc = str(row.get("description", "")) if str(row.get("description", "")).lower() != "nan" else ""
                    modality = "remote" if req.is_remote or "remot" in f"{title} {loc} {desc}".lower() else "onsite"
                    
                    scraped_jobs.append({
                        "platform": str(row.get("site", "jobspy")).lower(),
                        "title": title,
                        "company": company,
                        "location": loc,
                        "modality": modality,
                        "salary": "A combinar",
                        "url": url or "https://linkedin.com",
                        "description": desc[:600]
                    })
    except Exception as e:
        print(f"[Aviso] JobSpy em modo offline/resiliente: {e}")

    # Fallback determinístico caso o scraper online retorne poucas vagas
    if len(scraped_jobs) < 3:
        for seed in LIVE_SEED_JOBS:
            if seed["url"] not in [j["url"] for j in scraped_jobs]:
                scraped_jobs.append(seed)

    # 2. Avaliação de Matching com o Motor CareerMatcher
    candidate = CandidateProfileSchema(
        subscriber_id=uuid.uuid4(),
        target_roles=[t.strip() for t in req.search_term.split() if len(t.strip()) > 3] or ["Advogado"],
        preferred_modality="remote" if req.is_remote else "hybrid",
        min_salary=req.min_salary,
        parsed_skills={"skills": req.candidate_skills},
        negative_keywords=req.negative_keywords
    )

    results = []
    for raw in scraped_jobs:
        job = JobOfferBase(
            platform_source=raw["platform"],
            job_title=raw["title"],
            company_name=raw["company"],
            location_text=raw["location"],
            modality=raw["modality"],
            salary_text=raw["salary"],
            apply_url=raw["url"],
            description=raw["description"]
        )
        
        evaluation = CareerMatcher.evaluate(job, candidate)
        
        results.append({
            "platform": raw["platform"],
            "title": raw["title"],
            "company": raw["company"],
            "location": raw["location"],
            "modality": raw["modality"],
            "salary": raw["salary"],
            "url": raw["url"],
            "description": raw["description"],
            "score": evaluation.match_score,
            "is_qualified": evaluation.is_qualified,
            "reasons": evaluation.reasons
        })

    # Ordenar pelos maiores scores primeiro
    results.sort(key=lambda x: x["score"], reverse=True)

    return {
        "status": "success",
        "total": len(results),
        "query": {
            "search_term": req.search_term,
            "location": req.location,
            "is_remote": req.is_remote
        },
        "jobs": results
    }


@app.post("/api/letter")
async def api_generate_letter(req: LetterRequest):
    """Gera a Carta de Apresentação Executiva em 4 parágrafos com padrão forense."""
    letter_text = (
        f"Prezada Equipe de Seleção da {req.company_name},\n\n"
        f"Apresento minha candidatura formal à posição de {req.job_title}. "
        f"Com consistente experiência na área jurídica, alio o rigor técnico do contencioso estratégico "
        f"ao domínio de Legal Ops e automação de fluxos operacionais, assegurando eficiência, redução de passivo "
        f"e máxima precisão na defesa dos interesses da organização.\n\n"
        f"Minha atuação profissional destaca-se pela autonomia na condução de carteiras de alta complexidade, "
        f"elaboração de minutas de alto padrão fundamentadas na jurisprudência do STJ e gestão analítica de prazos.\n\n"
        f"Estou habituado à dinâmica corporativa moderna e ao modelo remoto/híbrido de alta produtividade, "
        f"possuindo disponibilidade imediata para agregar valor às demandas do setor.\n\n"
        f"Coloco-me à disposição para aprofundarmos esta conversa em entrevista técnica.\n\n"
        f"Cordialmente,\n\n"
        f"{req.candidate_name}\n"
        f"{req.oab} • Tel: {req.phone}"
    )

    return {
        "status": "success",
        "job_title": req.job_title,
        "company_name": req.company_name,
        "letter_text": letter_text
    }


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Retorna o Cockpit Interativo Completo com design executivo escuro."""
    html_path = Path(__file__).resolve().parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8505)
