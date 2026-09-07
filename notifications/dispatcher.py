"""
Despachante de Notificações Multicanal
Conformidade: Envio de Alertas via Telegram Executivo e WhatsApp Evolution API
"""
import os
import json
import urllib.request
import urllib.error
from typing import Optional
from core.config import settings

class NotificationDispatcher:
    def __init__(self):
        # Evolution API config
        self.evolution_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8084").rstrip("/")
        self.evolution_apikey = os.getenv("EVOLUTION_API_KEY", "admin_apikey")
        self.whatsapp_instance = os.getenv("EVOLUTION_INSTANCE_NAME", "JarvisBot")
        
        # Telegram config
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "8238804651")

    def _post_json(self, url: str, payload: dict, headers: dict) -> bool:
        """Helper para disparos HTTP POST puristas."""
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status in [200, 201]
        except Exception as e:
            print(f"  [ERROR] Falha no disparo POST para {url}: {e}")
            return False

    def send_whatsapp_message(self, phone_number: str, message_text: str) -> bool:
        """Despacha mensagem via Evolution API (WhatsApp)."""
        if not phone_number.startswith("55"):
            phone_number = "55" + "".join(filter(str.isdigit, phone_number))
            
        endpoint = f"{self.evolution_url}/message/sendText/{self.whatsapp_instance}"
        payload = {
            "number": phone_number,
            "options": {
                "delay": 1200,
                "presence": "composing"
            },
            "textMessage": {
                "text": message_text
            }
        }
        headers = {
            "Content-Type": "application/json",
            "apikey": self.evolution_apikey
        }
        
        print(f"  📲 Despachando notificação WhatsApp para {phone_number}...")
        return self._post_json(endpoint, payload, headers)

    def send_telegram_alert(self, message_text: str, parse_mode: str = "HTML") -> bool:
        """Despacha alerta para canal Telegram executivo."""
        if not self.telegram_bot_token:
            print("  ⚠️ TELEGRAM_BOT_TOKEN não configurado. Alerta silencioso na tela apenas.")
            print(f"---\n{message_text}\n---")
            return False
            
        endpoint = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message_text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        headers = {"Content-Type": "application/json"}
        
        print("  ✈️ Despachando alerta via Telegram...")
        return self._post_json(endpoint, payload, headers)

dispatcher = NotificationDispatcher()
