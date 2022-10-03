import datetime
import hashlib
from flask import Flask, jsonify
import multiprocessing
import threading


def math_func(proof: int, previous_proof: int) -> int:
    return proof ** 2 - previous_proof ** 2


def get_sha256(proof, previous_proof):
    return hashlib.sha256(
        str(math_func(proof, previous_proof)).encode()).hexdigest()


class Block:
    def __init__(self, index: int, proof: int, previous_hash: str, status: str):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.proof = proof
        self.previous_hash = previous_hash
        self.status = status

    def get_hash(self):
        hash = hashlib.sha256()
        hash.update(str(self.previous_hash).encode('utf-8'))
        hash.update(str(self.timestamp).encode('utf-8'))
        hash.update(str(self.index).encode('utf-8'))
        return hash.hexdigest()


class Blockchain:
    def __init__(self, calc_complex="00000"):
        self.chain = []
        self.create_block(1, "0", "completed")
        self.complex = calc_complex

    def create_block(self, proof, previous_hash, status):
        index = len(self.chain) + 1
        block = Block(index, proof, previous_hash, status)
        self.chain.append(block)

        return block

    def get_previous_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, previous_proof, start_proof, stop_proof):
        new_proof = start_proof
        check_proof = False
        print(start_proof, stop_proof)
        while check_proof is False and new_proof <= stop_proof:
            hash_operation = get_sha256(new_proof, previous_proof)

            if self.is_hash_complex_valid(hash_operation):
                check_proof = True
            else:
                new_proof += 1
        if check_proof:
            return new_proof
        return None

    def is_hash_complex_valid(self, hash_operation):
        return hash_operation[:len(self.complex)] == self.complex

    def chain_valid(self):
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


def find_num(iterable):
    for num in iterable:
        if num:
            return num
    return None


def task_gen(previous_proof, patch_length):
    start = 0
    end = patch_length
    step = (
                   end - start) // multiprocessing.cpu_count()  # число загружаемых заданий всем процессам
    while True:
        iterable = []
        for start_range in range(start, end, step):
            end_range = start_range + step
            iterable.append((previous_proof, start_range, end_range))
        yield iterable
        start = end
        end += patch_length


def callback(results):
    last_block = blockchain.get_previous_block()
    proof = find_num(results)
    if proof:
        last_block.proof = proof
        last_block.status = "completed"


def mining_proof(previous_proof):
    with multiprocessing.Pool() as pool:
        patch_length = 10 ** len(blockchain.complex)
        iterable = task_gen(previous_proof, patch_length)
        last_block = blockchain.get_previous_block()
        print(last_block.__dict__)
        while last_block.status == "in_progress":
            results = pool.starmap(blockchain.proof_of_work, next(iterable))
            proof = find_num(results)
            if proof:
                last_block.proof = proof
                last_block.status = "completed"
                break


@app.route("/multiprocessing", methods=["GET"])
def mp_mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block.proof
    previous_hash = previous_block.get_hash()
    block = blockchain.create_block(None, previous_hash, "in_progress")

    # mining_proof(previous_proof)
    response = {
        "status": block.status,
        "index": block.index,
    }
    p = threading.Thread(target=mining_proof, args=(previous_proof,))
    p.start()
    return jsonify(response), 200


# @app.route("/mine_block", methods=["GET"])
# def mine_block():
#     previous_block = blockchain.get_previous_block()
#     previous_proof = previous_block.proof
#     t_begin = datetime.datetime.now()
#     proof = blockchain.proof_of_work(previous_proof, 1, 10000000000)
#     t_end = datetime.datetime.now()
#     executed_time = t_end - t_begin
#     previous_hash = previous_block.get_hash()
#
#     block = blockchain.create_block(proof, previous_hash)
#
#     response = {
#         "message": "Block created",
#         "index": block.index,
#         "timestamp": block.timestamp,
#         "proof": block.proof,
#         "previous_hash": block.previous_hash,
#         "executed time in seconds": executed_time.total_seconds()
#     }
#
#     return jsonify(response), 200


@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = []
    for block in blockchain.chain:
        response.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "proof": block.proof,
            "previous_hash": block.previous_hash,
            "status": block.status
        })

    return jsonify(response), 200


@app.route("/valid", methods=["GET"])
def valid():
    return jsonify({
        "chain_valid": "OK" if blockchain.chain_valid() else "NOT OK"
    }), 200


app.run(host="127.0.0.1", debug=True, port=5000)
