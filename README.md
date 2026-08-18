# Parenting App — AI-Powered Family Advisor & Record Vault

> A secure, AI-assisted parenting platform that grounds its advice in a structured,
> continuously-updated record of each child — built as a demonstration of
> full-stack development and applied security engineering.

## Why this project exists

Most AI "parenting assistants" are generic chatbots with no memory of the
child they're talking about. This project explores what it takes to build
one that actually knows a child's history — age, milestones, preferences,
past conversations — and uses that context safely, securely, and
transparently.

It's also a portfolio project demonstrating security-conscious application
design: authentication, access control, encrypted sensitive data, audit
logging, and AI-specific safeguards (prompt-injection resistance, tiered
response safety).

## Core concept

- **AI Parenting Advisor** — situational guidance grounded in the child's
  profile, with a tiered safety model (routine guidance → info + professional
  referral → emergency-first response).
- **Child Record Vault** — structured, encrypted storage of medical,
  developmental, and preference data.
- **Family Organizer** — calendar, milestones, and routines.
- *(Future)* Co-parenting permissions and shared expense tracking.

## Security architecture (high level)

| Area | Approach |
|---|---|
| Auth | OAuth + MFA via managed auth provider |
| Access control | Role-based (parent / co-parent / viewer) |
| Data protection | Encryption at rest & in transit, field-level encryption for sensitive data |
| AI safety | Prompt-injection mitigation, output tiering, context scoping |
| Auditability | Access/change logging on all child-record reads and writes |

Full threat model: see [`docs/THREAT_MODEL.md`](docs/THREAT_MODEL.md) *(coming soon)*.

## Tech stack

- **Frontend:** Next.js, TypeScript
- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Auth:** Managed provider (Supabase Auth / Clerk)
- **AI:** LLM API with retrieval-augmented context from the child profile
- **Infra:** Docker, deployed on Vercel (frontend) + Railway/Render (backend)

## Project structure

```
parenting-app/
├── backend/     # FastAPI application
├── frontend/    # Next.js application
├── docs/        # Threat model, architecture notes, decisions
└── README.md
```

## Status

🚧 Early development — see [Issues](../../issues) for current progress.

## Getting started

Setup instructions will be added once the backend and frontend scaffolding
land (see `backend/README.md` and `frontend/README.md`).
