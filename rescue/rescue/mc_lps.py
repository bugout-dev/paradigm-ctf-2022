import argparse
import sys
import time

from brownie import network

from . import MasterChefLike, UniswapV2PairLike, MockERC20

parser = argparse.ArgumentParser()
MasterChefLike.add_default_arguments(parser, False)
parser.add_argument("--weth", required=True)
parser.add_argument("--mc-helper", required=True)
parser.add_argument("--msg-sender", required=True)

args = parser.parse_args()

network.connect(args.network)

num_lps = 355

mc_contract = MasterChefLike.MasterChefLike(args.address)
for i in range(num_lps):
    try:
        lp_info = mc_contract.pool_info(i)
        lp_token_address = lp_info[0]

        lp_token = MockERC20.MockERC20(lp_token_address)
        lp_token_balance = lp_token.balance_of(args.mc_helper)
        my_lp_token_balance = lp_token.balance_of(args.msg_sender)

        pair_contract = UniswapV2PairLike.UniswapV2PairLike(lp_token_address)
        pair_token_0 = pair_contract.token0()
        pair_token_1 = pair_contract.token1()

        print(
            f"Pool ID: {i}, LP token: {lp_token_address} (helper balance: {lp_token_balance}, my balance: {my_lp_token_balance}, is WETH: {lp_token_address == args.weth}), Token 0: {pair_token_0} (is WETH: {pair_token_0 == args.weth}), Token 1: {pair_token_1} (is WETH: {pair_token_1 == args.weth})"
        )

        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        print(f"Problem with pool {i} -- {repr(e)}")
        continue
