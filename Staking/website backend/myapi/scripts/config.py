import os

TON_API_KEY = os.environ.get("TONAPI_TOKEN", "")
AUTH_HEADER = {'Authorization': f'Bearer {TON_API_KEY}'}
TONAPI_REQUESTS = int(os.environ.get("TONAPI_REQUESTS", '1'))

TONAPI_URL_TESTNET = "https://testnet.tonapi.io/v2/"
GET_METHOD_URL_TESTNET = lambda x: TONAPI_URL_TESTNET + f"blockchain/accounts/{x}/methods/"

TONAPI_URL = "https://tonapi.io/v2/"
GET_METHOD_URL = lambda x: TONAPI_URL + f"blockchain/accounts/{x}/methods/"

TON_JUSDT_POOL = os.environ.get("TON_JUSDT_POOL", "EQAKleHU6-eGDQUfi4YXMNve4UQP0RGAIRkU4AiRRlgDUbaM")

OP_CODES = {
    "nft_ownership_assigned": "0x05138d91",
    "jetton_notify": "0x7362d09c",
    "jetton_transfer": "0x0f8a7ea5",
    "nft_transferred": "0x9cf42a7d"
}
