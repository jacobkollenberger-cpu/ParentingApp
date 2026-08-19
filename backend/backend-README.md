# Backend (FastAPI)

## Setup (Windows / PowerShell)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Then edit `.env` with real values (database URL, a generated secret key, etc).

## Run locally

```powershell
uvicorn app.main:app --reload
```

API will be live at http://localhost:8000
Interactive docs (dev only) at http://localhost:8000/docs

## Structure

```
app/
├── main.py              # FastAPI app, middleware, security headers
├── core/
│   ├── config.py         # Environment-based settings
│   └── security.py       # Password hashing, JWT creation/verification
├── models/                # SQLAlchemy ORM models (database tables)
│   ├── user.py
│   └── child.py
├── schemas/                # Pydantic request/response schemas
│   ├── auth.py
│   └── child.py
├── api/
│   ├── deps.py            # Shared dependencies (auth, DB session)
│   └── routes/
│       ├── auth.py        # /api/auth/register, /api/auth/login
│       └── children.py     # /api/children endpoints
└── db/
    └── session.py          # Database engine/session setup
```

## Security notes

- All `/children` endpoints require a valid JWT and filter strictly by
  `owner_id` - a user can only ever see or modify their own child records.
- `SECRET_KEY` and `DATABASE_URL` are loaded from `.env`, which is
  gitignored. Never commit real secrets.
- `allergies` and `medical_notes` fields are flagged as sensitive in
  `models/child.py` - field-level encryption for these is planned next.
- Passwords are hashed with bcrypt (via passlib) before storage; plaintext
  passwords are never persisted or logged.
- `/api/auth/login` and `/api/auth/register` return the same generic error
  message ("Incorrect email or password" / a generic registration failure)
  regardless of whether the email exists - this is a deliberate mitigation
  against user-enumeration attacks, where an attacker could otherwise probe
  which emails are registered by comparing error responses.
- `bcrypt` is pinned to `4.0.1` in `requirements.txt` alongside
  `passlib[bcrypt]`. Newer `bcrypt` releases changed a low-level behavior
  passlib's internal self-test depends on, causing hash operations to raise
  an unhandled `ValueError`. Pinning avoids this until passlib ships a fix.

## Not yet implemented (known next steps)

- [x] Auth routes (register/login) that actually issue tokens
- [x] Database migrations (Alembic)
- [ ] Field-level encryption for sensitive child data
- [ ] Audit logging on child record access/changes
- [ ] Rate limiting
