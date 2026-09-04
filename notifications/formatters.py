"""
Formatadores Humanizados de Mensagens e Alertas
Conformidade: Padrão Executivo de Carreira e Voz Humanizada
"""
from typing import Dict, Any
from core.schemas import JobOfferBase, MatchResult, CandidateProfileSchema


class NotificationFormatter:

    @staticmethod
    def format_whatsapp_job_alert(job: JobOfferBase, match: MatchResult) -> str:
        """
        Formata o alerta executivo de vaga para o WhatsApp do assinante.
        Estilo: Conciso, claro, sem jargões robóticos.
        """
        modality_icon = "🌐 100% Remoto" if job.modality == "remote" else ("🏢 Presencial" if job.modality == "onsite" else "🔄 Modelo Híbrido")
        salary = f"💰 {job.salary_text}" if job.salary_text else "💰 Salário compatível com o mercado"
        
        reasons_summary = "\n".join([f"  • {r}" for r in match.reasons[:2]])
        
        msg = (
            f"🎯 *NOVA OPORTUNIDADE QUALIFICADA ({match.match_score}% de aderência)*\n\n"
            f"📌 *Cargo:* {job.job_title}\n"
            f"🏢 *Empresa:* {job.company_name}\n"
            f"{modality_icon}\n"
            f"{salary}\n\n"
            f"🔍 *Por que recomendo para você:*\n"
            f"{reasons_summary}\n\n"
            f"🔗 *Link direto da vaga:* {job.apply_url}\n\n"
            f"_Deseja que eu redija sua carta de apresentação para esta vaga? Responda com 'sim'_"
        )
        return msg

    @staticmethod
    def format_telegram_job_alert(job: JobOfferBase, match: MatchResult) -> str:
        """
        Formata o alerta para o Telegram Bot com suporte a formatação rica.
        """
        return (
            f"🎯 <b>Vaga Qualificada: {match.match_score}% Match</b>\n\n"
            f"💼 <b>{job.job_title}</b> na <b>{job.company_name}</b>\n"
            f"📍 Modalidade: {job.modality.upper()}\n\n"
            f"👉 <a href='{job.apply_url}'>Acessar Vaga no Portal</a>"
        )

    @staticmethod
    def build_cover_letter_prompt(candidate: CandidateProfileSchema, job: JobOfferBase) -> str:
        """
        Constrói o prompt pericial para o LLM gerar a carta no padrão canônico.
        """
        roles_text = ", ".join(candidate.target_roles)
        skills_text = ", ".join(candidate.parsed_skills.get("keywords", []))
        
        return (
            f"Você é um assessor executivo de carreira de alto padrão.\n"
            f"Redija uma carta de apresentação em 4 parágrafos executivos, direta, persuasiva e sem clichês.\n\n"
            f"DADOS DO CANDIDATO:\n"
            f"- Cargos Alvo: {roles_text}\n"
            f"- Principais Competências: {skills_text}\n\n"
            f"DADOS DA VAGA:\n"
            f"- Cargo: {job.job_title}\n"
            f"- Empresa: {job.company_name}\n"
            f"- Descrição: {job.description[:1000]}\n\n"
            f"ESTRUTURA OBRIGATÓRIA:\n"
            f"1. Abertura citando o cargo e alinhamento de propósito com a empresa.\n"
            f"2. Destaque de 2 resultados sólidos obtidos na carreira conectados à dor da vaga.\n"
            f"3. Domínio técnico das exigências e metodologia de trabalho.\n"
            f"4. Fechamento seguro convidando para uma breve conversa de 15 minutos."
        )
