from secrets import token_urlsafe
from hashlib import sha256
import base64

def verify_pkce(code_verifier: str, code_challenge: str) -> bool:
    digest = sha256(code_verifier.encode()).digest()
    b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return b64 == code_challenge
