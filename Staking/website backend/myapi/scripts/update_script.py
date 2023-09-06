import psycopg2
import websocket
import sys
import traceback
import tongochi_db

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(1, BASE_DIR.joinpath("mysite").__str__())

from settings import *  # type: ignore
from functions import *
from time import time
from json import loads, dumps
from threading import Thread
from tonsdk.utils import Address  # type: ignore
from tonsdk.boc import Cell, Slice  # type: ignore


conn = psycopg2.connect(
    dbname=DB_NAME,  # type: ignore
    user=DB_USER,  # type: ignore
    password=DB_PASSWORD,  # type: ignore
    host=DB_HOST,  # type: ignore
    port=DB_PORT  # type: ignore
)
conn.autocommit = True
cursor = conn.cursor()


def getJettonPrices() -> dict[str, float]:
    cursor.execute("""
        SELECT
            name,
            "stonfiPoolAddress",
            "jettonType"
        FROM myapi_pool
    """)
    pools = cursor.fetchall()
    jetton_prices: dict[str, float] = {}
    for elem in pools:
        pool_name, ston_fi_pool, jetton_type = elem
        jetton_prices[pool_name] = getTonEquivalent(jetton_type, ston_fi_pool, 10 ** 9, False, 0)
    return jetton_prices


def updateNftCollections(cooldown: float = 1):
    cursor.execute("""SELECT name, "contractAddress" FROM myapi_pool""")
    pools = cursor.fetchall()
    for pool in pools:
        db_items = tongochi_db.get_all_collection_items(pool[0] + '_staking')
        onchain_items = []
        offset = 0
        while True:
            url = f'{TONAPI_URL}nfts/collections/{pool[1]}/items?offset={offset}'
            items_slice = get(url, headers=AUTH_HEADER).json()["nft_items"]
            items_slice = list(map(lambda x: Address(x["address"]).to_string(True, True, True), items_slice))
            onchain_items.extend(items_slice)
            if len(items_slice) < 1000:
                break
            offset += 1000

        for item_address in onchain_items:
            if item_address not in db_items:
                item_data = getNftContent(item_address, False, cooldown)
                lockup_start, lockup_period, staked_amount, index = item_data
                tongochi_db.insert_staking_nft_item(
                    jetton_name=pool[0],
                    index=index,
                    address=item_address,
                    lockup_start=lockup_start,
                    lockup_period=lockup_period,
                    staked_amount=staked_amount
                )
    print("finish updating nft content")


def updatePools(cooldown: float = 1):
    cursor.execute(""" SELECT name, "jettonWalletAddress", testnet FROM myapi_pool """)
    pools = cursor.fetchall()
    jettonPrices = getJettonPrices()
    oneTon = getUsdEqivalent(1, cooldown)
    for pool in pools:
        poolName, jettonWallet, testnet = pool
        jettonTvl = getJettonAmount(jettonWallet, testnet, cooldown)
        tonTvl = jettonTvl / 10 ** 9 * jettonPrices[poolName]
        usdTvl = tonTvl * oneTon

        if usdTvl > 100:
            usdTvl = int(usdTvl)
            tonTvl = int(tonTvl)
        else:
            usdTvl = round(usdTvl, 1)
            tonTvl = round(tonTvl, 1)

        if usdTvl != 0:
            print(f'update {poolName} tvls', jettonTvl, tonTvl, usdTvl)
            cursor.execute(f"""
                UPDATE myapi_pool
                SET
                    "jettonTvl" = {jettonTvl},
                    "tonTvl" = {tonTvl},
                    "usdTvl" = {usdTvl}
                WHERE name = '{poolName}'
            """)
        else:
            print(f'{poolName} usdTvl = ', usdTvl, " skipping updating pool tvl")


def addStakers(cooldown: float = 1):
    cursor.execute("""SELECT id, "poolName", "stakerAddress" FROM myapi_staker""")
    stakers = cursor.fetchall()

    if stakers:
        lastId = max(stakers, key=lambda t: t[0])[0]
    else:
        lastId = 0

    stakersByPool: dict[str, set[str]] = {}
    for staker in stakers:
        _, poolName, stakerAddress = staker

        if poolName not in stakersByPool:
            stakersByPool[poolName] = {stakerAddress}
        else:
            stakersByPool[poolName].add(stakerAddress)

    stakersToDelete = []
    stakersToAdd = []
    availablePools = []

    cursor.execute("""SELECT name, "contractAddress", testnet FROM myapi_pool""")
    pools = cursor.fetchall()

    for pool in pools:
        poolName, contractAddress, testnet = pool

        availablePools.append(poolName)

        base_url = TONAPI_URL_TESTNET if testnet else TONAPI_URL

        items = []
        offset = 0

        while True:
            url = f'{base_url}nfts/collections/{contractAddress}/items?offset={offset}'
            items_slice = get(url, headers=AUTH_HEADER).json()["nft_items"]
            items.extend(items_slice)

            if len(items_slice) < 1000:
                break

            offset += 1000

        sleep(cooldown)

        holders = set()
        for item in items:
            holderAddress = Address(item["owner"]["address"]).to_string(True, True, True)
            if holderAddress != contractAddress:
                holders.add(holderAddress)

        for staker in stakers:
            stakerId, stakerPool, stakerAddress = staker
            if stakerPool == poolName and stakerAddress not in holders:
                stakersToDelete.append(stakerId)

        for holder in holders:
            if poolName not in stakersByPool or holder not in stakersByPool[poolName]:
                lastId += 1
                stakersToAdd.append(f"({lastId}, '{holder}', '{poolName}', {testnet})")

    for pool in stakersByPool:
        if pool not in availablePools:
            for i in stakersByPool[pool]:
                stakersToDelete.append(list(filter(lambda x: x[1] == pool and x[2] == i,
                                                   stakers))[0][0])

    if stakersToDelete:
        cursor.execute(f"""
            DELETE FROM myapi_staker
            WHERE array_position(ARRAY{stakersToDelete}, id) IS NOT NULL
        """)
    if stakersToAdd:
        cursor.execute(f"""
            INSERT INTO myapi_staker (id, "stakerAddress", "poolName", testnet)
            VALUES {', '.join(stakersToAdd)}
        """)


def updateDeveloperPoints(cooldown: float) -> None:
    jettonPrices = getJettonPrices()
    oneTon = getUsdEqivalent(1, cooldown)
    cursor.execute("""SELECT "stakerAddress", "poolName", "stakerNftItems" FROM myapi_staker""")
    stakers = cursor.fetchall()
    NUMBER_OF_SECONDS_IN_DAY = 86400
    pointsByAddress = {}
    for staker in stakers:
        staker_address, pool_name, nfts = staker
        stakerBalance = 0
        for nft in nfts:
            if nft['lockupPeriod'] >= 14 * NUMBER_OF_SECONDS_IN_DAY:
                stakerBalance += nft['nftBalance']
        multiplier = {
            'PET': 100,
            'LP-PET-TON': 150,
        }.get(pool_name, 0) / 100
        pointsToAdd = stakerBalance / 10 ** 9 * jettonPrices[pool_name] * oneTon * multiplier
        curPoints = pointsByAddress.get(staker_address, 0)
        pointsByAddress[staker_address] = curPoints + pointsToAdd

    for staker_address in pointsByAddress:
        amountOfPoints = int(pointsByAddress[staker_address])
        if amountOfPoints > 0:
            tongochi_db.add_developer_points(wallet_address=staker_address, amount=amountOfPoints)


def updateStakers(cooldown: float = 0.2, initial=False):
    cursor.execute(""" SELECT name, "contractAddress" FROM myapi_pool """)
    pools = cursor.fetchall()
    nameToContract: dict[str, str] = {pool[0]: pool[1] for pool in pools}

    cursor.execute("""
        SELECT
            id,
            "poolName",
            "stakerAddress",
            "stakedJettons",
            "stakerNftItems"
        FROM myapi_staker
    """)
    stakers = cursor.fetchall()
    jettonPrices = getJettonPrices()

    for staker in stakers:
        staker_id, staker_pool_name, staker_address, stakedJettons, prev_nfts = staker
        prev_nfts = prev_nfts if prev_nfts else []

        contract_address = nameToContract[staker_pool_name]
        if initial:
            staker_data = getStakerData(
                userAddress=staker_address,
                contractAddress=contract_address,
                testnet=False,
                cooldown=cooldown,
                prev_nfts=prev_nfts
            )
            stakedJettons, nfts = staker_data
        else:
            nfts = prev_nfts

        tonEquivalent = stakedJettons / 10 ** 9 * jettonPrices[staker_pool_name]
        tonEquivalent = round(tonEquivalent, 2)

        if initial:
            cursor.execute(f"""
                UPDATE myapi_staker
                SET
                    "stakedJettons" = {stakedJettons},
                    "tonEquivalent" = {tonEquivalent},
                    "stakerNftItems" = '{dumps(nfts)}'::json
                WHERE id={staker_id}
            """)
        else:
            cursor.execute(f"""
                UPDATE myapi_staker
                SET
                    "tonEquivalent" = {tonEquivalent}
                WHERE id={staker[0]}
            """)


def find_tx_by_hash(source: dict, hash: str):
    stack: list = source.get("children", [])
    while stack:
        item = stack.pop(0)
        if item["transaction"]["hash"] == hash:
            return item
        children = item.get("children", [])
        stack.extend(children)

    return []


def find_tx_by_op_code(source: dict, op_code: str):
    stack: list = source.get("children", [])
    while stack:
        item = stack.pop(0)
        item_op_code = item["transaction"]["in_msg"].get("op_code")
        if item_op_code == op_code:
            return item
        children = item.get("children", [])
        stack.extend(children)

    return []

def connect_to_websocket(connection_params: dict):
    ws = websocket.WebSocket()
    ws.connect("wss://tonapi.io/v2/websocket", header=[f'"Authorization": "Bearer {TON_API_KEY}"'])

    ws.send(dumps(connection_params))
    return ws


def reconnect_to_db_1():
    global conn
    global cursor
    try:
        cursor.close()
        conn.close()
    except:
        pass
    conn = psycopg2.connect(
        dbname=DB_NAME,  # type: ignore
        user=DB_USER,  # type: ignore
        password=DB_PASSWORD,  # type: ignore
        host=DB_HOST,  # type: ignore
        port=DB_PORT  # type: ignore
    )
    conn.autocommit = True
    cursor = conn.cursor()


def update_websocket():
    connection_params = {"id": 1, "jsonrpc": "2.0", "method": "subscribe_account", "params": []}
    cursor.execute("""
        SELECT
            "contractAddress",
            name,
            "jettonWalletAddress",
            "stonfiPoolAddress",
            "jettonType",
            "jettonTvl",
            "tonTvl"
        FROM myapi_pool
    """)
    pools = cursor.fetchall()
    pools_by_address = {}
    for i in pools:
        pools_by_address[i[0]] = i[1:]
        connection_params["params"].append(i[0])

    ws = connect_to_websocket(connection_params)

    cd = 3 / TONAPI_REQUESTS
    while True:
        need_update = 0
        sleep(cd)
        try:
            message = loads(ws.recv())
            if message["method"] == "account_transaction":
                tx_hash = message["params"]["tx_hash"]
                trace = get(TONAPI_URL + "traces/" + tx_hash).json()
                with open("test.json", 'w') as f:
                    f.write(dumps(trace))
                main_tx = find_tx_by_hash(trace, tx_hash)
                in_msg: dict = main_tx["transaction"]["in_msg"]

                # if in_msg["value"] <= 50000000:
                #     continue

                pool_address = Address(message["params"]["account_id"]).to_string(True, True, True)
                pool_data = pools_by_address[pool_address]
                pool_name, pool_wallet, pool_stonfi, jetton_type, jetton_tvl, ton_tvl = pool_data

                operation = in_msg.get("op_code")
                print(operation)
                if operation == OP_CODES["nft_transferred"]:
                    nft_address = Address(in_msg["source"]["address"]).to_string(True, True, True)

                    raw_body: str = in_msg["raw_body"]
                    body_slice: Slice = Cell.one_from_boc(raw_body).begin_parse()
                    body_slice.skip_bits(96)
                    prev_owner = body_slice.read_msg_addr().to_string(True, True, True)
                    new_owner = body_slice.read_msg_addr().to_string(True, True, True)

                    nft_content = getNftContent(nft_address, False, 0)
                    if not nft_content:
                        continue

                    lockup_start, lockup_period, nft_balance, index = nft_content
                    nft_content_json = {"address": nft_address, "lockupStart": lockup_start,
                                        "lockupPeriod": lockup_period, "nftBalance": nft_balance}
                    nft_address_parsed = get(GET_METHOD_URL(pool_address) +
                                             f'get_nft_address_by_index?args={index}').json()["decoded"]["address"]
                    if Address(nft_address_parsed).to_string(True, True, True) != nft_address:  # check that msg was send by nft from right collection
                        continue

                    one_token = getTonEquivalent(jetton_type, pool_stonfi, nft_balance, False, 0)

                    # update prev owner
                    cursor.execute(f"""SELECT id, "stakedJettons", "tonEquivalent", "stakerNftItems" FROM myapi_staker
                                WHERE "stakerAddress"='{prev_owner}' AND "poolName"='{pool_name}'""")
                    prev_owner_data = cursor.fetchone()
                    if prev_owner_data:
                        staker_id, staked_jettons, staker_ton_equivalent, staker_nfts = prev_owner_data
                        staked_jettons -= nft_balance
                        staker_ton_equivalent = nft_balance / 10 ** 9 * one_token
                        for i in range(len(staker_nfts)):
                            if staker_nfts[i]["address"] == nft_address:
                                del staker_nfts[i]
                                break
                        if not staker_nfts:
                            cursor.execute(f"""DELETE FROM myapi_staker WHERE id={staker_id}""")
                        else:
                            cursor.execute(f"""UPDATE myapi_staker
                                            SET "stakedJettons"={staked_jettons}, "tonEquivalent"={staker_ton_equivalent},
                                                "stakerNftItems"='{dumps(staker_nfts)}'::json WHERE id={staker_id}""")

                    # update new owner
                    cursor.execute(f"""SELECT id, "stakedJettons", "tonEquivalent", "stakerNftItems" FROM myapi_staker
                                WHERE "stakerAddress"='{new_owner}' AND "poolName"='{pool_name}'""")
                    new_owner_data = cursor.fetchone()
                    if not new_owner_data:
                        cursor.execute("""SELECT MAX(id) FROM myapi_staker""")
                        new_staker_id = cursor.fetchone()[0] + 1
                        cursor.execute(f"""INSERT INTO myapi_staker (id, "stakerAddress", "poolName", "stakedJettons", "tonEquivalent",
                                       "stakerNftItems") VALUES ({new_staker_id}, '{new_owner}', '{pool_name}', {nft_balance},
                                       {nft_balance / 10 ** 9 * one_token}, '[{dumps(nft_content_json)}]'::json)""")
                    else:
                        staker_id, staked_jettons, staker_ton_equivalent, staker_nfts = new_owner_data
                        staked_jettons += nft_balance
                        staker_ton_equivalent = staked_jettons / 10 ** 9 * one_token
                        staker_nfts.append(nft_content_json)

                        cursor.execute(f"""UPDATE myapi_staker
                                        SET "stakedJettons"={staked_jettons}, "tonEquivalent"={staker_ton_equivalent},
                                            "stakerNftItems"='{dumps(staker_nfts)}'::json WHERE id={staker_id}""")

                elif operation == OP_CODES["nft_ownership_assigned"]:
                    staker_address = Address(in_msg["decoded_body"]["prev_owner"]).to_string(True, True, True)
                    cursor.execute(f"""SELECT id, "stakedJettons", "tonEquivalent", "stakerNftItems" FROM myapi_staker
                                WHERE "stakerAddress"='{staker_address}' AND "poolName"='{pool_name}'""")
                    staker_data = cursor.fetchone()

                    if not staker_data:
                        staker_data = (2 ** 31 - 1, 0, 0, [])

                    nft_address = Address(in_msg["source"]["address"]).to_string(True, True, True)

                    jetton_transfer_tx = find_tx_by_op_code(main_tx, OP_CODES["jetton_transfer"])
                    if not jetton_transfer_tx:
                        continue
                    jetton_transfer_message = jetton_transfer_tx["transaction"]["in_msg"]
                    unlocked_jettons = int(jetton_transfer_message["decoded_body"]["amount"])

                    staker_id, staked_jettons, staker_ton_equivalent, staker_nfts = staker_data
                    one_token = getTonEquivalent(jetton_type, pool_stonfi, unlocked_jettons, False, 0)

                    jetton_tvl -= unlocked_jettons
                    ton_tvl = jetton_tvl / 10 ** 9 * one_token

                    staked_jettons -= unlocked_jettons
                    staker_ton_equivalent = staked_jettons / 10 ** 9 * one_token
                    for i in range(len(staker_nfts)):
                        if staker_nfts[i]["address"] == nft_address:
                            del staker_nfts[i]
                            break

                    if not staker_nfts:
                        cursor.execute(f"""DELETE FROM myapi_staker WHERE id={staker_id}""")
                    else:
                        cursor.execute(f"""UPDATE myapi_staker
                                        SET "stakedJettons"={staked_jettons}, "tonEquivalent"={staker_ton_equivalent},
                                            "stakerNftItems"='{dumps(staker_nfts)}'::json WHERE id={staker_id}""")

                    cursor.execute(f"""UPDATE myapi_pool SET "jettonTvl"={jetton_tvl}, "tonTvl"={ton_tvl}
                                    WHERE name='{pool_name}'""")

                    tongochi_db.deactivate_nft_item(pool_name + '_staking', address=nft_address)

                elif operation == OP_CODES["jetton_notify"]:
                    jetton_wallet = Address(in_msg["source"]["address"]).to_string(True, True, True)
                    if jetton_wallet != pool_wallet:
                        continue

                    tx_children = main_tx.get("children")
                    if tx_children is None:
                        continue

                    staker_address = Address(in_msg["decoded_body"]["sender"]).to_string(True, True, True)

                    nft_address = Address(tx_children[0]["transaction"]["account"]["address"]).to_string(True, True,
                                                                                                         True)
                    nft_content = getNftContent(nft_address, False, 0)
                    if not nft_content:
                        continue
                    lockup_start, lockup_period, nft_balance, index = nft_content
                    nft_content_json = {"address": nft_address, "lockupStart": lockup_start,
                                        "lockupPeriod": lockup_period, "nftBalance": nft_balance}

                    one_token = getTonEquivalent(jetton_type, pool_stonfi, 10 ** 9, False, 0)

                    cursor.execute(f"""SELECT id, "stakedJettons", "tonEquivalent", "stakerNftItems" FROM myapi_staker
                                WHERE "stakerAddress"='{staker_address}' AND "poolName"='{pool_name}'""")
                    staker_data = cursor.fetchone()

                    if not staker_data:
                        cursor.execute("""SELECT MAX(id) FROM myapi_staker""")
                        new_staker_id = cursor.fetchone()[0] + 1
                        cursor.execute(f"""INSERT INTO myapi_staker (id, "stakerAddress", "poolName", "stakedJettons", "tonEquivalent",
                                       "stakerNftItems") VALUES ({new_staker_id}, '{staker_address}', '{pool_name}', {nft_balance},
                                       {nft_balance / 10 ** 9 * one_token}, '[{dumps(nft_content_json)}]'::json)""")
                    else:
                        staker_id, staked_jettons, staker_ton_equivalent, staker_nfts = staker_data
                        staked_jettons += nft_balance
                        staker_ton_equivalent = staked_jettons / 10 ** 9 * one_token
                        staker_nfts.append(nft_content_json)

                        cursor.execute(f"""UPDATE myapi_staker
                                        SET "stakedJettons"={staked_jettons}, "tonEquivalent"={staker_ton_equivalent},
                                            "stakerNftItems"='{dumps(staker_nfts)}'::json WHERE id={staker_id}""")

                    jetton_tvl += nft_balance
                    ton_tvl = jetton_tvl / 10 ** 9 * one_token
                    cursor.execute(f"""UPDATE myapi_pool SET "jettonTvl"={jetton_tvl}, "tonTvl"={ton_tvl}
                                    WHERE name='{pool_name}'""")

                    tongochi_db.insert_staking_nft_item(pool_name, index, nft_address, lockup_start, lockup_period,
                                                        nft_balance)

        except KeyboardInterrupt:
            ws.close()
            exit(0)
        except psycopg2.ProgrammingError as ex:
            print("database error: (ws)", ex)
            need_update = 1
        except psycopg2.InterfaceError as ex:
            print("database error: (ws)", ex)
            reconnect_to_db_1()
            need_update = 1
        except Exception as ex:
            print("update_websocket error:", ex)
            print('----')
            traceback.print_exc()
            print('----')
            if not ws.connected:
                while True:
                    try:
                        ws = connect_to_websocket(connection_params)
                        break
                    except Exception as ex:
                        traceback.print_exc()
                        sleep(10)
            need_update = 1

        if need_update:
            try:
                updateNftCollections(1 / TONAPI_REQUESTS)
                addStakers(1 / TONAPI_REQUESTS)
                updateStakers(1 / TONAPI_REQUESTS, initial=True)
            except Exception:
                print('----')
                traceback.print_exc()
                print('----')


def update_simple():
    cd = 1

    while True:
        try:
            updatePools(cd)
            updateStakers(cd)
            updateDeveloperPoints(cd)
            sleep(120)
        except KeyboardInterrupt:
            exit(0)
        except psycopg2.ProgrammingError as ex:
            print("database error: (update simple)", ex)
        except psycopg2.InterfaceError as ex:
            print("database error: (update simple)", ex)
            reconnect_to_db_1()
        except Exception as ex:
            print("update_simple error", ex)
            print('----')
            traceback.print_exc()
            print('----')



if __name__ == "__main__":
    try:
        updateNftCollections(1 / TONAPI_REQUESTS)
    except Exception as ex:
        print('Error with parsing nfts\n----')
        traceback.print_exc()
        print('----')

    updatePools(1 / TONAPI_REQUESTS)
    addStakers(1 / TONAPI_REQUESTS)
    updateStakers(1 / TONAPI_REQUESTS, initial=True)
    print("finish initial update")
    simple_thread = Thread(target=update_simple)
    ws_thread = Thread(target=update_websocket)
    simple_thread.start()
    ws_thread.start()
    ws_thread.join()
