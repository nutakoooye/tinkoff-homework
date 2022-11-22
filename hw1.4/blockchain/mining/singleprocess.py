from math import inf
from typing import Optional
import hashlib


def math_func(proof: int, previous_proof: int) -> int:
    return proof**2 - previous_proof**2


def get_sha256(proof: int, previous_proof: int) -> str:
    return hashlib.sha256(
        str(math_func(proof, previous_proof)).encode()
    ).hexdigest()


def proof_of_work(
    complex: str,
    previous_proof: int,
    start_range: int = 0,
    end_range: int | float = inf,
) -> Optional[int]:
    """search for proof in a certain range"""

    new_proof = start_range
    check_proof = False
    while check_proof is False and new_proof <= end_range:
        hash_operation = get_sha256(new_proof, previous_proof)
        if hash_operation[: len(complex)] == complex:
            check_proof = True
        else:
            new_proof += 1
    return new_proof if check_proof else None
