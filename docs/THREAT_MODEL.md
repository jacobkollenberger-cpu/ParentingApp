# Threat Model (Draft)

> Status: in progress — filled in as features are built.

## Scope
This document covers the security design of the parenting app, using a
STRIDE-based approach (Spoofing, Tampering, Repudiation, Information
Disclosure, Denial of Service, Elevation of Privilege).

## Assets to protect
- Child profile data (medical, developmental, behavioral)
- Parent account credentials
- AI conversation history
- Uploaded media/documents

## Authentication & session security

**Implementation:** JWT-based auth via `/api/auth/register` and `/api/auth/login`.

| Risk (STRIDE) | Mitigation |
|---|---|
| Spoofing — credential theft via plaintext storage | Passwords hashed with bcrypt (via passlib) before storage; plaintext never persisted or logged |
| Information Disclosure — user enumeration | Register and login return identical, generic error messages regardless of whether the email exists in the system, preventing an attacker from using error responses to build a list of valid accounts |
| Spoofing — forged/tampered tokens | JWTs are signed with a server-held `SECRET_KEY` (HS256) and verified on every protected request via `get_current_user`; tokens carry an expiry claim |
| Elevation of Privilege — token replay after account deactivation | `get_current_user` checks `is_active` on every request, not just at login, so deactivating an account invalidates access immediately even with a still-valid token |

**Known limitation (accepted for demo scope):** no refresh-token rotation
or token revocation list yet — a stolen token remains valid until it
expires. Acceptable for a portfolio-scale demo; would need addressing
before any real production use.

## Access control model (RBAC)
- `/children` endpoints filter every query by `owner_id == current_user.id`.
- Reads and writes on a child record that exists but belongs to a
  different user return the same 404 as a record that doesn't exist at
  all, so ownership can't be probed by comparing error responses.
- Single-owner model for now; co-parent sharing/roles are a planned
  extension, not yet implemented.

## To be documented
- [ ] Data encryption approach (at rest / in transit / field-level) —
      `allergies` and `medical_notes` are flagged as sensitive in the
      `Child` model but not yet field-level encrypted
- [ ] AI-specific risks (prompt injection, context leakage between users)
- [ ] File upload risks (malware, oversized files)
- [ ] Audit logging coverage
- [ ] Rate limiting on auth endpoints (brute-force protection)

## Dependency notes
- `bcrypt` is pinned to `4.0.1` alongside `passlib[bcrypt]==1.7.4` in
  `requirements.txt`. Newer `bcrypt` releases raise an exception during
  passlib's internal startup self-test rather than the older silent-
  truncation behavior passlib expects, which otherwise crashes every
  password hash operation with an unhandled `ValueError`.
