# 🛒 Documento 05 — Esteira de Vendas, Checkout & Onboarding Automático

## 1. O Funil de Conversão & Onboarding em Menos de 60 Segundos

A jornada do cliente foi desenhada para ter zero atrito técnico e entrega instantânea de valor:

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as Comprador / Candidato
    participant LP as Landing Page (empregos.autonomia.app.br)
    participant Kiwi as Kiwify / Gateway de Pagamento
    participant N8N as n8n Webhook Ingestor
    participant DB as Supabase Database
    participant WPP as WhatsApp Evolution API

    Cliente->>LP: Acessa e escolhe o plano (ex: Auto-Sniper R$ 97/mês)
    LP->>Kiwi: Redireciona para checkout com Pix em 1 clique
    Cliente->>Kiwi: Efetua o pagamento do Pix
    Kiwi->>N8N: Dispara Webhook de Compra Aprovada (order_status: paid)
    N8N->>DB: Cria assinante, gera License Token e ativa assinatura
    N8N->>WPP: Dispara mensagem calorosa de boas-vindas para o WhatsApp do cliente
    WPP-->>Cliente: "Olá, Dr(a)! Seu Copiloto de Carreira está ativo. Envie seu currículo em PDF aqui para começarmos!"
    Cliente->>WPP: Envia o arquivo PDF do currículo
    WPP->>N8N: Recebe o PDF, extrai dados de carreira e confirma preferências
    WPP-->>Cliente: "Perfeito! Já mapeei suas competências. Sua primeira varredura de vagas começa agora."
```

---

## 2. Script de Boas-Vindas Humanizado no WhatsApp

Assim que a compra é aprovada, o assinante recebe a seguinte mensagem (com status de "digitando..."):

```text
Olá, {{nome}}! Tudo bem? 🎯

Sou a Clara, sua Assistente Executiva de Carreira da Autonomia Empregos.

Seu acesso ao plano {{plano}} foi confirmado com sucesso! 🚀

A partir de agora, você não precisa mais perder horas navegando em sites de vagas. Eu vou caçar as melhores oportunidades para você 24 horas por dia.

Para configurarmos seu perfil em 1 minuto, por favor:
1️⃣ Me envie aqui o arquivo PDF do seu currículo mais atualizado.
2️⃣ Me diga: qual o cargo que você busca e sua pretensão salarial mínima?

Estou pronta! Pode me mandar o PDF por aqui mesmo. 👇
```
