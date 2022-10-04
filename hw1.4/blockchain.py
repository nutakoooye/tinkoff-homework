import datetime
import hashlib
from flask import Flask, jsonify, request, redirect, url_for
import multiprocessing
import threading


def math_func(proof: int, previous_proof: int) -> int:
    return proof ** 2 - previous_proof ** 2


def get_sha256(proof, previous_proof):
    return hashlib.sha256(
        str(math_func(proof, previous_proof)).encode()).hexdigest()


class Block:
    def __init__(self,
                 index: int,
                 proof: int,
                 previous_hash: str,
                 in_progress: bool):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.proof = proof
        self.previous_hash = previous_hash
        self.in_progress = in_progress

    def set_proof(self, proof):
        self.proof = proof
        self.in_progress = False

    def get_hash(self):
        hash = hashlib.sha256()
        hash.update(str(self.previous_hash).encode('utf-8'))
        hash.update(str(self.timestamp).encode('utf-8'))
        hash.update(str(self.index).encode('utf-8'))
        return hash.hexdigest()


class Blockchain:
    def __init__(self, calc_complex="00000"):
        self.chain = []
        self.init_block(1, "0", False)
        self.complex = calc_complex

    def init_block(self, proof: int, previous_hash: str,
                     in_progress: bool) -> Block:
        index = len(self.chain) + 1
        block = Block(index, proof, previous_hash, in_progress)
        self.chain.append(block)

        return block

    def get_previous_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, previous_proof, start_proof, stop_proof):
        """search for proof in a certain range"""
        new_proof = start_proof
        check_proof = False
        while check_proof is False and new_proof <= stop_proof:
            hash_operation = get_sha256(new_proof, previous_proof)
            if self.is_hash_complex_valid(hash_operation):
                check_proof = True
            else:
                new_proof += 1
        return new_proof if check_proof else None

    @staticmethod
    def find_num(iterable:list):
        for num in iterable:
            if num:
                return num
        return None

    @staticmethod
    def range_gen(previous_proof: int, patch_length: int):
        """
        generating ranges to find proof

        :param previous_proof:
        :param patch_length:length of the return range to search for evidence
        :return: range broken down by the number of cores in the system
        """
        start = 0
        end = patch_length
        step = (end - start) // multiprocessing.cpu_count()
        while True:
            iterable = []
            for start_range in range(start, end, step):
                end_range = start_range + step
                iterable.append((previous_proof, start_range, end_range))
            yield iterable
            start = end
            end += patch_length

    def mining_proof(self, previous_proof: int):
        """finding proof and adding it to the created block"""
        with multiprocessing.Pool() as pool:
            patch_length = 10 ** len(self.complex)
            iterable = self.range_gen(previous_proof, patch_length)
            last_block = self.get_previous_block()
            while last_block.in_progress:
                results = pool.starmap(self.proof_of_work, next(iterable))
                proof = self.find_num(results)
                if proof:
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
            block = self.init_block(None, previous_hash, True)
            p = threading.Thread(target=self.mining_proof,
                                 args=(previous_proof,))
            p.start()
            if wait:
                p.join()
        else:
            block = previous_block
        return block

    def is_hash_complex_valid(self, hash_operation: str) -> bool:
        return hash_operation[:len(self.complex)] == self.complex

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


app = Flask(__name__)
blockchain = Blockchain(calc_complex="000000")


@app.route('/mine_block', methods=['GET', 'POST'])
def mine_block():
    if request.method == 'POST':
        block = blockchain.new_block(wait=False)
        return redirect(url_for("get_block_status", id=block.index), 301)
    response = '''
           <form method="POST">
               <input type="submit" value="Start mining" 
               style="width: 100%; height: 10%">
           </form>'''
    return response


@app.route("/block/<int:id>/status", methods=["GET"])
def get_block_status(id):
    index = id - 1
    response = {"id": id}
    if index < len(blockchain.chain):
        block = blockchain.chain[index]
        response["status"] = "in progress" if block.in_progress else "completed"
    else:
        response["status"] = "not found"
    return jsonify(response)


@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = []
    for block in blockchain.chain:
        status = "In progress" if block.in_progress else "Completed"
        response.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "proof": block.proof,
            "previous_hash": block.previous_hash,
            "status": status
        })

    return jsonify(response), 200


@app.route("/valid", methods=["GET"])
def valid():
    return jsonify({
        "chain_valid": "OK" if blockchain.chain_valid() else "NOT OK"
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True, port=5000)
