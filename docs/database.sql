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


CREATE TABLE commands_run (
    user_id bigint,
    guild_id bigint,
    command_name varchar(20),
    count integer,
    PRIMARY KEY (user_id, guild_id, command_name)
);


CREATE TABLE command_log (
    user_id bigint,
    message_id bigint,
    guild_id bigint,
    command_name varchar(20),
    message_text text,
    time timestamp,
    PRIMARY KEY (message_id)
);


CREATE TABLE modification_log (
    cashier_id bigint,
    user_id bigint,
    message_id bigint,
    oldscape_mod bigint,
    newscape_mod bigint,
    PRIMARY KEY (message_id)
);
