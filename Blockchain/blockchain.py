"""creates the Blockchain with all attributes"""

# imported packets:
import functools
import json




# imported files:
from utility.hash_util import hash_block
from block import Block
from transaction import Transaction
from utility.verification import Verification
from wallet import Wallet

MINING_REWARD = 100


class Blockchain:
    def __init__(self,hosting_node_id):
        genesis_block = Block(0, "", [], 99, 0)
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id
    
    @property #what do I want to return if someone accesses Chain
    def chain(self):
        return self.__chain[:] #with copy

    @chain.setter
    def chain(self,val):
        self.__chain = val


    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open("blockchain.txt", mode="r") as f:
                # file_content = pickle.load(f.read())
                file_content = f.readlines()
                # blockchain = file_content["chain"]
                # open_transactions = file_content["ot"]
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx["sender"], tx["recipient"], tx["signature"], tx["amount"]) for tx in block["transactions"]]
                    updated_block = Block(
                        block["index"], block["previous_hash"], converted_tx, block["nonce"], block["timestamp"])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx["sender"], tx["recipient"],tx["signature"], tx["amount"])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            pass

    def save_data(self):
        try:
            with open("blockchain.txt", mode="w") as f:
                # making a dictionnaire out of every Block in Blockchain / every transaction needs to be a dictionnaire to
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                    tx.__dict__ for tx in block_el.transactions], block_el.nonce, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
                # save_data= {
                # "chain": blockchain
                #     "ot": open_transactions
                # }
                # f.write(pickle.dumps(blockchain))
        except IOError:
            print("Saving failed")

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        nonce = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, nonce):
            nonce += 1
        return nonce

    def get_balance(self):
        participant = self.hosting_node

        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        # gets all the Mooney payed by someone by checking the whole blockchain
        amount_sent = functools.reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

        tx_recipient = [[tx.amount for tx in block.transactions
                        if tx.recipient == participant] for block in self.__chain]
        amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(
            tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

        return amount_recieved - amount_sent

    def get_last_blockchain_value(self):
        # sendet den letzten Block Value sozusagen den vorherigen Hash
        """Returns the last Value of the Blockchxain."""
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]


    def add_transaction(self, recipient, sender, signature, amount=1): 
        if self.hosting_node == None:
            return False
        # Erstellen der transaction als dictionnaire, mit informationen die von get_transaction_value geholt wurden
        transaction = Transaction(sender, recipient, signature, amount)
        # Transaktion Verifizieren mit def verify_transaction
        if Verification.verify_transaction(transaction, self.get_balance):
            # falls Transaktion g??ltig dann f??ge die neue Teilnehmer hinzu
            # und f??ge die Transaktion den offenen Transaktionen hin
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        if self.hosting_node == None:
            return False
        last_block = self.__chain[-1]
        # nimmt den letzten Block um es nachher im Block Header zu tun
        hashed_block = hash_block(last_block)
        nonce = self.proof_of_work()
        # erstellt eine Reward Transaktion welche dann auch im Open Transactions gespeichert wird
        reward_transaction = Transaction("MINING", self.hosting_node,"", MINING_REWARD)
        # Kopiert die offenen Transaktionen um denen ide reward Transaktion anzuh??ngen
        copied_transactions = self.__open_transactions[:]
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, nonce) 
        for tx in block.transactions:
            if not Wallet.verify_transaction(tx):
                return False
        copied_transactions.append(reward_transaction)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        self.load_data()
        return True

    # Put together all Values of the last Block with a for Loop, to
    # hash the Block for key in last_block / keys is used in a dictionary
    # erstellt einen neuen Block mit dem previous Block nimmt die l??nge des BLocks und die Transaktionen
    # f??gt den Block den Transaktionen hinzu
