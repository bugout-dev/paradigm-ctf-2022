import argparse
from collections import defaultdict
import json

from web3 import Web3

parser = argparse.ArgumentParser()
parser.add_argument("events", help="Events file")
args = parser.parse_args()

DEFAULT_ACCOUNT_STATE = {"balance": 0, "num_transfers_in": 0, "num_transfers_out": 0, "amount_in": 0, "amount_out": 0}
state = defaultdict(lambda: {**DEFAULT_ACCOUNT_STATE})

with open(args.events) as ifp:
    for line in ifp:
        event = json.loads(line.strip())
        if event["event"] == "Transfer":
            from_address = Web3.toChecksumAddress(event["args"]["from"])
            to_address = Web3.toChecksumAddress(event["args"]["to"])
            value = event["args"]["value"]

            state[from_address]["balance"] -= value
            state[from_address]["num_transfers_out"] += 1
            state[from_address]["amount_out"] += value

            state[to_address]["balance"] += value
            state[to_address]["num_transfers_in"] += 1
            state[to_address]["amount_in"] += value

balances = [v["balance"] for v in state.values()]
num_transfers_in = [v["num_transfers_in"] for v in state.values()]
num_transfers_out = [v["num_transfers_out"] for v in state.values()]
amount_in = [v["amount_in"] for v in state.values()]
amount_out = [v["amount_out"] for v in state.values()]


balances.sort(reverse=True)
num_transfers_in.sort(reverse=True)
num_transfers_out.sort(reverse=True)
amount_in.sort(reverse=True)
amount_out.sort(reverse=True)

top_balances = balances[:10]
top_in = num_transfers_in[:10]
top_out = num_transfers_out[:10]
top_amount_in = amount_in[:10]
top_amount_out = amount_out[:10]

balance_whales = []
out_whales = []
in_whales = []
amount_in_whales = []
amount_out_whales = []

for address, info in state.items():
    if info["balance"] in top_balances:
        balance_whales.append((address, info["balance"]))
    if info["num_transfers_in"] in top_in:
        in_whales.append((address, info["num_transfers_in"]))
    if info["num_transfers_out"] in top_out:
        out_whales.append((address, info["num_transfers_out"]))
    if info["amount_in"] in top_amount_in:
        amount_in_whales.append((address, info["amount_in"]))
    if info["amount_out"] in top_amount_out:
        amount_out_whales.append((address, info["amount_out"]))

print("Addresse with highest balances:")
for address, balance in sorted(balance_whales, key=lambda p: p[1], reverse=True):
    print(f"- Address: {address}, balance: {balance}")

print("Addresse which spent the most:")
for address, amount_out in sorted(amount_out_whales, key=lambda p: p[1], reverse=True):
    print(f"- Address: {address}, amount out: {amount_out}")

print("Addresse which earned the most:")
for address, amount_in in sorted(amount_in_whales, key=lambda p: p[1], reverse=True):
    print(f"- Address: {address}, amount in: {amount_in}")

print("Addresse which spent the most times:")
for address, num_out in sorted(out_whales, key=lambda p: p[1], reverse=True):
    print(f"- Address: {address}, transfers out: {num_out}")

print("Addresse which earned the most times:")
for address, num_in in sorted(in_whales, key=lambda p: p[1], reverse=True):
    print(f"- Address: {address}, transfers in: {num_in}")
