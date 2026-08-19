"""
Rate limiting configuration.

Uses slowapi (built on the `limits` library) to throttle requests per
client IP. Applied specifically to auth endpoints - login and register
are the highest-value targets for brute-force and credential-stuffing
attacks, since a successful guess yields a valid session.

In-memory storage is fine for a single-instance demo; a real multi-server
deployment would need a shared backend (e.g. Redis) so limits are
enforced consistently across instances rather than reset per-process.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
