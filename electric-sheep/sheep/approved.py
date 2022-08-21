import argparse
import json

from brownie import network, web3

parser = argparse.ArgumentParser()
parser.add_argument("events", help="Events file")
args = parser.parse_args()

network.connect("ctf-22")

approved_smart_contracts = {}

with open(args.events) as ifp:
    for line in ifp:
        event = json.loads(line.strip())
        if event["event"] == "Approval":
            spender = web3.toChecksumAddress(event["args"]["spender"])
            owner = web3.toChecksumAddress(event["args"]["owner"])
            allowance = event["args"]["value"]
            code = web3.eth.getCode(spender)
            if code is not None and code != "" and code != "0x" and code != "0x0" and code != 0 and code != "0":
                if approved_smart_contracts.get(spender) is None:
                    approved_smart_contracts[spender] = {}
                if approved_smart_contracts[spender].get(owner) is None:
                    approved_smart_contracts[spender][owner] = 0
                approved_smart_contracts[spender][owner] += allowance

print(json.dumps(approved_smart_contracts, indent=2))
