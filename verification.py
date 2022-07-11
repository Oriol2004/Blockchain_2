from hash_util import hash_string_256, hash_block


class Verification:
    def valid_proof(self, transactions, last_hash, nonce):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) +
                 str(last_hash) + str(nonce)).encode()
        guess_hash = hash_string_256(guess)
        print(guess_hash)
        return(guess_hash[0:3]) == "000"
        # to check if the first characters are equal to 0

    def verify_chain(self, blockchain):
        # überprüft die Blockchain indem es denn vorherigen hash mit dem von der Blockchain
        for (index, block) in enumerate(blockchain):
            if index == 0:
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not self.valid_proof(block.transactions[:-1], block.previous_hash, block.nonce):
                print("Proof of Work is invalid")
                return False
                # [:-1] to get the reward transaction away
        return True

    def verify_transactions(self, open_transactions, get_balance):
        # alle transactionen in open transactions werden durch die Funktion verify_transactions überprüft
        return all([self.verify_transaction(tx, get_balance) for tx in open_transactions])

    def verify_transaction(self, transaction, get_balance):
        # holt den Kontostand des senders der Transaktion
        sender_balance = get_balance()
        # returnt richtig wenn die Balance auch grösser ist als der Betrag das er senden will
        return sender_balance >= transaction.amount
