from flask import Flask, jsonify, request, redirect, url_for
from blockchain.chain import Blockchain

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
        response["status"] = (
            "in progress" if block.in_progress else "completed"
        )
    else:
        response["status"] = "not found"
    return jsonify(response)


@app.route("/get_chain", methods=["GET"])
def get_chain():
    response = []
    for block in blockchain.chain:
        status = "In progress" if block.in_progress else "Completed"
        response.append(
            {
                "index": block.index,
                "timestamp": block.timestamp,
                "proof": block.proof,
                "previous_hash": block.previous_hash,
                "status": status,
            }
        )

    return jsonify(response), 200


@app.route("/valid", methods=["GET"])
def valid():
    return (
        jsonify(
            {"chain_valid": "OK" if blockchain.chain_valid() else "NOT OK"}
        ),
        200,
    )
