import hashlib
import json

def hash_string_256(string):
    return hashlib.sha256(string).hexdigest()

def hash_block(block):
    hashable_block = block.__dict__.copy()
    hashable_block["transactions"] = [tx.to_ordered_dict() for tx in hashable_block["transactions"]]
    # diese funktion wird beim Minen benutzt, Hashed denn letzten block indem es diese mit einem Bindestrich verbindet
    return hash_string_256(json.dumps(hashable_block, sort_keys=True).encode())
    # creates a str from the block and turns it into a hash  / hexdigest to turn it into a readable string
