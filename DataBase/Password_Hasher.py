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
    
    @staticmethod
    def verify_password(input_password: str, stored_hash: str, stored_salt: str) -> bool:
        new_hash = PasswordHasher.hash_password(input_password, stored_salt)
        return new_hash == stored_hash