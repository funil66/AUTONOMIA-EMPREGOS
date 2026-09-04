"""
Serviço de Ingestão de Webhooks do Asaas (Raelcia Studio / Autonomia Empregos)
Processa pagamentos recebidos, ativa licenças e agenda o onboarding no WhatsApp.
"""
import uuid
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from core.schemas import JobOfferBase
from core.config import settings

logger = logging.getLogger("autonomia_empregos.asaas_webhook")


class AsaasWebhookService:

    TIER_MAPPING = {
        47.0: "radar_hunter",
        97.0: "auto_sniper",
        197.0: "executive_copilot",
        347.0: "clt_master"
    }

    @classmethod
    def resolve_plan_tier(cls, amount: float, description: str = "") -> str:
        """Determina o plano contratado pelo valor pago ou pelo texto da descrição."""
        desc_lower = description.lower()
        if "vip" in desc_lower or "master" in desc_lower or amount >= 300.0:
            return "clt_master"
        if "copilot" in desc_lower or "executive" in desc_lower or amount >= 180.0:
            return "executive_copilot"
        if "sniper" in desc_lower or amount >= 90.0:
            return "auto_sniper"
        return "radar_hunter"

    @classmethod
    def format_salutation(cls, full_name: str) -> str:
        """Formata a saudação respeitando títulos e pronomes de tratamento."""
        tokens = full_name.strip().split()
        if not tokens:
            return "Assinante"
        if tokens[0].lower() in ["dr.", "dr", "dra.", "dra"]:
            return " ".join(tokens[:2])
        return tokens[0]

    @classmethod
    def process_payment_event(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa o evento do webhook do Asaas de forma determinística e resiliente.
        """
        event = payload.get("event")
        if event not in ["PAYMENT_RECEIVED", "PAYMENT_CONFIRMED"]:
            return {
                "status": "ignored",
                "reason": f"Evento {event} não requer ativação imediata"
            }

        payment = payload.get("payment", {})
        customer = payload.get("customer", {})
        
        # Extração de Dados Financeiros
        amount = float(payment.get("value", 0.0))
        description = payment.get("description", "")
        plan_tier = cls.resolve_plan_tier(amount, description)
        
        # Extração e Limpeza do Contato
        customer_name = customer.get("name") or payment.get("customerName", "Assinante Autonomia")
        raw_phone = customer.get("mobilePhone") or customer.get("phone") or payment.get("mobilePhone", "")
        clean_phone = re.sub(r'\D', '', str(raw_phone))
        if clean_phone and not clean_phone.startswith("55"):
            clean_phone = f"55{clean_phone}"
            
        customer_email = customer.get("email") or payment.get("email", f"cliente_{clean_phone}@autonomia.app.br")

        # Geração de Chave de Licença
        license_token = f"AE-{uuid.uuid4().hex[:8].upper()}-{uuid.uuid4().hex[:4].upper()}"
        subscriber_id = str(uuid.uuid4())
        
        salutation = cls.format_salutation(customer_name)
        onboarding_msg = (
            f"Olá, {salutation}! 🎯\n\n"
            f"Seu acesso ao *Autonomia Empregos ({plan_tier.replace('_', ' ').title()})* foi ativado!\n"
            f"Chave de Licença: `{license_token}`\n\n"
            f"Eu sou a Clara, sua copiloto de carreira. Me envie aqui seu currículo em PDF para iniciarmos suas candidaturas!"
        )

        logger.info(f"Assinatura ativada com sucesso: {customer_name} ({plan_tier}) - Tel: {clean_phone}")

        return {
            "status": "success",
            "subscriber_id": subscriber_id,
            "license_token": license_token,
            "plan_tier": plan_tier,
            "amount_paid": amount,
            "customer_phone": clean_phone,
            "customer_name": customer_name,
            "onboarding_message": onboarding_msg
        }
