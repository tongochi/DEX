import psycopg2
import websocket
import sys
import tongochi_db

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(1, BASE_DIR.joinpath("mysite").__str__())

from settings import *  # type: ignore
from functions import *
from time import time
from json import loads, dumps
from threading import Thread
from tonsdk.utils import Address
from tonsdk.boc import Cell, Slice

conn = psycopg2.connect(
    dbname=DB_NAME,  # type: ignore
    user=DB_USER,  # type: ignore
    password=DB_PASSWORD,  # type: ignore
    host=DB_HOST,  # type: ignore
    port=DB_PORT  # type: ignore
)
cursor = conn.cursor()

last_update_devpoints = 0
timeout = 10 * 60


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
    cursor.execute("""
        SELECT
            name,
            "jettonWalletAddress",
            "stonfiPoolAddress",
            "jettonType",
            testnet
        FROM myapi_pool
    """)
    pools = cursor.fetchall()

    for pool in pools:
        pool_name, jetton_wallet, ston_fi_pool, jetton_type, testnet = pool
        jettonTvl = getJettonAmount(
            jettonWalletAddress=jetton_wallet,
            testnet=testnet,
            cooldown=cooldown
        )

        if jetton_type == "LP":
            tonTvl = getTonEqivalentLp(
                poolAddress=ston_fi_pool,
                LpAmount=jettonTvl,
                testnet=testnet,
                cooldown=cooldown,
            )
        else:
            tonTvl = getTonEqivalentJetton(
                poolAddress=ston_fi_pool,
                jettonAmount=jettonTvl,
                testnet=testnet,
                cooldown=cooldown,
            )

        usdTvl = getUsdEqivalent(tonTvl, cooldown=cooldown)

        if usdTvl > 100:
            usdTvl = int(usdTvl)
            tonTvl = int(tonTvl)
        else:
            usdTvl = round(usdTvl, 1)
            tonTvl = round(tonTvl, 1)

        if usdTvl != 0:
            print(f'update {pool_name} tvls', jettonTvl, tonTvl, usdTvl)
            cursor.execute(f"""
                UPDATE myapi_pool
                SET
                    "jettonTvl" = {jettonTvl},
                    "tonTvl" = {tonTvl},
                    "usdTvl" = {usdTvl}
                WHERE name = '{pool_name}'
            """)
            conn.commit()
        else:
            print('usdTvl = ', usdTvl, " skipping updating pool tvl")


def addStakers(cooldown: float = 1):
    cursor.execute("""SELECT id, "poolName", "stakerAddress" FROM myapi_staker""")
    stakers = cursor.fetchall()

    if stakers:
        last_id = max(stakers, key=lambda t: t[0])[0]
    else:
        last_id = 0

    stakersByPool: dict[str, set[str]] = {}
    for staker in stakers:
        _, pool_name, staker_address = staker

        if pool_name not in stakersByPool:
            stakersByPool[pool_name] = {staker_address}
        else:
            stakersByPool[pool_name].add(staker_address)

    stakersToDelete = []
    stakersToAdd = []
    availablePools = []

    cursor.execute("""SELECT name, "contractAddress", testnet FROM myapi_pool""")
    pools = cursor.fetchall()

    for pool in pools:
        pool_name, contract_address, testnet = pool

        availablePools.append(pool_name)

        base_url = TONAPI_URL_TESTNET if testnet else TONAPI_URL

        items = []
        offset = 0

        while True:
            url = f'{base_url}nfts/collections/{contract_address}/items?offset={offset}'
            items_slice = get(url, headers=AUTH_HEADER).json()["nft_items"]
            items.extend(items_slice)

            if len(items_slice) < 1000:
                break

            offset += 1000

        sleep(cooldown)

        holders = set()
        for item in items:
            holderAddress = Address(item["owner"]["address"]).to_string(True, True, True)
            if holderAddress != contract_address:
                holders.add(holderAddress)

        for staker in stakers:
            staker_id, staker_pool, staker_address = staker
            if staker_pool == pool_name and staker_address not in holders:
                stakersToDelete.append(staker_id)

        for holder in holders:
            if pool_name not in stakersByPool or holder not in stakersByPool[pool_name]:
                last_id += 1
                stakersToAdd.append(f"({last_id}, '{holder}', '{pool_name}', {testnet})")

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
    conn.commit()


def get_ton_equivalent(
        jetton_type: str,
        ston_fi_pool: str,
        amount: float | int,
        testnet: bool,
        cooldown: float,
) -> float:
    if jetton_type == "Jetton":
        ton_eqivalent = getTonEqivalentJetton(
            poolAddress=ston_fi_pool,
            jettonAmount=amount,
            testnet=testnet,
            cooldown=cooldown,
        )
    else:
        ton_eqivalent = getTonEqivalentLp(
            poolAddress=ston_fi_pool,
            LpAmount=amount,
            testnet=testnet,
            cooldown=cooldown,
        )

    return ton_eqivalent


def add_developer_points(
        staker_address: str,
        pool_name: str,
        ton_equivalent: int,
        staker_data: tuple[float, list[dict]],
        cooldown: float,
) -> None:
    NUMBER_OF_SECONDS_IN_DAY = 86400
    _, nfts = staker_data

    balance = 0
    for nft in nfts:
        if nft['lockupPeriod'] >= 14 * NUMBER_OF_SECONDS_IN_DAY:
            balance += nft['nftBalance']

    usd_equivalent = getUsdEqivalent(ton_equivalent, cooldown=cooldown)

    multiplier = {
        'PET': 100,
        'LP-PET-TON': 125,
    }.get(pool_name, 100)

    amount_of_points = int((usd_equivalent / 100) * multiplier)

    if amount_of_points > 0:
        tongochi_db.add_developer_points(
            wallet_address=staker_address,
            amount=amount_of_points,
        )


def updateStakers(cooldown: float = 0.2, initial=False):
    cursor.execute("""
        SELECT
            name,
            "contractAddress",
            "stonfiPoolAddress",
            "jettonType",
            testnet
        FROM myapi_pool
    """)
    pools = cursor.fetchall()

    nameToPool: dict[str, tuple] = {pool[0]: pool for pool in pools}

    cursor.execute("""SELECT id, "poolName", "stakerAddress", "stakedJettons", 
                   "tonEquivalent", "stakerNftItems" FROM myapi_staker""")
    stakers = cursor.fetchall()

    global last_update_devpoints
    if last_update_devpoints + timeout <= int(time()):
        update_devpoints = True
        last_update_devpoints = int(time())
    else:
        update_devpoints = False

    for staker in stakers:
        staker_id, staker_pool_name, staker_address, stakedJettons, tonEquivalent, prev_nfts = staker
        prev_nfts = prev_nfts if prev_nfts else []

        pool_name, contract_address, ston_fi_pool, jetton_type, testnet = nameToPool[staker_pool_name]
        if initial:
            staker_data = getStakerData(
                userAddress=staker_address,
                contractAddress=contract_address,
                testnet=testnet,
                cooldown=cooldown,
                prev_nfts=prev_nfts
            )
            stakedJettons, nfts = staker_data
        else:
            nfts = prev_nfts

        tonEquivalent = get_ton_equivalent(
            jetton_type=jetton_type,
            ston_fi_pool=ston_fi_pool,
            amount=stakedJettons,
            testnet=testnet,
            cooldown=cooldown,
        )
        tonEquivalent = round(tonEquivalent, 2) if tonEquivalent else 0

        if update_devpoints:
            add_developer_points(
                staker_address=staker_address,
                pool_name=pool_name,
                ton_equivalent=tonEquivalent,
                staker_data=(0, nfts),
                cooldown=cooldown,
            )

        if initial:
            cursor.execute(f"""
                UPDATE myapi_staker
                SET
                    "stakedJettons" = {stakedJettons},
                    "tonEquivalent" = {tonEquivalent},
                    "stakerNftItems" = '{dumps(nfts)}'::json
                WHERE id={staker[0]}
            """)
        else:
            cursor.execute(f"""
                UPDATE myapi_staker
                SET
                    "tonEquivalent" = {tonEquivalent}
                WHERE id={staker[0]}
            """)
        conn.commit()


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


def reconnect_to_db():
    global conn
    global cursor
    conn = psycopg2.connect(
        dbname=DB_NAME,  # type: ignore
        user=DB_USER,  # type: ignore
        password=DB_PASSWORD,  # type: ignore
        host=DB_HOST,  # type: ignore
        port=DB_PORT  # type: ignore
    )
    cursor = conn.cursor()


def update_websocket():
    connection_params = {"id": 1, "jsonrpc": "2.0", "method": "subscribe_account", "params": []}
    cursor.execute("""SELECT 
                "contractAddress", 
                name, 
                "jettonWalletAddress", 
                "stonfiPoolAddress", 
                "jettonType", 
                "jettonTvl",
                "tonTvl" 
            FROM myapi_pool""")
    pools = cursor.fetchall()
    pools_by_address = {}
    for i in pools:
        pools_by_address[i[0]] = i[1:]
        connection_params["params"].append(i[0])

    ws = connect_to_websocket(connection_params)

    cd = 3 / TONAPI_REQUESTS
    while True:
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
                    if Address(nft_address_parsed).to_string(True, True,
                                                             True) != nft_address:  # check that msg was send by nft from right collection
                        continue

                    one_token = get_ton_equivalent(jetton_type, pool_stonfi, nft_balance, False, 0)

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
                    conn.commit()

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
                    one_token = get_ton_equivalent(jetton_type, pool_stonfi, unlocked_jettons, False, 0)

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
                    conn.commit()

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

                    one_token = get_ton_equivalent(jetton_type, pool_stonfi, 10 ** 9, False, 0)

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
                    conn.commit()

                    tongochi_db.insert_staking_nft_item(pool_name, index, nft_address, lockup_start, lockup_period,
                                                        nft_balance)

        except KeyboardInterrupt:
            ws.close()
            exit(0)
        except psycopg2.ProgrammingError as ex:
            print("database error: (ws)", ex)
            conn.rollback()
        except psycopg2.InterfaceError as ex:
            print("database error: (ws)", ex)
            reconnect_to_db()
        except Exception as ex:
            print("update_websocket error:", ex)
            if not ws.connected:
                ws = connect_to_websocket()


def update_simple():
    cd = 1
    while True:
        try:
            updatePools(cd)
            updateStakers(cd)
            sleep(120)
        except KeyboardInterrupt:
            exit(0)
        except Exception as ex:
            print("update_simple error", ex)


if __name__ == "__main__":
    updateNftCollections(1)
    updatePools(1)
    addStakers(1)
    updateStakers(1, initial=True)
    print("finish initial update")
    simple_thread = Thread(target=update_simple)
    ws_thread = Thread(target=update_websocket)
    simple_thread.start()
    ws_thread.start()
    ws_thread.join()
