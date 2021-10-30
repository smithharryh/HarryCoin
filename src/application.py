from uuid import uuid4

from flask import Flask, jsonify, request

from src.Blockchain import Blockchain

app = Flask(__name__)

"""
Below create a random name for the node flask is on
"""
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    """
    Endpoint for mine which is a HTTP GET request
    :return: json response containing details of the newly mined block
    """
    lastBlock = blockchain.lastBlock
    lastProof = lastBlock['proof']
    proof = blockchain.proofOfWork(lastProof)

    blockchain.newTransaction(sender="0", recipient=node_identifier, amount=1)
    previousHash = blockchain.hash(lastBlock)
    block = blockchain.newBlock(proof, previousHash)
    response = {
        'message': "New block forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previousHash': block['previousHash']
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def newTransaction():
    """
    Endpoint for newTransaction which is a HTTP POST request
    :return: json response saying transaction will be added to the block
    """
    values = request.get_json()
    requiredFields = ['sender', 'recipient', 'amount']
    if not all(x in values for x in requiredFields):
        return "Missing Values", 400

    index = blockchain.newTransaction(values['sender'], values['recipient'], values['amount'])
    response ={'message': f'Transaction will be added to Block{index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    """
    Endpoint to return the whole blockchain using HTTP GET request
    :return: json response of the chain and its length
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def registerNodes():
    values = request.get_json()
    nodes = values.get['nodes']
    if nodes is None:
        return "Error: List of nodes is not valid", 400

    for node in nodes:
        blockchain.registerNode(node)

    response = {
        'message': 'New nodes have been added',
        'totalNodes': list(blockchain.nodes)
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'Chain has been replaced',
            'newChain': blockchain.chain
        }
    else:
        response = {
            'message': 'Chain is the authority so does not need replacing',
            'chain': blockchain.chain
        }
    return jsonify(response), 200


if __name__ == "__main__":
    """
    runs the server
    """
    app.run(host='localhost', port=12345)
