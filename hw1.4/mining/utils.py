import hashlib


def math_func(proof: int, previous_proof: int) -> int:
    return proof**2 - previous_proof**2


def get_sha256(proof: int, previous_proof: int) -> str:
    return hashlib.sha256(
        str(math_func(proof, previous_proof)).encode()
    ).hexdigest()
