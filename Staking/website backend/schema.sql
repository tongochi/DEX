CREATE schema IF NOT EXISTS nft_collections;
-- table schema: nft_collections
CREATE TABLE IF NOT EXISTS nft_collections.LP_PET_TON_staking_content
(
    id          INTEGER     NOT NULL,
    address     VARCHAR(48) NOT NULL,
    name        VARCHAR(35) NOT NULL,
    description TEXT        NOT NULL,
    image       TEXT        NOT NULL,
    attributes  TEXT        NOT NULL,
    active      BOOLEAN     NOT NULL DEFAULT true,
    PRIMARY KEY (id),
    UNIQUE (address)
);
CREATE TABLE IF NOT EXISTS nft_collections.PET_staking_content
(
    id          INTEGER     NOT NULL,
    address     VARCHAR(48) NOT NULL,
    name        VARCHAR(35) NOT NULL,
    description TEXT        NOT NULL,
    image       TEXT        NOT NULL,
    attributes  TEXT        NOT NULL,
    active      BOOLEAN     NOT NULL DEFAULT true,
    PRIMARY KEY (id),
    UNIQUE (address)
);

create table if not exists public.developerpoints
(
    identificator      serial       primary key,
    owner_wallet       varchar(100) unique,
    amount             bigint       not null,
    last_update_time   bigint       not null,
    last_update_amount bigint       not null
);