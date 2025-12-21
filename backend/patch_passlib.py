"""Monkey-patch passlib to fix bcrypt 72-byte limit bug."""
import passlib.handlers.bcrypt


# Monkey-patch passlib's bcrypt to truncate passwords to 72 bytes
_original_calc_checksum = passlib.handlers.bcrypt._BcryptCommon._calc_checksum


def _patched_calc_checksum(self, secret):
    """Truncate password to 72 bytes before hashing."""
    if isinstance(secret, str):
        secret = secret.encode('utf-8')

    # Truncate to 72 bytes to avoid bcrypt error
    if len(secret) > 72:
        secret = secret[:72]

    # Call original method with truncated secret
    return _original_calc_checksum(self, secret)


# Apply the patch
passlib.handlers.bcrypt._BcryptCommon._calc_checksum = _patched_calc_checksum

print("✅ Passlib bcrypt patch applied - passwords will be truncated to 72 bytes")
