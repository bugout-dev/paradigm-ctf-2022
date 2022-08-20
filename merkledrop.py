import argparse
import json

from web3 import Web3

def score_validation(args: argparse.Namespace):
    with open(args.infile) as ifp:
        merkle_tree = json.load(ifp)

    token_total = int(merkle_tree["tokenTotal"], 16)
    individual_amounts = {}
    sum_individual = 0
    for address, info in merkle_tree["claims"].items():
        individual_amount = int(info["amount"], 16)
        individual_amounts[address] = individual_amount
        sum_individual += individual_amount

    print(token_total, sum_individual)

def gen_leaf(index, account, amount):
    return Web3.solidityKeccak(["uint256", "address", "uint96"], [index, account, amount])

def verify(root, leaf, proof):
    computed_hash = leaf
    for element in proof:
        if int(computed_hash, 16) < int(element, 16):
            computed_hash = Web3.solidityKeccak(["bytes32", "bytes32"], [computed_hash, element]).hex()
        else:
            computed_hash = Web3.solidityKeccak(["bytes32", "bytes32"], [element, computed_hash]).hex()
    return computed_hash == root

def handle_gen_leaf(args: argparse.Namespace):
    leaf_raw = gen_leaf(args.index, args.account, args.amount)
    leaf = leaf_raw.hex()
    print(leaf)

def handle_verify(args: argparse.Namespace):
    print(verify(args.root, args.leaf, args.proof))

def collide(args: argparse.Namespace):
    merkle_root = args.root
    print(f"Merkle root: {merkle_root}")

    for index in range(1000000000):
        print(f"Checking index: {index}")
        leaf_raw = gen_leaf(index, args.account, args.amount)
        leaf = leaf_raw.hex()
        print(f"Leaf: {leaf}")
        if leaf == merkle_root:
            print("Collision!")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="merkledrop challenge")
    subparsers = parser.add_subparsers()

    amount_parser = subparsers.add_parser("amount")
    amount_parser.add_argument("infile")
    amount_parser.set_defaults(func=score_validation)

    gen_leaf_parser = subparsers.add_parser("gen-leaf")
    gen_leaf_parser.add_argument("--index", type=int, required=True)
    gen_leaf_parser.add_argument("--account", required=True)
    gen_leaf_parser.add_argument("--amount", type=int, required=True)
    gen_leaf_parser.set_defaults(func=handle_gen_leaf)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("--root", required=True)
    verify_parser.add_argument("--leaf", required=True)
    verify_parser.add_argument("--proof", nargs="*")
    verify_parser.set_defaults(func=handle_verify)

    collide_parser = subparsers.add_parser("collide")
    collide_parser.add_argument("--root", required=True)
    collide_parser.add_argument("--account", required=True)
    collide_parser.add_argument("--amount", type=int, required=True)
    collide_parser.set_defaults(func=collide)

    args = parser.parse_args()
    args.func(args)
