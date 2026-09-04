# 🛡️ Documento 06 — Política Anti-Pirataria, Proteção de IP & Conformidade LGPD

## 1. Princípios Imutáveis de Proteção de Propriedade Intelectual

1. **Vedação ao Código Aberto / Arquivo Local:**  
   Sob nenhuma hipótese o código Python, os adaptadores de scraping ou os prompts dos LLMs são disponibilizados para download. O cliente adquire uma **licença de uso de serviço (SaaS)**, e não a titularidade do código.
2. **Modelo Black-Box Centralizado na VPS:**  
   Todo o processamento inteligente reside no servidor soberano da Autonomia Empregos. A interface do usuário limita-se a comandos de chat (WhatsApp/Telegram) ou formulários web controlados.
3. **Corte Imediato por Inadimplência:**  
   Caso a recorrência falhe na Kiwify (estorno, cancelamento ou falta de pagamento), o webhook do n8n atualiza o status para `canceled` no Supabase, revogando o token de atendimento no mesmo instante.
4. **Rate Limiting & Anti-Abuso:**  
   Para evitar que concorrentes contratem o plano para minerar dados ou saturar a infraestrutura, cada plano possui limites diários de candidaturas e alertas:
   - Radar Hunter: Até 30 vagas qualificadas/dia.
   - Auto-Sniper: Até 15 despachos de cartas por e-mail/dia.
   - Executive Copilot: Até 30 candidaturas ativas simultâneas.
   - CLT Master VIP: Até 5 sessões completas de simulação por semana.

---

## 2. Conformidade Rigorosa com a LGPD (Lei nº 13.709/2018)

- **Consentimento Expresso:** No ato do envio do currículo pelo WhatsApp, o assinante concorda com o processamento dos seus dados profissionais para fins exclusivos de matching de vagas.
- **Anonimização de Dados para LLMs:** Dados de documento pessoal sensíveis (como CPF ou RG que constem no currículo do candidato) são mascarados antes de qualquer envio a APIs de terceiros.
- **Direito ao Esquecimento:** O comando `/excluir_meus_dados` no WhatsApp remove o arquivo PDF e todos os dados cadastrais do banco Supabase em até 24 horas úteis.
