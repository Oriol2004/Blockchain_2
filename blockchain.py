"""erstellt die Blockchain mit allen Attributen"""

# importierte Pakete:
from functools import reduce
import json
import requests

# importierte Dateien:
from nützlich.hash_util import hash_block
from block import Block
from transaction import Transaction
from nützlich.verification import Verification
from wallet import Wallet

MINING_REWARD = 100

#class Blockchain wird erstellt mit allen passenden Attributen
class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, "", [], 99, 0)
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    @property  
    # Falls jemand auf die Chain zugreift
    def chain(self):
        return self.__chain[:]  # with copy

    @chain.setter
    #Gibt der Chain ein Wert
    def chain(self, val):
        self.__chain = val

    #Um die Offenen Transaktionen zu bekommen
    def get_open_transactions(self):
        return self.__open_transactions[:]

    #Funktion um Blockchain und Transaktionen zu laden
    def load_data(self):
        try:
            with open("blockchain-{}.txt".format(self.node_id), mode="r") as f:
                #Blockchain wird gelesen und der neuen Blockchain (updated_blockchain) hinzugeügt
                file_content = f.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx["sender"], tx["recipient"], tx["signature"], tx["amount"]) for tx in block["transactions"]]
                    updated_block = Block(
                        block["index"], block["previous_hash"], converted_tx, block["nonce"], block["timestamp"])
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                #Offene Transaktionen werden gelesen und der neuen Transaktionen (updated_transactions) hinzugefügt
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx["sender"], tx["recipient"], tx["signature"], tx["amount"])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transaction
                #Peer Nodes werden geladen
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
        except (IOError, IndexError):
            pass

    #Funktion um Data zu speichern
    def save_data(self):
        try:
                # aus jedem Block in der Blockchain ein Wörterbuch machen / jede Transaktion muss auch ein Wörterbuch sein
                with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                    saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                        tx.__dict__ for tx in block_el.transactions], block_el.nonce, block_el.timestamp) for block_el in self.__chain]]
                    f.write(json.dumps(saveable_chain))
                    f.write('\n')
                    saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                    f.write(json.dumps(saveable_tx))
                    f.write('\n')
                    f.write(json.dumps(list(self.__peer_nodes)))
        except IOError:
            print("Saving failed")

    #Proof of Work algorithmus um den passenden Hash zu finden/ hier wird auch die Nonce hochgezählt
    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        nonce = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, nonce):
            nonce += 1
        return nonce

    #Das Guthaben für einen Teilnehmer berechnen und zurückgeben.
    def get_balance(self, sender=None):
        
        if sender == None:
            if self.public_key == None:
                return None
            participant = self.public_key
        else:
            participant = sender
        #Holt eine Liste aller gesendeten Münzbeträge für die angegebene Person (leere Listen werden zurückgegeben, wenn die Person NICHT der Absender war)
        #Dies holt gesendete Beträge von Transaktionen, die bereits in Blöcken der Blockchain enthalten waren
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
       
        # Dies holt die gesendeten Beträge der offenen Transaktionen ab (um Doppelausgaben zu vermeiden)
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        print(tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                             if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        # Dies holt die erhaltenen Münzbeträge von Transaktionen, die bereits in Blöcken der Blockchain enthalten waren
        # Offene Transaktionen werden hier ignoriert, da es nicht möglich sein sollte, Münzen auszugeben, bevor die Transaktion bestätigt und in einen Block aufgenommen wurde
        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt)
                                 if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        # Rückgabe des Gesamtsaldos
        return amount_received - amount_sent


    #Gibt den letzten Wert der Blockchain zurück.
    def get_last_blockchain_value(self):
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    #Funktion um Transaktionen hinzuzufügen
    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        transaction = Transaction(sender, recipient, signature, amount)
        #Überprüft die Transaktion
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                #Transaktion wird allen Peer Nodes mitgeteilt
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={
                                                 'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    #Funktion um Block zu schürfen
    def mine_block(self):
        if self.public_key == None:
            return None
        last_block = self.__chain[-1]
        # nimmt den letzten Block um es nachher im Block Header zu tun
        hashed_block = hash_block(last_block)
        nonce = self.proof_of_work()
        # erstellt eine Reward Transaktion welche dann auch im Open Transactions gespeichert wird
        reward_transaction = Transaction(
            "MINING", self.public_key, "", MINING_REWARD)
        # Kopiert die offenen Transaktionen um denen ide reward Transaktion anzuhängen
        copied_transactions = self.__open_transactions[:]
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, nonce)
        for tx in block.transactions:
            if not Wallet.verify_transaction(tx):
                return None
        copied_transactions.append(reward_transaction)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()

        for node in self.__peer_nodes:
            #Der neue Block wird allen Peer Nodes mitgeteilt
            url = "http://{}/broadcast-block".format(node)
            converted_block = block.__dict__.copy()
            converted_block["transactions"] = [
                tx.__dict__ for tx in converted_block["transactions"]]
            try:
                response = requests.post(url, json={"block": converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print("Block declined, needs resolving")
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    #Funktion um den neuen Block hinzuzufügen/ Neuer Hash mit Nonce wird überprüft, last_hash wird überprüft, schlussendlich werden die offenen Transaktionen geleert
    def add_block(self, block):
        transactions = [Transaction(
            tx["sender"], tx["recipient"], tx["signature"], tx["amount"]) for tx in block["transactions"]]
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block["previous_hash"], block["nonce"])
        hashes_match = hash_block(self.chain[-1]) == block["previous_hash"]
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(
            block["index"], block["previous_hash"], transactions, block["nonce"], block["timestamp"])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block["transactions"]:
            for opentx in stored_transactions:
                if opentx.sender == itx["sender"] and opentx.recipient == itx["recipient"] and opentx.amount == itx["amount"] and opentx.signature == itx["signature"]:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print("Item was already removed")
        self.save_data()
        return True
    
    #Funktion um Probleme zwischen Nodes zu lösen/ Länge der Blockchain usw.
    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = "http://{}/chain".format(node) 
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block["index"],block["previous_hash"],[Transaction(tx["sender"],tx["recipient"],tx["signature"],tx["amount"]) for tx in block["transactions"]], block["nonce"],block["tiimestamp"]) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    #Funktion um neue Nodes zu adden
    def add_peer_node(self, node):
        self.__peer_nodes.add(node)
        self.save_data()

    #Funktion um Node zu entfernen
    def remove_peer_node(self, node):
        self.__peer_nodes.discard(node)
        self.save_data()

    #Funktion um die Peer Nodes zu laden
    def get_peer_nodes(self):
        return list(self.__peer_nodes)[:]
