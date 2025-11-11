import hashlib
import secrets
import string

class PasswordHasher:
    @staticmethod
    def generate_salt(length: int = 32) -> str:
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    @staticmethod
    def hash_password(password: str, salt: str) -> str:
        salted_password = password + salt
        return hashlib.sha256(salted_password.encode()).hexdigest()