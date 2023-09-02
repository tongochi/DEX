from typing import Literal
from requests import get
from time import sleep
from tonsdk.utils import Address

from config import *


def getTonEqivalentJetton(
    poolAddress: str,
    jettonAmount: int,
    testnet: bool = False,
    cooldown: float = 1,
) -> float:
    get_url = GET_METHOD_URL_TESTNET if testnet else GET_METHOD_URL
    url = get_url(poolAddress) + "get_pool_data"

    try:
        poolData = get(url, headers=AUTH_HEADER).json()["stack"]
        sleep(cooldown)

        jettonReserve = int(poolData[0]["num"], 16)
        tonReserve = int(poolData[1]["num"], 16) // 1_000_000_000

        return jettonAmount / jettonReserve * tonReserve
    except Exception as e:
        print(e, 'tonEqivJetton')
        return 0


def getTonEqivalentLp(
    poolAddress: str,
    LpAmount: int,
    testnet: bool = False,
    cooldown: float = 1,
) -> float:
    get_url = GET_METHOD_URL_TESTNET if testnet else GET_METHOD_URL
    url = get_url(poolAddress) + "get_pool_data"

    try:
        poolData = get(url, headers=AUTH_HEADER).json()["stack"]
        sleep(cooldown)
        tonReserve = int(poolData[1]["num"], 16) // 1_000_000_000

        url = get_url(poolAddress) + "get_jetton_data"
        jettonData = get(url, headers=AUTH_HEADER).json()["stack"]
        sleep(cooldown)
        lpTokenSupply = int(jettonData[0]["num"], 16)

        return LpAmount / lpTokenSupply * tonReserve * 2
    except Exception as e:
        print(e, 'tvlLp')
        return 0


def getUsdEqivalent(tonAmount: float, cooldown: float = 1) -> float:
    url = GET_METHOD_URL(TON_JUSDT_POOL) + "get_pool_data"

    try:
        poolData = get(url, headers=AUTH_HEADER).json()["stack"]
        sleep(cooldown)

        jusdtReserve = int(poolData[0]["num"], 16) // 1_000_000
        tonReserve = int(poolData[1]["num"], 16) // 1_000_000_000

        return tonAmount * (jusdtReserve / tonReserve)
    except Exception as e:
        print(e, 'usdEqiv')
        return 0


def getJettonAmount(
    jettonWalletAddress: str,
    testnet: bool = False,
    cooldown: float = 1,
) -> int:
    get_url = GET_METHOD_URL_TESTNET if testnet else GET_METHOD_URL
    base_url = get_url(jettonWalletAddress)
    url = base_url + "get_wallet_data"

    try:
        jettonWalletData = get(url, headers=AUTH_HEADER).json()["stack"]
        sleep(cooldown)
        amount = int(jettonWalletData[0]["num"], 16)
    except Exception as e:
        print(e, 'jettonAmount')
        amount = 0

    return amount


def getNftContent(
    nftAddress: str,
    testnet: bool = False,
    cooldown: float = 1,
) -> Literal[0] | tuple[int, int, int, int]:
    get_url = GET_METHOD_URL_TESTNET if testnet else GET_METHOD_URL
    url = get_url(nftAddress) + "get_nft_content"

    try:
        nftContent = get(url, headers=AUTH_HEADER).json()["stack"]
        sleep(cooldown)
        return (
            int(nftContent[0]["num"], 16),  # start
            int(nftContent[1]["num"], 16),  # period
            int(nftContent[2]["num"], 16),  # amount
            int(nftContent[3]["num"], 16)  # index
        )

    except Exception as e:
        print(e, 'nftBalance')
        return 0


def getStakerData(
    userAddress: str,
    contractAddress: str,
    testnet: bool = False,
    cooldown: float = 0.2,
    prev_nfts: list = []
) -> tuple[float, list[dict]]:
    base_url = TONAPI_URL_TESTNET if testnet else TONAPI_URL
    url = f"{base_url}accounts/{userAddress}/nfts?collection={contractAddress}"

    stackedBalance = 0
    data = []

    nfts_by_address = {}
    for i in prev_nfts:
        nfts_by_address[i["address"]] = i

    try:
        nfts = get(url, headers=AUTH_HEADER).json()["nft_items"]

        for i in nfts:
            nftAddress = Address(i["address"]).to_string(True, True, True)

            if nftAddress in nfts_by_address:
                data.append(nfts_by_address[nftAddress])
                stackedBalance += data[-1]["nftBalance"]
                continue

            sleep(cooldown)
            nft_content = getNftContent(nftAddress, testnet=testnet, cooldown=0)
            assert nft_content != 0
            lockupStart, lockupPeriod, nftBalance, nftIndex = nft_content
            if nftBalance != 0:
                stackedBalance += nftBalance
                data.append({"address": nftAddress, "lockupStart": lockupStart,
                             "lockupPeriod": lockupPeriod, "nftBalance": nftBalance})
            else:
                return 0, []

        return stackedBalance, data
    except Exception as e:
        print(e, 'userBalance')
        return 0, []
