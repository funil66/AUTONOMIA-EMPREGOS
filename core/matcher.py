"""
Motor de Avaliação e Ponderação de Vagas (Deterministic Matching Engine)
Calcula a aderência do candidato (0 a 100%) sem alucinações e com penalidade estrita para termos negativos.
"""
import uuid
from typing import List, Tuple
from .schemas import JobOfferBase, CandidateProfileSchema, MatchResult
from .config import settings


class CareerMatcher:

    @classmethod
    def evaluate(cls, job: JobOfferBase, profile: CandidateProfileSchema, job_id: uuid.UUID = None) -> MatchResult:
        """
        Avalia uma vaga contra o perfil de um candidato e gera um score determinístico.
        """
        job_id = job_id or uuid.uuid4()
        score = 0
        reasons: List[str] = []
        
        job_title_lower = job.job_title.lower()
        job_desc_lower = job.description.lower()
        full_corpus = f"{job_title_lower} {job_desc_lower}"

        # 1. Filtro Excludente de Palavras-Chave Negativas (Hard Veto)
        for bad_word in profile.negative_keywords:
            if bad_word.lower() in full_corpus:
                return MatchResult(
                    job_offer_id=job_id,
                    subscriber_id=profile.subscriber_id,
                    match_score=0,
                    reasons=[f"Desqualificado: termo proibido identificado ('{bad_word}')"],
                    is_qualified=False
                )

        # 2. Compatibilidade de Cargo (Peso: 40 pontos)
        role_matched = False
        for target in profile.target_roles:
            target_clean = target.lower().strip()
            if target_clean in job_title_lower:
                score += 40
                reasons.append(f"Compatibilidade exata no título: '{target}' (+40)")
                role_matched = True
                break
            elif target_clean in job_desc_lower:
                score += 20
                reasons.append(f"Cargo mencionado no corpo da vaga: '{target}' (+20)")
                role_matched = True
                break
                
        if not role_matched:
            reasons.append("Cargo principal não identificado no título")

        # 3. Compatibilidade de Modalidade (Peso: 30 pontos)
        pref = profile.preferred_modality.lower()
        job_mod = job.modality.lower()
        
        if pref == "remote":
            if job_mod == "remote":
                score += 30
                reasons.append("Modalidade 100% remota confirmada (+30)")
            elif job_mod == "hybrid":
                score += 10
                reasons.append("Modalidade híbrida parcial (+10)")
            else:
                reasons.append("Vaga presencial (candidato prefere remoto)")
        elif pref in ["hybrid", "any"]:
            score += 30
            reasons.append(f"Modalidade aceita ({job_mod}) (+30)")
        elif pref == "onsite":
            if job_mod == "onsite":
                score += 30
                reasons.append("Vaga presencial compatível (+30)")

        # 4. Compatibilidade de Competências / Skills (Peso: 30 pontos)
        skills_dict = profile.parsed_skills or {}
        required_skills = skills_dict.get("keywords", [])
        if required_skills:
            matched_skills = [s for s in required_skills if s.lower() in full_corpus]
            if matched_skills:
                skill_ratio = len(matched_skills) / len(required_skills)
                skill_points = int(round(skill_ratio * 30))
                score += skill_points
                reasons.append(f"Skills identificadas ({len(matched_skills)}/{len(required_skills)}): {', '.join(matched_skills)} (+{skill_points})")
        else:
            # Se não houver keywords cadastradas, bonifica proporcionalmente
            score += 15
            reasons.append("Critério de skills genérico aplicado (+15)")

        final_score = min(100, max(0, score))
        is_qualified = final_score >= settings.default_match_threshold

        return MatchResult(
            job_offer_id=job_id,
            subscriber_id=profile.subscriber_id,
            match_score=final_score,
            reasons=reasons,
            is_qualified=is_qualified
        )
