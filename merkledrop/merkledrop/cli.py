import argparse
import json

from brownie import network
from web3 import Web3

from . import MerkleDistributor, MerkleProof, Setup, Token


def get_deployment_info(setup_address):
    setup_contract = Setup.Setup(setup_address)
    merkle_distributor_address = setup_contract.merkle_distributor()
    token_address = setup_contract.token()
    return {
        "setup_address": setup_address,
        "merkle_distributor_address": merkle_distributor_address,
        "token_address": token_address,
    }


def handle_get_deployment_info(args: argparse.Namespace):
    network.connect(args.network)
    info = get_deployment_info(args.address)
    print(
        f"Setup address: {info['setup_address']}, Merkle Distributor address: {info['merkle_distributor_address']}, Token address: {info['token_address']}"
    )


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
    print(json.dumps(individual_amounts, indent=2))


def gen_leaf(index, account, amount):
    return Web3.solidityKeccak(
        ["uint256", "address", "uint96"], [index, Web3.toChecksumAddress(account), amount]
    )


def verify(root, leaf, proof):
    computed_hash = leaf
    for element in proof:
        if int(computed_hash, 16) < int(element, 16):
            computed_hash = Web3.solidityKeccak(
                ["bytes32", "bytes32"], [computed_hash, element]
            ).hex()
        else:
            computed_hash = Web3.solidityKeccak(
                ["bytes32", "bytes32"], [element, computed_hash]
            ).hex()
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

def claim_info(args: argparse.Namespace):
    with open(args.infile) as ifp:
        merkle_tree = json.load(ifp)

    claimant_address = list(merkle_tree["claims"].keys())[args.claim]
    claim_info = merkle_tree["claims"][claimant_address]

    print(f"Claimant address: {claimant_address}")
    print(f"Index: {claim_info['index']}")
    print(f"Amount: {int(claim_info['amount'], 16)}")
    print(f"Proof: {' '.join(claim_info['proof'])}")

def claim_all(args: argparse.Namespace):
    network.connect(args.network)
    tx_config = MerkleDistributor.get_transaction_config(args)

    distributor = MerkleDistributor.MerkleDistributor(args.address)

    with open(args.infile) as ifp:
        merkle_tree = json.load(ifp)

    for address, claim_info in merkle_tree["claims"].items():
        index = claim_info["index"]
        amount = int(claim_info["amount"], 16)
        proof = claim_info["proof"]
        distributor.claim(index, address, amount, proof, tx_config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="merkledrop challenge")
    subparsers = parser.add_subparsers()

    deployment_info_parser = subparsers.add_parser("deployment-info")
    Setup.add_default_arguments(deployment_info_parser, False)
    deployment_info_parser.set_defaults(func=handle_get_deployment_info)

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

    merkle_distributor_parser = MerkleDistributor.generate_cli()
    subparsers.add_parser(
        "distributor", parents=[merkle_distributor_parser], add_help=False
    )

    merkle_prover_parser = MerkleProof.generate_cli()
    subparsers.add_parser("prover", parents=[merkle_prover_parser], add_help=False)

    setup_parser = Setup.generate_cli()
    subparsers.add_parser("setup", parents=[setup_parser], add_help=False)

    token_parser = Token.generate_cli()
    subparsers.add_parser("token", parents=[token_parser], add_help=False)

    claim_info_parser = subparsers.add_parser("claim-info")
    claim_info_parser.add_argument("infile")
    claim_info_parser.add_argument("--claim", type=int)
    claim_info_parser.set_defaults(func=claim_info)

    claim_all_parser = subparsers.add_parser("claim-all")
    MerkleDistributor.add_default_arguments(claim_all_parser, True)
    claim_all_parser.add_argument("infile")
    claim_all_parser.set_defaults(func=claim_all)

    args = parser.parse_args()
    args.func(args)
