"""
Módulo de Normalização e Sanitização Determinística de Vagas
Garante que todas as vagas de diferentes portais sejam convertidas para o mesmo contrato de dados.
"""
import re
import hashlib
from typing import Tuple, Optional


class JobNormalizer:
    
    @staticmethod
    def compute_url_hash(url: str) -> str:
        """Gera um hash SHA-256 estável e único para a URL canônica da vaga."""
        # Limpa parâmetros comuns de tracking (utm, refId, trackingId, etc.)
        clean_url = re.sub(r'([?&])(utm_[^&]+|refId=[^&]+|trackingId=[^&]+|trk=[^&]+)', '', url)
        clean_url = clean_url.rstrip('?&/').strip()
        return hashlib.sha256(clean_url.encode('utf-8')).hexdigest()

    @staticmethod
    def classify_modality(title: str, location: str, description: str) -> str:
        """Classifica deterministamente a modalidade da vaga: remote, hybrid ou onsite."""
        corpus = f"{title} {location} {description}".lower()
        
        # Detecção de Remoto
        remote_tokens = [
            "remoto", "100% remoto", "totalmente remoto", "trabalho remoto", 
            "home office", "home-office", "teletrabalho", "remote", "anywhere in brazil"
        ]
        
        # Detecção de Híbrido
        hybrid_tokens = [
            "híbrido", "hibrido", "hybrid", "dias presenciais", "modelo híbrido"
        ]
        
        if any(t in corpus for t in hybrid_tokens):
            return "hybrid"
            
        if any(t in corpus for t in remote_tokens):
            return "remote"
            
        return "onsite"

    @staticmethod
    def extract_contact_email(description: str) -> Optional[str]:
        """Extrai eventuais e-mails corporativos mencionados no corpo da vaga."""
        pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        matches = re.findall(pattern, description)
        if matches:
            for email in matches:
                # Ignora e-mails genéricos de suporte de plataformas
                lower_email = email.lower()
                if not any(bad in lower_email for bad in ["noreply", "suporte@", "support@", "contato@linkedin"]):
                    return lower_email
        return None

    @staticmethod
    def sanitize_text(text: str) -> str:
        """Remove tags HTML residuais e espaços duplicados."""
        if not text:
            return ""
        clean = re.sub(r'<[^>]+>', ' ', text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
