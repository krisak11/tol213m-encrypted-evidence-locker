# This file defines the SQL schema for the Locksy application, which includes tables for users and their encrypted items.
# The schema includes fields for storing user credentials, encryption parameters, and the encrypted data blobs.

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT UNIQUE NOT NULL,

    pw_hash         TEXT NOT NULL,

    kek_salt        BLOB NOT NULL,
    kek_time_cost   INTEGER NOT NULL,
    kek_memory_cost INTEGER NOT NULL,
    kek_parallelism INTEGER NOT NULL,

    dek_nonce       BLOB NOT NULL,
    dek_wrapped     BLOB NOT NULL,

    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    name        TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    size_bytes  INTEGER NOT NULL,

    nonce       BLOB NOT NULL,
    aad         BLOB NOT NULL,
    ciphertext  BLOB NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_items_user_id ON items(user_id);
"""