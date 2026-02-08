# This module provides functions to connect to the SQLite database and initialize it with the required schema for the Locksy application.

from __future__ import annotations

import sqlite3

from .schema import SCHEMA_SQL

# Connect to the SQLite database at the given path and enable foreign key support.
def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# Initialize the database by creating the necessary tables and indexes as defined in the SCHEMA_SQL.
def init_db(db_path: str) -> None:
    conn = connect(db_path)
    with conn:
        conn.executescript(SCHEMA_SQL)
    conn.close()