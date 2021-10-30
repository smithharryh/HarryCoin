import hashlib
import json
from time import time

# from src.Block import Block
# from src.Transaction import Transaction
from urllib.parse import urlparse

import requests


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.currentTransactions = []
        self.newBlock(previousHash=1, proof=100)  # Create the genesis block
        self.nodes = set()

    def newBlock(self, proof, previousHash=None):
        """
        Creates a new Block in the chain
        :param proof:  integer proof given by the Proof of Work algorithm
        :param previousHash: hash of the last block in the chain
        :return: a new Block object
        """
        # TODO: Implement block and transaction as class
        # block = Block(index=len(self.chain) + 1,
        #               timestamp=time(),
        #               transactions=self.currentTransactions,
        #               proof=proof,
        #               previousHash=previousHash or self.hash(self.chain[-1]))
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.currentTransactions,
            'proof': proof,
            'previousHash': previousHash or self.hash(self.chain[-1]),
        }
        self.currentTransactions = []
        self.chain.append(block)
        return block

    def newTransaction(self, sender, recipient, amount):
        """
        Create a new transaction to go into the next mined block
        :param sender: address of the sender
        :param recipient: address of the recipient
        :param amount: amount to be send
        :return: last block in the chain which will hold this transaction
        """
        self.currentTransactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return self.lastBlock['index'] + 1

    @staticmethod
    def hash(block):
        """
        Create a SHA-256 hash of a block provided
        :param block: block to be hashed
        :return: 256 hash of block
        """
        blockString = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(blockString).hexdigest()

    @property
    def lastBlock(self):
        """
        Utility method to return the last block in the chain
        :return: Block object of the last block in the chain
        """
        return self.chain[-1]

    def proofOfWork(self, lastProof):
        """
        Proof of work algorithm
        :param lastProof: integer value of last proof
        :return:  integer value
        """
        proof = 0
        while self.validProof(lastProof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def validProof(lastProof, proof):
        f"""
        Validates the proof to check the hash of (lastProof, proof) contains 4 leading zeroes
        :param lastProof: integer value for previous proof
        :param proof: integer value for current proof
        :return: returns a boolean value for if the proof is valid or not
        """
        guess = f'{lastProof}{proof}'.encode()
        guessHash = hashlib.sha256(guess).hexdigest()
        return guessHash[:4] == "0000"

    def registerNode(self, address):
        """
        Add a new node to the list of nodes
        :param address: Location of the node
        """
        parsedURL = urlparse(address)
        self.nodes.add(parsedURL.netloc)

    def validChain(self, chain):
        """
        Determine if a chain is valid
        :param chain: provided chain
        :return: boolean for if the chain is valid
        """

        lastBlock = chain[0]
        currentIndex = 1
        while currentIndex < len(chain):
            block = chain[currentIndex]
            print(f'{lastBlock}')
            print(f'{block}')
            print("\n ------------ \n")

            if block['previousHash'] != self.hash(lastBlock):  # Verify hash
                return False

            if not self.validProof(lastBlock['proof'], block['proof']):  # Verify proof
                return False

            lastBlock = block
            currentIndex += 1

        return True

    def resolve_conflicts(self):
        """
        This is the consensus algorithm, resolving conflicts by replacing the chain with the longest one on the network
        :return: boolean to state whether the chain has been replaced or not
        """

        neighbours = self.nodes
        newChain = None

        maxLength = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > maxLength and self.validChain(chain):
                    maxLength = length
                    newChain = chain

        if newChain:
            self.chain = newChain
            return True

        return False
