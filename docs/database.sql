DROP DATABASE IF EXISTS botname;
CREATE DATABASE botname;
USE botname;


-- Create a table for the user's settings
CREATE TYPE currency AS ENUM ('oldscape', 'newscape');
CREATE TABLE user_data (
    user_id bigint,
    currency_setting currency DEFAULT null,
    client_seed text DEFAULT null,
    oldscape bigint DEFAULT 0,
    newscape bigint DEFAULT 0,
    PRIMARY KEY (user_id)    
);


CREATE TABLE dice (
    user_id bigint,
    nonce int DEFAULT -1,
    server_seed char(40),
    PRIMARY KEY (user_id)
);


CREATE TABLE user_changes (
    user_id bigint,
    oldscape_changes bigint DEFAULT 0,
    newscape_changes bigint DEFAULT 0,
    PRIMARY KEY (user_id)
);


CREATE TABLE commands_run (
    user_id BIGINT,
    guild_id BIGINT,
    command_name VARCHAR(20),
    count INTEGER,
    PRIMARY KEY (user_id, guild_id, command_name)
);

