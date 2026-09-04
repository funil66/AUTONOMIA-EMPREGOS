-- ==============================================================================
-- Schema DDL: AUTONOMIA EMPREGOS (SaaS de Carreira & Vagas)
-- Repositório: funil66/AUTONOMIA-EMPREGOS
-- Banco de Dados: PostgreSQL 15+ (Supabase)
-- Data de Criação: 2026-09-03
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Tabela de Assinantes (Tenants)
CREATE TABLE IF NOT EXISTS saas_subscribers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    whatsapp_phone VARCHAR(30) NOT NULL,
    telegram_chat_id VARCHAR(50),
    license_token VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'canceled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Assinaturas e Planos
CREATE TABLE IF NOT EXISTS saas_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscriber_id UUID NOT NULL REFERENCES saas_subscribers(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL DEFAULT 'kiwify',
    external_order_id VARCHAR(100),
    plan_tier VARCHAR(50) NOT NULL CHECK (plan_tier IN ('radar_hunter', 'auto_sniper', 'executive_copilot', 'clt_master')),
    billing_cycle VARCHAR(20) NOT NULL DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'yearly')),
    amount_paid NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'past_due', 'canceled')),
    starts_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela de Perfil Profissional do Candidato
CREATE TABLE IF NOT EXISTS saas_candidate_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscriber_id UUID UNIQUE NOT NULL REFERENCES saas_subscribers(id) ON DELETE CASCADE,
    target_roles TEXT[] NOT NULL DEFAULT '{}',
    preferred_modality VARCHAR(30) NOT NULL DEFAULT 'remote' CHECK (preferred_modality IN ('remote', 'hybrid', 'onsite', 'any')),
    target_city VARCHAR(100),
    target_state VARCHAR(2),
    min_salary NUMERIC(10, 2),
    resume_pdf_path TEXT,
    parsed_skills JSONB DEFAULT '{}'::jsonb,
    negative_keywords TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Tabela de Vagas Mapeadas no Mercado (Banco Global Compartilhado)
CREATE TABLE IF NOT EXISTS saas_job_offers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform_source VARCHAR(50) NOT NULL,
    external_job_id VARCHAR(255),
    job_title VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    location_text VARCHAR(255),
    modality VARCHAR(30) NOT NULL DEFAULT 'remote',
    salary_text VARCHAR(100),
    description TEXT,
    apply_url TEXT NOT NULL,
    url_hash VARCHAR(64) UNIQUE NOT NULL,
    contact_email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Tabela de Candidaturas e Despachos Individuais
CREATE TABLE IF NOT EXISTS saas_job_applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscriber_id UUID NOT NULL REFERENCES saas_subscribers(id) ON DELETE CASCADE,
    job_offer_id UUID NOT NULL REFERENCES saas_job_offers(id) ON DELETE CASCADE,
    match_score INTEGER NOT NULL CHECK (match_score >= 0 AND match_score <= 100),
    cover_letter TEXT,
    dispatch_status VARCHAR(30) NOT NULL DEFAULT 'alerted' 
        CHECK (dispatch_status IN ('alerted', 'approved', 'dispatched', 'viewed', 'interview_invited', 'rejected', 'ignored')),
    approved_by_user_at TIMESTAMP WITH TIME ZONE,
    dispatched_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabela de Simulações de Entrevista por Áudio (CLT Master VIP)
CREATE TABLE IF NOT EXISTS saas_interview_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subscriber_id UUID NOT NULL REFERENCES saas_subscribers(id) ON DELETE CASCADE,
    job_offer_id UUID REFERENCES saas_job_offers(id) ON DELETE SET NULL,
    question_prompt TEXT NOT NULL,
    question_audio_url TEXT,
    answer_audio_url TEXT,
    transcription_text TEXT,
    score_awarded INTEGER CHECK (score_awarded >= 0 AND score_awarded <= 10),
    feedback_strengths TEXT,
    feedback_improvements TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices de Alta Performance
CREATE INDEX IF NOT EXISTS idx_subscribers_token ON saas_subscribers(license_token);
CREATE INDEX IF NOT EXISTS idx_subscribers_whatsapp ON saas_subscribers(whatsapp_phone);
CREATE INDEX IF NOT EXISTS idx_job_offers_hash ON saas_job_offers(url_hash);
CREATE INDEX IF NOT EXISTS idx_job_applications_user ON saas_job_applications(subscriber_id, dispatch_status);
