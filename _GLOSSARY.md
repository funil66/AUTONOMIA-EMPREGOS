---
id: "GLOSSARY-05-AUTONOMIA-EMPREGOS"
tipo: "glossary"
dominio: "MICRO_SAAS"
up: "[[_INDEX]]"
status: "ativo"
data_criacao: "2026-09-03"
---

# 📖 Glossário Analítico & Dicionário de Variáveis — AUTONOMIA EMPREGOS

## 1. Entidades de Negócio e Assinatura

| Termo | Definição Canônica | Mapeamento no Banco / Sistema |
| :--- | :--- | :--- |
| `TENANT` / `SUBSCRIBER` | Usuário final pagante do SaaS que contratou uma assinatura. | Tabela `saas_subscribers` no Supabase. |
| `RADAR_HUNTER` (Tier 1) | Plano básico de busca de vagas com alertas imediatos sem geração de cartas. | Coluna `plan_tier = 'radar_hunter'`. |
| `AUTO_SNIPER` (Tier 2) | Plano intermediário com cartas de apresentação em IA e despacho por e-mail. | Coluna `plan_tier = 'auto_sniper'`. |
| `EXECUTIVE_COPILOT` (Tier 3) | Plano profissional com integração a boards globais ATS e Kanban de gestão. | Coluna `plan_tier = 'executive_copilot'`. |
| `CLT_MASTER_VIP` (Tier 4) | Plano supremo de carreira com simulador de entrevista por áudio e auditoria PJ/CLT. | Coluna `plan_tier = 'clt_master'`. |
| `KIWIFY_WEBHOOK` | Gatilho assíncrono emitido pela processadora de pagamentos no ato da compra. | Endpoint n8n `/webhook/kiwify-career-onboarding`. |
| `TOKEN_LICENCA` | Hash criptográfico (JWT) atrelado ao WhatsApp e E-mail do comprador para autenticar chamadas. | Coluna `license_token` (SHA-256). |

---

## 2. Entidades Operacionais de Carreira

| Termo | Definição Canônica |
| :--- | :--- |
| `ATS_SCORE` | Nota de 0 a 100 calculada pelo cruzamento entre o perfil do candidato e as exigências da vaga. |
| `SNIPER_DISPATCH` | E-mail de apresentação formal enviado diretamente ao tomador de decisão (RH/Sócio) com anexo em PDF. |
| `HUMAN_IN_THE_LOOP` | Princípio mandatório onde o robô NUNCA dispara sem aprovação prévia do assinante via botão no WhatsApp/Telegram. |
| `AUDIO_DIAGNOSTICO` | Módulo de análise de fala onde o candidato grava áudio e a IA avalia dicção, vocabulário e método STAR. |
| `AUDITORIA_PJ_CLT` | Relatório comparativo com cálculo real de impostos (Simples Nacional vs CLT) e rescisão trabalhista. |
