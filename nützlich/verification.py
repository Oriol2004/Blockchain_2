"""Stellt Verifikationshilfsmethoden zur Verfügung"""
from nützlich.hash_util import hash_string_256, hash_block
from wallet import Wallet


class Verification:

    @staticmethod
    #Funktion um den Passenden Hash zu finden, hasht Transaktionen, letzten Hash und Nonce zusammen
    def valid_proof(transactions, last_hash, nonce):
        guess = (str([tx.to_ordered_dict() for tx in transactions]
                     ) + str(last_hash) + str(nonce)).encode()

        guess_hash = hash_string_256(guess)
        return guess_hash[0:4] == '0000'

    @classmethod
    #Funktion um die aktuelle Blockchain zu überprüfen und gibt True zurück, wenn sie gültig ist, sonst False.
    def verify_chain(cls, blockchain):
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.nonce):
                print('Proof of work is invalid')
                return False
        return True

    @staticmethod
    #Funktion um die Transaktionen zu Validieren, Überprüft das Guthaben des Senders
    def verify_transaction(transaction, get_balance, check_funds=True):
        if transaction.sender == transaction.recipient:
            return False

        if check_funds:
            sender_balance = get_balance(transaction.sender)
            return sender_balance >= transaction.amount and Wallet.verify_transaction(transaction)
        else:
            return Wallet.verify_transaction(transaction)

    @classmethod
    #Validiert alle Transaktionen in "open_transactions" mithilfe der Funktion verify_transaction 
    def verify_transactions(cls, open_transactions, get_balance):
        """Verifies all open transactions."""
        return all([cls.verify_transaction(tx, get_balance, False) for tx in open_transactions])
