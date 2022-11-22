from .mining.multiprocess import mp_mining_proof
from .mining.singleprocess import get_sha256
from .block import Block
import threading


class Blockchain:
    def __init__(self, calc_complex: str = "00000"):
        self.chain: list = []
        self.init_block(1, "0", False)
        self.complex = calc_complex

    def init_block(
        self, proof: int, previous_hash: str, in_progress: bool
    ) -> Block:
        index = len(self.chain) + 1
        block = Block(index, proof, previous_hash, in_progress)
        self.chain.append(block)

        return block

    def get_previous_block(self) -> Block:
        return self.chain[-1]

    def mining(self, previous_proof):
        proof = mp_mining_proof(previous_proof, self.complex)

        last_block = self.get_previous_block()
        last_block.set_proof(proof)

    def new_block(self, wait=False) -> Block:
        """
        generating a new block and adding to the chain

        :param wait: if false - background mining
        :return: generated block
        """
        previous_block = self.get_previous_block()
        if not previous_block.in_progress:
            previous_proof = previous_block.proof
            previous_hash = previous_block.get_hash()

            block = self.init_block(0, previous_hash, True)

            p = threading.Thread(target=self.mining, args=(previous_proof,))
            p.start()
            if wait:
                p.join()
        else:
            block = previous_block
        return block

    def is_hash_complex_valid(self, hash_operation: str) -> bool:
        return hash_operation[: len(self.complex)] == self.complex

    def chain_valid(self) -> bool:
        previous_block = self.chain[0]
        block_index = 1

        while block_index < len(self.chain):
            block = self.chain[block_index]
            if block.previous_hash != previous_block.get_hash():
                return False

            previous_proof = previous_block.proof
            proof = block.proof
            hash_operation = get_sha256(proof, previous_proof)

            if not self.is_hash_complex_valid(hash_operation):
                return False

            previous_block = block
            block_index += 1

        return True
