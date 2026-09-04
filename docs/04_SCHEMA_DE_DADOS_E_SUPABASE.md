# 🗄️ Documento 04 — Schema de Dados & Estrutura Relacional no Supabase

## 1. Mapeamento das Tabelas no Supabase / PostgreSQL

O banco de dados relacional foi projetado para alta integridade referencial, auditoria completa e conformidade com a LGPD:

```mermaid
erDiagram
    SUBSCRIBERS ||--o{ SUBSCRIPTIONS : has
    SUBSCRIBERS ||--o{ CANDIDATE_PROFILES : configures
    SUBSCRIBERS ||--o{ JOB_APPLICATIONS : performs
    SUBSCRIBERS ||--o{ INTERVIEW_SESSIONS : records
    JOB_OFFERS ||--o{ JOB_APPLICATIONS : matched_to

    SUBSCRIBERS {
        uuid id PK
        string full_name
        string email UK
        string whatsapp_phone
        string telegram_chat_id
        string license_token UK
        string status
        timestamp created_at
    }

    SUBSCRIPTIONS {
        uuid id PK
        uuid subscriber_id FK
        string platform
        string plan_tier
        decimal amount
        string status
        timestamp expires_at
    }

    CANDIDATE_PROFILES {
        uuid id PK
        uuid subscriber_id FK
        string target_roles
        string preferred_modality
        decimal min_salary
        string resume_pdf_url
        jsonb parsed_skills
    }

    JOB_OFFERS {
        uuid id PK
        string platform_source
        string job_title
        string company_name
        string modality
        string salary_text
        text description
        string apply_url
        string contact_email
        timestamp scraped_at
    }

    JOB_APPLICATIONS {
        uuid id PK
        uuid subscriber_id FK
        uuid job_offer_id FK
        integer match_score
        text cover_letter
        string dispatch_status
        timestamp dispatched_at
    }

    INTERVIEW_SESSIONS {
        uuid id PK
        uuid subscriber_id FK
        string question_audio_url
        string answer_audio_url
        text transcript
        integer score_awarded
        text feedback_text
        timestamp created_at
    }
```

---

## 2. Índices e Performance
- `idx_subscribers_token`: Busca ultrarrápida por hash de licença na autenticação de webhooks e APIs.
- `idx_job_offers_url_hash`: Evita duplicação de vagas raspadas mais de uma vez.
- `idx_job_applications_composite`: Acelera a consulta do painel Kanban do usuário (`subscriber_id`, `dispatch_status`).
