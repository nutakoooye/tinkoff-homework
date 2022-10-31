import datetime
import hashlib


class Block:
    def __init__(
        self, index: int, proof: int, previous_hash: str, in_progress: bool
    ):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.proof = proof
        self.previous_hash = previous_hash
        self.in_progress = in_progress

    def set_proof(self, proof: int):
        self.proof = proof
        self.in_progress = False

    def get_hash(self):
        hash = hashlib.sha256()
        hash.update(str(self.previous_hash).encode('utf-8'))
        hash.update(str(self.timestamp).encode('utf-8'))
        hash.update(str(self.index).encode('utf-8'))
        return hash.hexdigest()
