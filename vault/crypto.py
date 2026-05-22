import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_key():
    key = os.environ.get('CIPHER_KEY')
    if not key:
        raise ValueError("CIPHER_KEY environment variable not set")
    return base64.urlsafe_b64decode(key.encode())

def encrypt_password(plain_text: str) -> bytes:
    key = get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)                        # 12 random bytes
    encrypted = aesgcm.encrypt(nonce, plain_text.encode(), None)
    return base64.urlsafe_b64encode(nonce + encrypted)

def decrypt_password(encrypted_bytes) -> str:
    key = get_key()
    aesgcm = AESGCM(key)
    decoded = base64.urlsafe_b64decode(bytes(encrypted_bytes))
    nonce = decoded[:12]                          # first 12 bytes = nonce
    cipher_text = decoded[12:]                    # rest = encrypted data
    return aesgcm.decrypt(nonce, cipher_text, None).decode()

def check_strength(password: str) -> dict:
    score = 0
    feedback = []

    if len(password) >= 8:   score += 1
    else: feedback.append("Use at least 8 characters")

    if len(password) >= 12:  score += 1
    else: feedback.append("12+ characters is stronger")

    if any(c.isupper() for c in password): score += 1
    else: feedback.append("Add uppercase letters")

    if any(c.islower() for c in password): score += 1
    else: feedback.append("Add lowercase letters")

    if any(c.isdigit() for c in password): score += 1
    else: feedback.append("Add numbers")

    if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password): score += 1
    else: feedback.append("Add special characters")

    labels = {6: "Strong", 5: "Strong", 4: "Good", 3: "Fair", 2: "Weak", 1: "Very Weak", 0: "Very Weak"}
    colors = {6: "green", 5: "green", 4: "blue", 3: "orange", 2: "red", 1: "red", 0: "red"}

    return {
        "score": score,
        "max": 6,
        "label": labels[score],
        "color": colors[score],
        "feedback": feedback,
        "percentage": int((score / 6) * 100)
    }
