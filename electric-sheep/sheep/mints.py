import argparse
import json

from brownie import network, web3, ZERO_ADDRESS

parser = argparse.ArgumentParser()
parser.add_argument("events", help="Events file")
args = parser.parse_args()

mints = []

with open(args.events) as ifp:
    for line in ifp:
        event = json.loads(line.strip())
        if event["event"] == "Transfer" and event["args"]["from"] == ZERO_ADDRESS:
            mints.append(event)


network.connect("ctf-22")

for mint_event in mints:
    tx_hash = mint_event["transactionHash"]
    tx = web3.eth.getTransaction(tx_hash)
    mint_event["transaction_sender"] = tx["from"]
    mint_event["input"] = tx["input"]
    mint_event["r"] = tx["r"].hex()
    mint_event["s"] = tx["s"].hex()
    mint_event["v"] = tx["v"]

print(json.dumps(mints, indent=2))
