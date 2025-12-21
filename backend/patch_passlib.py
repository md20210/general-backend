"""Monkey-patch bcrypt to fix passlib 72-byte limit bug."""
import bcrypt as _bcrypt_module

# Store original bcrypt.hashpw
_original_hashpw = _bcrypt_module.hashpw


def _patched_hashpw(password, salt):
    """Truncate password to 72 bytes before hashing."""
    if isinstance(password, str):
        password = password.encode('utf-8')

    # Truncate to 72 bytes to avoid bcrypt error
    if len(password) > 72:
        password = password[:72]

    # Call original bcrypt.hashpw with truncated password
    return _original_hashpw(password, salt)


# Patch bcrypt.hashpw directly
_bcrypt_module.hashpw = _patched_hashpw

print("✅ Bcrypt patch applied - passwords will be truncated to 72 bytes")
