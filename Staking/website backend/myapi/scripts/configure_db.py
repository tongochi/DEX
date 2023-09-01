import psycopg2
from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(1, BASE_DIR.joinpath("mysite").__str__())
from settings import *  # type: ignore

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER,  # type: ignore
                        password=DB_PASSWORD, host=DB_HOST,  # type: ignore
                        port=DB_PORT)  # type: ignore

cursor = conn.cursor()

cursor.execute("""ALTER TABLE myapi_pool ALTER COLUMN "tonTvl" SET DEFAULT 0""")
cursor.execute("""ALTER TABLE myapi_pool ALTER COLUMN "jettonTvl" SET DEFAULT 0""")
cursor.execute("""ALTER TABLE myapi_pool ALTER COLUMN "usdTvl" SET DEFAULT 0""")
cursor.execute("""ALTER TABLE myapi_pool ALTER COLUMN testnet SET DEFAULT false""")
cursor.execute("""ALTER TABLE myapi_staker ALTER COLUMN "stakedJettons" SET DEFAULT 0""")
cursor.execute("""ALTER TABLE myapi_staker ALTER COLUMN "tonEquivalent" SET DEFAULT 0""")
cursor.execute("""ALTER TABLE myapi_staker ALTER COLUMN "stakerNftItems" SET DEFAULT '[]'::json""")
cursor.execute("""ALTER TABLE myapi_staker ALTER COLUMN testnet SET DEFAULT false""")

cursor.execute("DELETE FROM myapi_pool")
conn.commit()

poolPet = [
    "'PET'",
    f"'{os.environ['PET_COLLECTION']}'",
    f"'{os.environ['PET_WALLET']}'",
    "'EQB3-eMJDlGP5ZpwTmfakZGhBXAI_jBzJmqhU_CmpIx3nFo-'",
    "'Jetton'",
    "False",
]
poolLp = [
    "'LP-PET-TON'",
    f"'{os.environ['LP_PET_TON_COLLECTION']}'",
    f"'{os.environ['LP_PET_TON_WALLET']}'",
    "'EQB3-eMJDlGP5ZpwTmfakZGhBXAI_jBzJmqhU_CmpIx3nFo-'",
    "'LP'",
    "False",
]

for pool in (poolPet, poolLp):
    query = f"""
        INSERT INTO myapi_pool (
            name,
            "contractAddress",
            "jettonWalletAddress",
            "stonfiPoolAddress",
            "jettonType",
            "testnet"
        ) VALUES ({', '.join(pool)})
    """
    cursor.execute(query)

conn.commit()
