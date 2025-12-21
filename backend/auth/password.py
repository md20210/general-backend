"""Custom password helper using bcrypt directly without passlib."""
import bcrypt
from fastapi_users.password import PasswordHelperProtocol


class BcryptPasswordHelper(PasswordHelperProtocol):
    """Password helper using bcrypt directly."""

    def __init__(self, rounds: int = 12):
        """Initialize bcrypt password helper.

        Args:
            rounds: Number of bcrypt rounds (default: 12)
        """
        self.rounds = rounds

    def verify_and_update(
        self, plain_password: str, hashed_password: str
    ) -> tuple[bool, str | None]:
        """Verify a password and return if it needs rehashing.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to verify against

        Returns:
            Tuple of (verified, updated_hash or None)
        """
        # Ensure inputs are bytes
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # Verify password
        verified = bcrypt.checkpw(plain_bytes, hashed_bytes)

        # Check if rehashing is needed (rounds changed)
        updated_hash = None
        if verified:
            # Extract current rounds from hash
            # Bcrypt hash format: $2b$12$...
            current_rounds = int(hashed_password.split('$')[2])
            if current_rounds != self.rounds:
                updated_hash = self.hash(plain_password)

        return verified, updated_hash

    def hash(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string
        """
        # Ensure password is bytes
        password_bytes = password.encode('utf-8')

        # Generate salt and hash
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Return as string
        return hashed.decode('utf-8')

    def generate(self) -> str:
        """Generate a random password.

        Returns:
            Random password string
        """
        import secrets
        import string

        # Generate a 16-character random password
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(16))
