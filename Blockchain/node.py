"""the whole Node system with user interface"""

from uuid import uuid4
from blockchain import Blockchain
from utility.verification import Verification
from wallet import Wallet



class Node:
    def __init__(self):
        #self.wallet = str(uuid4())
        self.wallet = Wallet()
        self.wallet.create_keys()
        self.blockchain = Blockchain(self.wallet.public_key)

    def get_transaction_value(self):
        # fragt nach Informationen für die neue Transaktion
        tx_recipient = input("Enter the name of the recipient: ")
        tx_amount = float(input("Your transaction amount please; "))
        return (tx_recipient, tx_amount)
        """Returning values with a tuple, works best for mixed data types"""

    def get_user_choice(self):
        # fragt danach was man machen will
        choice = (input("Your choice: "))
        return choice

    def print_blockchain_elements(self):
        # alle Blöcke von der Blockchain werden nun ausgedrückt
        for block in self.blockchain.chain :
            print("Outputting Block")
            print(block)

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print("Choose")
            print("1: Add a new transaction")
            print("2: Output the blockchain")
            print("3: Mine a new block")
            print("4: Check Transaction validity")
            print("5: Create wallet")
            print("6: Load wallet")
            print("7: Save Keys")
            print("q: Quit")
            # fragt nach dem was man machen will
            user_choice = self.get_user_choice()

            if user_choice == "1":
                tx_data = self.get_transaction_value()
                # unpacking der Transaktion durch get_transaction_value def und tx_data wird zur Information
                recipient, amount = tx_data
                # diese Infromationen (tx_data) werden nun zur def add_transaction geschickt
                # wenn Richtig zurückkommt dann wird die Transaktion hinzugefügt
                signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature , amount=amount):
                    print("Added transaction")
                else:
                    print("Transaction failed!")

            elif user_choice == "2":
                # drückt die Blockchain aus
                self.print_blockchain_elements()

            elif user_choice == "3":
                if not self.blockchain.mine_block():
                    print("Mining failed, not found wallet!")


            elif user_choice == "q":
                waiting_for_input = False

            elif user_choice == "4":
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print("All transactions are valid")
                else:
                    print("There are invalid transactions")

            elif user_choice == "5":
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_choice == "6":
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)

            elif user_choice == "7":
                self.wallet.save_keys()
            
            if not Verification.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print("Invalid Blockchain")
                break

            print("Balance of {}: {:6.2f}".format(
                self.wallet.public_key, self.blockchain.get_balance()))
        else:
            print("Done!")
            print(40 * "_") 

if __name__ == "__main__":
    node = Node()
    node.listen_for_input()
