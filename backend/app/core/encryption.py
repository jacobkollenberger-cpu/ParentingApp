"""
Field-level encryption for sensitive database columns.

Uses Fernet (symmetric, authenticated encryption from the `cryptography`
library) so sensitive fields are unreadable at rest even to someone with
raw database access (a leaked backup, a compromised DB credential, etc.) -
this is defense in depth on top of RBAC and transport encryption, not a
replacement for either.

EncryptedString is a SQLAlchemy TypeDecorator: it hooks into the normal
read/write path transparently, so model and route code never has to think
about encryption directly - a route just reads/writes `child.allergies`
as a plain string, exactly as before.
"""

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy.types import Text, TypeDecorator

from app.core.config import settings

_fernet = Fernet(settings.encryption_key.encode())


class EncryptedString(TypeDecorator):
    """A text column that is encrypted before storage and decrypted on read.

    Backed by Text (unbounded) rather than a fixed-length String, since
    Fernet ciphertext is meaningfully longer than the original plaintext
    (encryption overhead plus base64 encoding) - a fixed-length column
    sized off the plaintext would risk silently truncating ciphertext.
    """

    impl = Text
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """Called automatically before writing to the database."""
        if value is None:
            return None
        return _fernet.encrypt(value.encode()).decode()

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """Called automatically after reading from the database."""
        if value is None:
            return None
        try:
            return _fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            # Data that predates encryption being enabled, or was tampered
            # with / encrypted under a different key. Fail loudly rather
            # than silently returning garbage ciphertext to the client.
            raise ValueError(
                "Could not decrypt field - wrong ENCRYPTION_KEY or corrupted data"
            )
