import argparse
import json

from brownie import network, web3, ZERO_ADDRESS
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("events", help="Events file")
args = parser.parse_args()

events = []

with open(args.events) as ifp:
    for line in ifp:
        event = json.loads(line.strip())
        events.append(event)


network.connect("ctf-22")

for item in tqdm(events):
    tx_hash = item["transactionHash"]
    tx = web3.eth.getTransaction(tx_hash)
    item["transaction_sender"] = tx["from"]
    item["transaction_recipient"] = tx.get("to")
    item["input"] = tx["input"]
    item["r"] = tx["r"].hex()
    item["s"] = tx["s"].hex()
    item["v"] = tx["v"]

for event in events:
    print(json.dumps(event))
