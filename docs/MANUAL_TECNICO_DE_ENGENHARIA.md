# 🛠️ Manual Técnico de Engenharia & Operação — Autonomia Empregos

> **Módulo:** `MOD-015` | **Repositório:** [`funil66/AUTONOMIA-EMPREGOS`](https://github.com/funil66/AUTONOMIA-EMPREGOS)  
> **Classificação:** Micro-SaaS Soberano B2C/B2B | **Porta VPS:** Gateway `:8000` / n8n `:5678`

---

## 1. Visão Geral da Pilha Tecnológica (Stack)

* **Runtime:** Python 3.12+ com tipagem estrita via Pydantic v2.
* **Banco de Dados Relacional:** PostgreSQL 15+ (Supabase) sob o container `jarvis-postgres` na porta 5432.
* **Gateway de Pagamento:** Asaas API v3 (conta homologada Raelcia Studio com chave webhook segura).
* **Canal de Mensagens:** Evolution API (porta 8081 / `zap.allissonsousa.adv.br`) + Telegram Bot API.
* **Inteligência Artificial & Transcrição:** 
  * Geração de Cartas: Claude 3.5 Sonnet / OpenAI via Hub Central 9Router.
  * Transcrição de Áudio de Entrevistas: Faster-Whisper local (CPU multi-thread na VPS).

---

## 2. Estrutura de Diretórios e Módulos

```
03_MICRO_SAAS/05_Vagas_Career_SaaS/
├── core/
│   ├── config.py             # Configurações centralizadas, thresholds e time-outs
│   ├── schemas.py            # Modelos Pydantic v2 de dados relacionais
│   ├── normalizer.py         # Higienização de texto, hashing SHA-256 de URL e classificação de modalidade
│   └── matcher.py            # Motor determinístico de matching (40% cargo, 30% modalidade, 30% skills)
├── adapters/
│   ├── base.py               # Interface abstrata para agregadores de vagas
│   └── mock_adapter.py       # Adaptador determinístico para testes e homologação
├── services/
│   └── asaas_webhook.py      # Receptor de webhooks do Asaas, provisionamento de assinante e WhatsApp
├── notifications/
│   └── formatters.py         # Formatadores humanizados de alertas executivos e prompts de IA
├── database/
│   └── migrations/           # DDL executável (PostgreSQL / Supabase)
├── web/
│   └── landing_page/         # Frontend estático de alta conversão (HTML5, Termos, LGPD)
└── tests/                    # Bateria de testes automatizados (pytest 9.1.1)
```

---

## 3. Fluxo de Execução do Ciclo de Busca (Job Pipeline)

1. **Agendamento (Cron / n8n):** Dispara a cada 6 horas (06:00, 12:00, 18:00, 00:00).
2. **Scraping Coletivo:** Coleta vagas dos termos alvo cadastrados pelos assinantes ativos.
3. **Deduplicação Determinística:** Calcula o hash SHA-256 da URL limpa (`JobNormalizer.compute_url_hash`). Se já existir na tabela `saas_job_offers`, a vaga é descartada do processamento pesado.
4. **Matching Multi-Tenant:** Itera sobre todos os `saas_candidate_profiles` ativos:
   * Aplica hard veto para palavras proibidas pelo candidato.
   * Calcula pontuação ponderada.
   * Se score $\ge 70\%$, insere na tabela `saas_job_applications` como `alerted`.
5. **Notificação Humanizada:** Envia alerta formatado no WhatsApp com botão interativo para o candidato aprovar o despacho de carta com IA.

---

## 4. Bateria de Testes e Quality Gates (Pilar E)

Para executar a suíte de testes de integridade:
```bash
/home/funil/DEV/GOOGLE-1/.venv/bin/pytest 03_MICRO_SAAS/05_Vagas_Career_SaaS/tests -v
```
Critério de aprovação: 100% de sucesso (13 testes aprovados sem avisos de depreciação).
