from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
#converts data between binary and ASCII

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None
        

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        #unpacking tuple
        self.private_key = private_key
        self.public_key = public_key
        

    def load_keys(self):
        try:
            with open("wallet.txt", mode = "r") as f: 
                keys = f.readlines()
                public_key = keys[0][:-1]
                private_key = keys[1]
                self.public_key = public_key
                self.private_key = private_key
        except(IOError):
            print("Loading wallet failed")


    def save_keys(self):
        if self.public_key != None and self.private_key != None:
            try:
                with open("wallet.txt", mode="w") as f:
                    f.write(self.public_key)
                    f.write("\n")
                    f.write(self.private_key)
            except(IOError, IndexError):
                print("saving wallet failed")
        else:
            print("Keys are empty")
        

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.public_key()
        #generates a public_key that belongs to that private_key
        return (binascii.hexlify(private_key.exportKey(format = "DER")).decode("ascii"), binascii.hexlify(public_key.exportKey(format = "DER")).decode("ascii"))
        #gives string representation of the private_key/public_key

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(RSA.import_key(binascii.unhexlify(self.private_key)))
        #creating signature identity / private_key is used for signing
        h = SHA256.new((str(sender) + str(recipient) + str(amount)).encode("utf8"))
        signature = signer.sign(h)
        #signing signer with the hash of recipient + sende + amount
        return binascii.hexlify(signature).decode("ascii")

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        h = SHA256.new((str(transaction.sender) + str(transaction.recipient) + str(transaction.amount)).encode("utf8"))
        return verifier.verify(h,binascii.unhexlify(transaction.signature))
