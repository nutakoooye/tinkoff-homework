import datetime
import hashlib
from flask import Flask, jsonify
import multiprocessing


def math_func(proof: int, previous_proof: int) -> int:
    return proof ** 2 - previous_proof ** 2


def get_sha256(proof, previous_proof):
    return hashlib.sha256(
        str(math_func(proof, previous_proof)).encode()).hexdigest()


class Block:
    def __init__(self, index, proof, previous_hash):
        self.index = index
        self.timestamp = str(datetime.datetime.now())
        self.proof = proof
        self.previous_hash = previous_hash

    def get_hash(self):
        hash = hashlib.sha256()
        hash.update(str(self.previous_hash).encode('utf-8'))
        hash.update(str(self.timestamp).encode('utf-8'))
        hash.update(str(self.index).encode('utf-8'))
        return hash.hexdigest()


class Blockchain:
    """
    BlockChain
        [data1] -> [data2, hash(data1)] -> [data3, hash(data2)]
        proof-of-work --
        blockchain - nodes(компы)
    """

    def __init__(self, calc_complex="00000"):
        self.chain = []
        self.create_block(1, "0")
        self.complex = calc_complex

    def create_block(self, proof, previous_hash):
        index = len(self.chain) + 1
        block = Block(index, proof, previous_hash)
        self.chain.append(block)

        return block

    def get_previous_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, previous_proof, start_proof, stop_proof):
        new_proof = start_proof
        check_proof = False

        while check_proof is False and new_proof <= stop_proof:
            hash_operation = get_sha256(new_proof, previous_proof)

            if self.is_hash_complex_valid(hash_operation):
                check_proof = True
            else:
                new_proof += 1
        if check_proof:
            print("------------------", new_proof)
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


class CoreMiner(multiprocessing.Process):
    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        while True:
            temp_task = self.task_queue.get()

            if temp_task is None:
                self.task_queue.task_done()
                break

            answer = temp_task.process()
            print(answer)
            self.task_queue.task_done()
            if answer:
                print(answer)
                self.result_queue.put(answer)


class Task():
    def __init__(self,
                 blockchain: Blockchain,
                 previous_proof: int,
                 start_proof: int,
                 stop_proof: int):
        self.blockchain = blockchain
        self.previous_proof = previous_proof
        self.start_proof = start_proof
        self.stop_proof = stop_proof

    def process(self):
        return blockchain.proof_of_work(self.previous_proof,
                                        self.start_proof,
                                        self.stop_proof)


# user -> www.vk.ru -> login(eyes) - front -> POST username, password ==> backend - АПИ

app = Flask(__name__)
blockchain = Blockchain(calc_complex="000000")


def mining_proof(blockchain:blockchain)->int:
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block.proof

    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    n_cores = multiprocessing.cpu_count()
    miners = [CoreMiner(tasks, results) for i in range(n_cores)]

    start_proof = 1
    stop_proof = 10 ** (len(blockchain.complex)+1)
    step = (stop_proof - start_proof) // 20
    for miner_core in miners:
        miner_core.start()

    while results.empty():
        print('new section')

        for proof_section in range(start_proof, stop_proof, step):
            task = Task(blockchain,
                        previous_proof,
                        proof_section,
                        proof_section+step)
            tasks.put(task)
            print(proof_section,proof_section+step)
        start_proof = stop_proof
        stop_proof *= 2

        for i in range(n_cores):
            tasks.put(None)
        tasks.join()

    return results.get()
# Graphql, GRPC

# Shop - product API - REST
# POST - create new product
# PUT - change product
# PATCH - change small product
# GET - get list product

@app.route("/multiprocessing", methods=["GET"])
def mp_mine_block():
    proof = mining_proof(blockchain)
    previous_block = blockchain.get_previous_block()
    previous_hash = previous_block.get_hash()
    block = blockchain.create_block(proof, previous_hash)

    response = {
        "message": "Block created",
        "index": block.index,
        "timestamp": block.timestamp,
        "proof": block.proof,
        "previous_hash": block.previous_hash,
        # "executed time in seconds": executed_time.total_seconds()
    }
    return jsonify(response), 200


@app.route("/mine_block", methods=["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block.proof
    # t_begin = datetime.datetime.now()
    proof = blockchain.proof_of_work(previous_proof, 1, 10000000000)
    t_end = datetime.datetime.now()
    # executed_time = t_end - t_begin
    previous_hash = previous_block.get_hash()

    block = blockchain.create_block(proof, previous_hash)

    response = {
        "message": "Block created",
        "index": block.index,
        "timestamp": block.timestamp,
        "proof": block.proof,
        "previous_hash": block.previous_hash,
        # "executed time in seconds": executed_time.total_seconds()
    }

    return jsonify(response), 200


@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = []
    for block in blockchain.chain:
        response.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "proof": block.proof,
            "previous_hash": block.previous_hash
        })

    return jsonify(response), 200


@app.route("/valid", methods=["GET"])
def valid():
    return jsonify({
        "chain_valid": "OK" if blockchain.chain_valid() else "NOT OK"
    }), 200


app.run(host="127.0.0.1", debug=True, port=5000)
