# General Backend Package

# CRITICAL: Patch bcrypt BEFORE any other imports
import bcrypt as _bcrypt_module

_original_hashpw = _bcrypt_module.hashpw


def _patched_hashpw(password, salt):
    """Truncate password to 72 bytes before hashing."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    if len(password) > 72:
        password = password[:72]
    return _original_hashpw(password, salt)


_bcrypt_module.hashpw = _patched_hashpw
print("✅ Bcrypt patch applied in backend/__init__.py")
