"""URL Routing mit Flask"""
from urllib import response
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain


app = Flask(__name__)
CORS(app)


#Funktion um HTML File "node" zu laden
@app.route("/", methods=["GET"])
def get_node_ui():
    return send_from_directory("ui", "node.html")

#Funktion um HTMl File "network" zu laden
@app.route("/network", methods=["GET"])
def get_network_ui():
    return send_from_directory("ui", "network.html")

#Funktion um eine Wallet zu kreieren und Blockchain zu starten
@app.route("/wallet", methods=["POST"])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key, port)
        response = {
            "public_key": wallet.public_key,
            "private_key":  wallet.private_key,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Saving the keys failed."
        }
        return jsonify(response), 500

#Funktion um die Keys zu laden
@app.route("/wallet", methods=["GET"])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key,port)
        response = {
            "public_key": wallet.public_key,
            "private_key":  wallet.private_key,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Loading the keys failed."
        }
        return jsonify(response), 500

#Funktion um das Guthaben eines Nodes zu bekommen und es zu laden
@app.route("/balance", methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if balance != None:
        response = {
            "message": "Fetched balance succesfully",
            "funds": balance
        }
        return jsonify(response),200
    else:
        response = {
            "message": "Loading balance failed. ",
            "wallet_set_up": wallet.public_key != None
        }
        return jsonify(response), 500


# um die Transaktionen für die anderen Knoten zu verbreiten / open_transactions wird nun für andere Knoten sichtbar sein
@app.route("/broadcast-transaction", methods=["POST"])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            "message": "No data found"
        }
        return jsonify(response), 400
    required = ["sender", "recipient", "amount", "signature"]
    if not all(key in values for key in required):
        response = {
            "message": "Not enough data found"
        }
        return jsonify(response), 400
    success = blockchain.add_transaction(
        values["recipient"], values["sender"], values["signature"], values["amount"], is_receiving=True)
    if success:
        response = {
            "message": "successfully added transaction.",
            "transactions": {
                "sender": values["sender"],
                "recipient": values["recipient"],
                "amount": values["amount"],
                "signature": values["signature"]
            }
        }
        return jsonify(response), 201
    else:
        response = {"message": "creating a transaction failed"}
        return jsonify(response), 500

# um die Blockchain für die anderen Knoten zu verbreiten / der neue Block wird nun für andere Knoten sichtbar sein
@app.route("/broadcast-block", methods= ["POST"])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            "message": "No data found"
        }
        return jsonify(response), 400
    if "block" not in values:
        response = {
            "message": "Some data is missing"
        }
    block = values["block"]
    if block["index"] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block):
            response = {
                "message": "Block added"
            }
            return jsonify(response),201
        else:
            response = {
                "message": "Block invalid"
            }
            return jsonify(response),409
            
    elif block["index"] > blockchain.chain[-1].index:
        response = {"message": "Blockchain seems to differ from local Blockchain!"}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {"message": "Blockchain seems to be shorter block not added!"}
        return jsonify(response), 409

#Funktion um eine Transaktion hinzuzufügen
@app.route('/transaction', methods=["GET","POST"])
def add_transaction():
    if wallet.public_key == None:
        response = {
            'message': 'No wallet set up.'
        }
        return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found.'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing.'
        }
        return jsonify(response), 400
    recipient = values['recipient']
    amount = values['amount']
    #Unterschreiben der Transaktion
    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)
    #Erstellen der neuen Transaktion
    success = blockchain.add_transaction(recipient, wallet.public_key, signature, amount)
    if success:
        response = {
            'message': 'Successfully added transaction.',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature
            },
            'funds': blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Creating a transaction failed.'
        }
        return jsonify(response), 500

#Funktion um einen neuen Block zu schürfen
@app.route("/mine", methods=['POST'])
def mine():
    if blockchain.resolve_conflicts:
        response = {"message": "resolve conflicts first, block not added!"}
    block = blockchain.mine_block()
    if block!= None:
        dict_block = block.__dict__.copy()
        dict_block["transactions"] = [
            tx.__dict__ for tx in dict_block["transactions"]]
        response = {
            "message": "Block added succesfully.",
            "block": dict_block,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Adding a block failed.",
            "wallet_set_up": wallet.public_key != None
        }
        return jsonify(response), 500

#Löst Probleme zwischen den Nodes, fokus lieg bei der länge der Blockchain, die längste Kette wird beibehalten
@app.route("/resolve-conflicts", methods = ["POST"])
def resolve_conflicts():
    replaced = blockchain.resolve()
    if replaced:
        response = {"message": "chain was replaced"}
    else:
        response = {"message": "local chain was kept"}
    return jsonify(response), 200
    
#Sendet die "open_transactions", in Form von einem Wörterbuch, zurück
@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200

#Stellt die Kette dar, jeder Block wird zu einem Wörterbuch indem jede Transaktion auch zu einem Wörterbuch wird
@app.route("/chain", methods=["GET"])
def get_chain():
    chain_snapshot = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain_snapshot]
    for dict_block in dict_chain:
        dict_block["transactions"] = [
            tx.__dict__ for tx in dict_block["transactions"]]
    return jsonify(dict_chain), 200

#Funktion um den neuen Node zu adden
@app.route("/node", methods=["POST"])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            "message": "No data atached."
        }
        return jsonify(response), 400
    if "node" not in values:
        response = {
            "message": "No node found"
        }
        return jsonify(response), 400
    node = values["node"]
    blockchain.add_peer_node(node)
    response = {
        "message": "Node added successfully",
        "all_nodes": blockchain.get_peer_nodes()
    }
    return jsonify(response), 201

#Funktion um Nodes zu löschen
@app.route("/node/<node_url>", methods=["DELETE"])
def remove_node(node_url):
    if node_url == "" or node_url == None:
        response = {
            "message": "No node found"
        }
        return jsonify(response), 400
    blockchain.remove_peer_node(node_url)
    response = {
        "message": blockchain.get_peer_nodes()
    }
    return jsonify(response), 200

#Sendet als Antwort alle peer nodes
@app.route("/nodes", methods=["GET"])
def get_nodes():
    nodes = blockchain.get_peer_nodes()
    response = {
        "all_nodes": nodes
    }
    return jsonify(response), 200

#Startet Programm mit dem Passenden port
if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(port)
    blockchain = Blockchain(wallet.public_key,port)
    app.run(host="0.0.0.0", port=port, debug=True)
