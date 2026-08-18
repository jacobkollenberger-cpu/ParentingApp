# Threat Model (Draft)

> Status: placeholder — to be filled in as features are built.

## Scope
This document will cover the security design of the parenting app, using a
STRIDE-based approach (Spoofing, Tampering, Repudiation, Information
Disclosure, Denial of Service, Elevation of Privilege).

## Assets to protect
- Child profile data (medical, developmental, behavioral)
- Parent account credentials
- AI conversation history
- Uploaded media/documents

## To be documented
- [ ] Authentication & session security
- [ ] Access control model (RBAC)
- [ ] Data encryption approach (at rest / in transit / field-level)
- [ ] AI-specific risks (prompt injection, context leakage between users)
- [ ] File upload risks (malware, oversized files)
- [ ] Audit logging coverage
- [ ] Known limitations / accepted risks for the demo scope
