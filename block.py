"""creates the block class"""

from time import time
from utility.printable import Printable

class Block(Printable):
    def __init__(self, index, previous_hash, transactions, nonce, timestamp = None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = time() if timestamp is None else timestamp
        self.transactions = transactions
        self.nonce = nonce

    
