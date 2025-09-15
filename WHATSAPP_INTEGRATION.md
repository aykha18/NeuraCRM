## WhatsApp Business Integration for NeuraCRM

### Purpose
Enable first‑class WhatsApp Business messaging in NeuraCRM to acquire, qualify, and convert leads faster, while giving sales reps AI assistance and management real‑time visibility.

---

## 1) Objectives
- Centralize WhatsApp conversations in CRM, mapped to Contacts/Leads/Deals.
- Support compliant outbound messaging (templates) and inbound session messaging.
- Provide AI insights (intent, sentiment, summary, next‑best‑action) on threads.
- Automate routine actions (create lead, schedule tasks, send pricing, follow‑ups).
- Measure channel performance (volume, response times, conversion, revenue).

---

## 2) Integration Options

### A. Meta WhatsApp Business Platform (Cloud API)
- Direct integration with Meta; our app hosts webhook + access token.
- Pros: lowest latency/cost, control over features, no vendor lock‑in.
- Requirements: Verified Business Manager, WABA, phone number, approved templates, webhook URL, HSM management.

### B. BSP (Twilio, 360dialog, MessageBird)
- Pros: faster onboarding, number hosting, simpler template tooling.
- Tradeoff: ongoing vendor margin, feature gaps, pricing variability.

Recommendation: Start with Meta Cloud API and hide behind a Provider Adapter so we can swap/augment with a BSP later if needed.

---

## 3) High‑Level Architecture

```
WhatsApp User  <->  Meta Cloud API  <->  Webhook Receiver (FastAPI)
                                             |
                                         Event Bus
                                             |
                 +----------------------------+----------------------------+
                 |                             |                            |
             Message Store                 AI Pipeline                 Notification
           (Postgres/pgvector)          (Summaries/Intent/NBA)            (Tasks)
                 |                             |                            |
               CRM UI <------------------------------------------------------+
                 |
           Outbound Sender  -> Meta Cloud API (session + template messages)
```

Components:
- Webhook Receiver: `POST /webhooks/whatsapp` (verification + message/status ingest).
- Provider Adapter Interface: `send_message`, `send_template`, `mark_read`, `upload_media`.
- Queue/Worker: retries, rate limit handling, async AI jobs.
- Data Store: normalized messages/threads; vector index for AI.
- UI: unified inbox, template sender, AI panel, analytics dashboard.

---

## 4) Data Model (Proposed Tables)

- `whatsapp_accounts(id, organization_id, phone_number_id, waba_id, access_token_enc, verified_at, status)`
- `whatsapp_contacts(id, organization_id, wa_id, contact_id, opt_in_status, last_seen_at)`
- `whatsapp_threads(id, organization_id, contact_id, lead_id, last_msg_at, is_open)`
- `whatsapp_messages(id, thread_id, provider_msg_id, direction, text, media_id, status, sent_at, delivered_at, read_at, ai_intent, ai_sentiment, ai_entities_json)`
- `media_blobs(id, organization_id, provider_media_id, storage_url, mime_type, size, expires_at)`

Indexes:
- `whatsapp_messages(thread_id, sent_at DESC)`, `whatsapp_contacts(wa_id, organization_id)`.

---

## 5) API & Webhooks (FastAPI)

### Webhooks
- `GET /webhooks/whatsapp`: verification challenge (hub.mode/token/challenge).
- `POST /webhooks/whatsapp`: signature verification (X‑Hub‑Signature‑256) → enqueue `message_received`/`status_update` events → always 200 fast.

### Admin (per organization)
- `POST /api/whatsapp/accounts`: connect credentials (encrypted at rest).
- `GET /api/whatsapp/templates` and `POST /api/whatsapp/templates/sync`.

### Messaging
- `GET /api/whatsapp/threads?open=1&contact_id=...`
- `GET /api/whatsapp/threads/{id}`
- `GET /api/whatsapp/threads/{id}/messages?cursor=...`
- `POST /api/whatsapp/messages` (session message within 24h)
- `POST /api/whatsapp/messages/template` (HSM with template name + components)
- `POST /api/whatsapp/media` (ingest uploads) / `GET /api/whatsapp/media/{id}` (signed URL)

### Provider Adapter (Python)
```python
class WhatsAppProvider(Protocol):
    def send_message(self, wa_account, to_wa_id, text, context=None) -> ProviderResult: ...
    def send_template(self, wa_account, to_wa_id, template, lang, components) -> ProviderResult: ...
    def mark_read(self, wa_account, message_id): ...
    def upload_media(self, wa_account, file_path_or_url): ...
```

---

## 6) Compliance & Policy
- Consent capture and audit trail on each contact (opt‑in channel/source).
- 24‑hour customer care window enforcement; outside window require template.
- Template lifecycle: create → submit → approved → usage; locale management.
- Opt‑out/STOP handling; Do‑Not‑Contact flags; suppression lists.
- PII minimization: redact before vectorization; encrypt raw payloads.

---

## 7) AI Sales Assistant

### Pipeline
1. **Normalization**: strip quoted text, unify emojis, OCR images/PDFs.
2. **Detection**: language, intent (pricing/demo/support/objection), sentiment.
3. **Extraction**: entities (company, budget, product, date/time); BANT scoring.
4. **Summaries**: rolling thread summary; “since last update” delta.
5. **NBA**: next‑best‑action suggestions – reply drafts, template suggestion, schedule demo, escalate.
6. **Automation**: rules/triggers (e.g., intent=demo → create task + invite draft).

### Models & Store
- LLM: GPT‑4o‑mini / Llama‑3.1‑8B‑Instruct (switchable). Small classifier for fast intent.
- Vector DB: pgvector (reuse Postgres) or Qdrant for semantic search.
- Guardrails: profanity filter, data redaction, template boundary
  (never send unapproved copy outside 24‑hour window).

---

## 8) Frontend UX

- Unified Inbox (WhatsApp tag): thread list with unread, SLA badge, channel icon.
- Composer:
  - Session mode and Template mode (picker + variable preview).
  - Attachments; quick replies; AI reply suggestions.
- Right Sidebar: contact 360, lead/deal links, AI insights (intent, summary, NBA), tasks.
- Admin → WhatsApp Settings: connect number, templates, compliance, automation rules.

---

## 9) Deployment & Ops

- Secrets in KMS/Vault; per‑org credential encryption.
- Webhook IP allowlist; signature verification; idempotency keys.
- Job queue (RQ/Celery) with retry/backoff; dead‑letter queue.
- Observability: structured logs; dashboards – message volume, delivery success, response time, template quality, conversion; alerting on sustained 4xx/5xx and rate limits.
- SLOs: webhook ack < 300ms (async jobs); outbound success ≥ 99%; median first‑response time < 5 min.

---

## 10) Milestones (6‑week plan)

**W1**: Provider adapter, webhook verification, models/migrations, message ingest → DB.

**W2**: Thread mapping to Contact/Lead; inbox UI read‑only; session send path.

**W3**: Templates sync & send; queue/retry; delivery/read receipts; media handling.

**W4**: AI v1 (summary, sentiment, intent) + insights panel; analytics v1.

**W5**: NBA + reply drafts; automation rules; compliance UI (opt‑in/opt‑out).

**W6**: Load testing; rate‑limit handling; SLO dashboard; playbooks & docs.

---

## 11) Cost / Benefit Analysis

### Cost Drivers
- **Meta WhatsApp fees** (illustrative; region dependent):
  - Conversation‑based pricing by category (Marketing, Utility, Authentication, Service); $0.01–$0.15 per conversation typical.
  - Template approval is free; failures cost time.
- **Infra**:
  - App/API & workers (Railway/Render/Heroku) – $30–$150/mo for small teams.
  - Storage for media (S3/GCS) – $5–$50/mo depending on volume; egress minimal with signed URLs.
  - Vector DB (pgvector on existing Postgres) – incremental.
- **AI**:
  - Summaries/intent per message – $0.0005–$0.003 each (with small models / batching).
  - For 10k msgs/mo → $5–$30/mo.

### Implementation Effort
- Initial build ~4–6 weeks for MVP with one engineer + part‑time design.
- Template ops and compliance overhead ongoing but small.

### Benefits (Quantified)
- **Lead capture uplift**: +15–30% vs email/web forms in markets where WhatsApp is primary.
- **Speed‑to‑lead**: 2–5× faster first response → 35–50% conversion lift (industry benchmarks).
- **Rep productivity**: AI summaries/NBA reduce handling time 20–35% per conversation.
- **Marketing ROI**: templated broadcast to opted‑in lists → 20–40% CTR, 5–15% conversion (use judiciously to protect template quality scores).

### ROI Example (conservative)
- 3 reps, 600 inbound WhatsApp convos/mo.
- Close rate improves from 6% → 8% (from AI + speed) → +12 deals.
- AOV $300 → +$3,600/mo incremental; channel + infra cost $150–$300 → net +$3,300/mo.

---

## 12) Sales Acceleration Playbook

1. **Instant routing**: first inbound → assign by round‑robin; SLA timer; auto‑greet within 5s.
2. **Template nudges**: 23‑hour follow‑up within care window; outside window use Utility/Marketing template with consent.
3. **AI objection handling**: suggest knowledge snippets and response drafts; one‑tap send.
4. **Qualification rules**: if intent=demo or budget>threshold → create deal + task automatically.
5. **Broadcasts**: approved Marketing template to warm opt‑in segments (low frequency) → promo/demos.
6. **Win‑back**: template campaign to stalled deals with incentive; track improvement in reopen rate.

KPIs to watch: first response time, conversation‑to‑lead rate, lead‑to‑deal rate, revenue per conversation, rep handling time, template quality rating, opt‑out rate.

---

## 13) Risks & Mitigations

- **24‑hour rule violations** → template guard + UI warnings; auto‑fallback.
- **Template quality drops** → frequency caps, relevance scoring, audience selection.
- **Rate limits** → queue with backoff; shard by phone_number_id.
- **PII/Compliance** → encryption, redaction before AI; opt‑out enforcement; audits.
- **Model drift/AI errors** → human‑in‑the‑loop; never auto‑send outside templates.

---

## 14) Success Criteria
- T‑30 days: time‑to‑first‑response < 5 min (P50), all inbound chats mapped to contacts/leads.
- T‑60 days: +15% conversation‑to‑lead conversion; AI suggestions used in >50% replies.
- T‑90 days: +20% rep productivity; +10–20% revenue lift attributable to WhatsApp channel.

---

## 15) Backlog / Future
- Multi‑number per org; per‑rep signatures.
- Commerce messages (catalog, order notifications) where available.
- Voice notes transcription; image understanding for product questions.
- Auto‑translation for cross‑language conversations.


