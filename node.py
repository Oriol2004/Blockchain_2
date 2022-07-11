from uuid import uuid4
from blockchain import Blockchain
from verification import Verification


class Node:
    def __init__(self):
        #self.id = str(uuid4())
        self.id = "Oriol"
        self.blockchain = Blockchain(self.id)

    def get_transaction_value(self):
        # fragt nach Informationen für die neue Transaktion
        tx_recipient = input("Enter the name of the recipient: ")
        tx_amount = float(input("Your transaction amount please; "))
        return (tx_recipient, tx_amount)
        """Returning values with a tuple, works best for mixed data types"""

    def get_user_choice(self):
        # fragt danach was man machen will
        choice = float(input("Your choice: "))
        return choice

    def print_blockchain_elements(self):
        # alle Blöcke von der Blockchain werden nun ausgedrückt
        for block in self.blockchain.chain:
            print("Outputting Block")
            print(block)

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print("Choose")
            print("1 : Add a new transaction")
            print("2 : Output the blockchain")
            print("3 : Mine a new block")
            print("4 : Quit")
            print("5 : Check Transaction validity")
            # fragt nach dem was man machen will
            user_choice = self.get_user_choice()

            if user_choice == 1:
                tx_data = self.get_transaction_value()
                # unpacking der Transaktion durch get_transaction_value def und tx_data wird zur Information
                recipient, amount = tx_data
                # diese Infromationen (tx_data) werden nun zur def add_transaction geschickt
                # wenn Richtig zurückkommt dann wird die Transaktion hinzugefügt
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print("Added transaction")
                else:
                    print("Transaction failed!")

            elif user_choice == 2:
                # drückt die Blockchain aus
                self.print_blockchain_elements()

            elif user_choice == 3:
                self.blockchain.mine_block()

            elif user_choice == 4:
                waiting_for_input = False

            elif user_choice == 5:
                verifier = Verification()
                if verifier.verify_transactions(self.blockchain.open_transactions, self.blockchain.get_balance):
                    print("All transactions are valid")
                else:
                    print("There are invalid transactions")

            elif user_choice != 1. != 2. != 3. != 4. != 5:
                print("Enter a Valid Amount!!!")

                print(40 * "_")
            verifier = Verification()
            if not verifier.verify_chain(self.blockchain.chain):
                self.print_blockchain_elements()
                print("Invalid Blockchain")
                break

            print("Balance of {}: {:6.2f}".format(
                self.id, self.blockchain.get_balance()))
        else:
            print("Done!")
            print(40 * "_")


node = Node()
node.listen_for_input()