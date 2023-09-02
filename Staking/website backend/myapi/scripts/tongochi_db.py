import time
from pathlib import Path
import sys
import psycopg2
from json import loads, dumps
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(1, BASE_DIR.joinpath("mysite").__str__())
from settings import *  # type: ignore


__tongochi_db_connection = psycopg2.connect(
    dbname=TONGOCHI_DB_NAME,  # type: ignore
    user=TONGOCHI_DB_USER,  # type: ignore
    password=TONGOCHI_DB_PASS,  # type: ignore
    host=TONGOCHI_DB_HOST,  # type: ignore
    port=TONGOCHI_DB_PORT,  # type: ignore
)


def add_developer_points(
    wallet_address: str,
    amount: int,
) -> None:
    query = """
        INSERT INTO DeveloperPoints (owner_wallet, amount, last_update_time, last_update_amount)
        VALUES (%(owner_wallet)s, %(amount)s, %(current_time)s, %(amount)s)

        ON CONFLICT (owner_wallet)
        DO UPDATE
        SET
            amount = DeveloperPoints.amount + (
                (CAST((%(current_time)s - DeveloperPoints.last_update_time) AS bigint) * %(amount)s) / CAST(60 AS bigint)
            ),
            last_update_time = %(current_time)s,
            last_update_amount = %(amount)s
        WHERE DeveloperPoints.last_update_time + %(timeout)s <= %(current_time)s
        AND DeveloperPoints.owner_wallet = %(owner_wallet)s;
    """

    TIMEOUT: int = 5 * 60  # 5 Minutes
    current_time = int(time.time())

    vars_ = {
        'owner_wallet': wallet_address,
        'amount': amount,
        'timeout': TIMEOUT,
        'current_time': current_time,
    }

    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(query, vars_)
        __tongochi_db_connection.commit()


def get_developer_points(
    wallet_address: str,
) -> tuple[int, int, int]:
    """
    Returns amount of points, devider for convert it to rational number,
    and last update amount
    """
    query = """
        SELECT amount, last_update_amount from DeveloperPoints
        WHERE owner_wallet = %(wallet_address)s;
    """

    vars_ = {
        'wallet_address': wallet_address,
    }

    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(query, vars_)
        result = cursor.fetchone()

    DEVIDER: int = 10_000

    if not result:
        return (0, DEVIDER, 0)

    amount: int = result[0]
    last_update_amount: int = result[1]

    return (amount, DEVIDER, last_update_amount)


def nft_collection_exists(collection: str):
    query = f"""
        SELECT * FROM pg_tables
        WHERE schemaname='nft_collections'
        AND tablename='{collection.lower()}_content'
    """

    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(query)
        if not cursor.fetchone():
            return False

    return True


def insert_staking_nft_item(
    jetton_name: str,
    index: int,
    address: str,
    lockup_start: int,
    lockup_period: int,
    staked_amount: int,
) -> None:
    jetton_name = jetton_name.replace("-", "_")
    if not nft_collection_exists(jetton_name + '_staking'):
        return

    table_name = f"nft_collections.{jetton_name}_staking_content"

    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name} WHERE id={index}")
        if cursor.fetchone():
            print(f"item with id={index} already exists in {table_name} but ok")
            cursor.execute(f"DELETE FROM {table_name} WHERE id={index}")
            __tongochi_db_connection.commit()

    query = f"""
        INSERT INTO {table_name} VALUES (%(index)s, %(address)s, %(name)s,
        %(description)s, %(image)s, %(attributes)s, true);
    """

    lockup_start_attr = datetime.fromtimestamp(lockup_start).strftime("%d/%m/%Y, %H:%M")
    lockup_end_attr = datetime.fromtimestamp(lockup_start + 60 +
                                             lockup_period).strftime("%d/%m/%Y, %H:%M")
    lockup_period_attr = str(timedelta(seconds=lockup_period).days) + ' days'
    staked_amount_attr = str(staked_amount / 10 ** 9)
    vars_ = {
        'index': index,
        'address': address,
        'name': jetton_name.replace('_', ' ') + ' staking NFT',
        'description': ('NFT proof for staking on Tongochi DEX. '
                        'For unstaking, you will need this NFT.'),
        'attributes': dumps([
            {"trait_type": "Lockup start (UTC)", "value": lockup_start_attr},
            {"trait_type": "Lockup end (UTC)", "value": lockup_end_attr},
            {"trait_type": "Lockup period", "value": lockup_period_attr},
            {"trait_type": "Staked amount", "value": staked_amount_attr}
        ]),
        'image': "https://raw.githubusercontent.com/ArkadiyStena/testJson/main/nft-content/nft-image.png"
    }

    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(query, vars_)
        __tongochi_db_connection.commit()


def deactivate_nft_item(
    collection: str,
    index: int = None,
    address: str = None,
) -> None:
    if not (index or address):
        return
    collection = collection.replace("-", "_")
    if not nft_collection_exists(collection):
        return

    if index:
        query = f"""
            UPDATE nft_collections.{collection}_content
            SET active=false WHERE id=%(index)s;
        """
        vars_ = {
            'index': index,
        }
    else:
        query = f"""
            UPDATE nft_collections.{collection}_content
            SET active=false WHERE address=%(address)s;
        """
        vars_ = {
            'address': address,
        }

    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(query, vars_)
        __tongochi_db_connection.commit()


def get_nft_item(collection: str, index: int) -> dict:
    """
    Returns nft content for explorers
    """
    collection = collection.replace("-", "_")
    if not nft_collection_exists(collection):
        return {"error": "collection not in database"}

    query = f"""
        SELECT name, address, description, image, attributes, active
        FROM nft_collections.{collection}_content
        WHERE id = %(index)s;
    """

    vars_ = {
        'index': index
    }

    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(query, vars_)
        result = cursor.fetchone()

    if not result or result[-1] == False:
        return {"name": "not found"}

    return {
        "name": result[0],
        "address": result[1],
        "description": result[2],
        "image": result[3],
        "attributes": loads(result[4])
    }


def get_all_collection_items(collection: str) -> list | dict:
    """
    Returns the list of nft addresses
    """
    collection = collection.replace("-", "_")
    if not nft_collection_exists(collection):
        return {"error": "not in database"}

    query = f"""SELECT address FROM nft_collections.{collection}_content """
    with __tongochi_db_connection.cursor() as cursor:
        cursor.execute(query)
        result = list(map(lambda x: x[0], cursor.fetchall()))
    return result
