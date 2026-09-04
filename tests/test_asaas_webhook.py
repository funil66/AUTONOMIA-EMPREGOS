"""
Testes Unitários do Webhook do Asaas (Pilar E)
"""
import pytest
from services.asaas_webhook import AsaasWebhookService


def test_asaas_payment_received_activation():
    payload = {
        "event": "PAYMENT_RECEIVED",
        "payment": {
            "id": "pay_123456",
            "customer": "cus_987654",
            "value": 97.0,
            "description": "Autonomia Empregos - Auto-Sniper Mensal",
            "customerName": "Dr. Fernando Silveira",
            "mobilePhone": "(16) 99123-4567",
            "email": "fernando@silveira.adv.br"
        }
    }
    
    result = AsaasWebhookService.process_payment_event(payload)
    assert result["status"] == "success"
    assert result["plan_tier"] == "auto_sniper"
    assert result["amount_paid"] == 97.0
    assert result["customer_phone"] == "5516991234567"
    assert result["license_token"].startswith("AE-")
    assert "Fernando" in result["onboarding_message"]


def test_asaas_event_ignored():
    payload = {
        "event": "PAYMENT_OVERDUE",
        "payment": {"id": "pay_000"}
    }
    result = AsaasWebhookService.process_payment_event(payload)
    assert result["status"] == "ignored"
