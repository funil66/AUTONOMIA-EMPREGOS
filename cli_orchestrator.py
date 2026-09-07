#!/usr/bin/env python3
"""
Orquestrador CLI do Motor de Vagas Career SaaS
Conformidade: RPA Vagas - Estágio de Descoberta, Matching e Alertas
"""
import sys
import uuid
import time
from pathlib import Path

# Fix python path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.schemas import CandidateProfileSchema, JobOfferBase
from core.matcher import CareerMatcher
from notifications.formatters import NotificationFormatter
from notifications.dispatcher import dispatcher
from adapters.mock_adapter import MockJobAdapter
from adapters.jobspy_adapter import JobSpyAdapter

def run_pipeline(send_alerts: bool = False, force_mock: bool = False):
    print("================================================================================")
    print("🤖 JARVIS RPA VAGAS CAREER SAAS - ORQUESTRADOR PIPELINE V1.0")
    print("================================================================================\n")
    
    # 1. Carregar Perfil Canônico do Titular (conforme manual em docs/04_OPERACAO_ADVOCACIA/MANUAL_CANONICO_RPA_VAGAS_E_CARREIRA.md)
    print("👤 A carregar Perfil de Candidatura Central (Dr. Allisson Sousa)...")
    profile = CandidateProfileSchema(
        subscriber_id=uuid.uuid4(),
        full_name="Allisson Gonçalves de Sousa",
        contact_phone="5516993741001",
        target_roles=[
            "Advogado Sênior", 
            "Advogado Contencioso", 
            "Advogado Bancário", 
            "Legal Ops",
            "Coordenador Jurídico"
        ],
        parsed_skills={
            "keywords": [
                "Contencioso Cível", "Fraudes Digitais", "PIX", 
                "Superendividamento", "Legal Ops", "Jurimetria"
            ]
        },
        preferred_modality="REMOTE",
        negative_keywords=["Estágio", "Trainee", "Júnior", "Assistente"]
    )
    
    # 2. Varredura via Adaptadores
    print("🔍 Iniciando varredura multicanal [MockBoard Adapter ativo]...")

    if force_mock:
        adapter = MockJobAdapter()
        print("🔍 Iniciando varredura multicanal [MockBoard Adapter ativo]...")
    else:
        adapter = JobSpyAdapter(platform="linkedin")
        print("🔍 Iniciando varredura multicanal [JobSpy LinkedIn Adapter ativo]...")

    job_offers = adapter.search(search_term="Advogado Sênior", location="Brasil", limit=10)
    print(f"  ✅ Encontradas {len(job_offers)} novas oportunidades.\n")
    
    # 3. Processamento & Matching Determinístico
    print("🧠 Submetendo oportunidades ao Evaluator Engine (ATS)...")
    qualified_matches = []
    
    for job in job_offers:
        print(f"\n  Avaliação: {job.job_title} | {job.company_name} | Modalidade: {job.modality}")
        result = CareerMatcher.evaluate(job, profile)
        print(f"  Score: {result.match_score}% -> {'✅ APROVADA' if result.is_qualified else '❌ DESCARTADA'}")
        
        for reason in result.reasons:
            print(f"    - {reason}")
            
        if result.is_qualified:
            qualified_matches.append((job, result))
            
    print(f"\n================================================================================")
    print(f"🎯 Total de Vagas Qualificadas: {len(qualified_matches)}/{len(job_offers)}")
    print(f"================================================================================")
    
    # 4. Despacho & Workflow N8N/Notificações
    if not qualified_matches:
        print("  😴 Nenhuma oportunidade cruzou a nota de corte (Tier 1 > 70%). Sistema em repouso.")
        return
        
    print("\n🚀 Despachando alertas e triggers de candidatura (Tier 1)...")
    for job, match in qualified_matches:
        if send_alerts:
            # WhatsApp
            wpp_msg = NotificationFormatter.format_whatsapp_job_alert(job, match)
            dispatcher.send_whatsapp_message(profile.contact_phone, wpp_msg)
            
            # Telegram
            tg_msg = NotificationFormatter.format_telegram_job_alert(job, match)
            dispatcher.send_telegram_alert(tg_msg)
            
            time.sleep(1) # Rate limit safe
        else:
            print(f"  ℹ️  (DRY-RUN) Simulando envio WPP e Telegram para: {job.job_title}")
            print("  [Payload Carta Prompt]:")
            print(NotificationFormatter.build_cover_letter_prompt(profile, job))
            print("-" * 50)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Career SaaS Orchestrator Job")
    parser.add_argument("--mock", action="store_true", help="Força uso de mock dados.")
    parser.add_argument("--send-alerts", action="store_true", help="Realmente despacha mensagens HTTP para Evolution e Telegram.")
    args = parser.parse_args()
    
    run_pipeline(args.send_alerts, args.mock)
