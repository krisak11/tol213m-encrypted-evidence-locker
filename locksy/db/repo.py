# This module defines the repository functions for interacting with the SQLite database in the Locksy application.
# It includes functions to retrieve user information, insert new users, and manage encrypted items associated with each user.

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List
import sqlite3

@dataclass
class UserRow:
    """
    Data class representing a user row in the database, containing fields for user credentials, encryption parameters, and metadata.
    """
    id: int
    username: str
    pw_hash: str
    kek_salt: bytes
    kek_time_cost: int
    kek_memory_cost: int
    kek_parallelism: int
    dek_nonce: bytes
    dek_wrapped: bytes

# Retrieve a user from the database by their username, returning a UserRow object if found, or None if not found.
def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[UserRow]:
    row = conn.execute(
        """
        SELECT id, username, pw_hash, kek_salt, kek_time_cost, kek_memory_cost,
               kek_parallelism, dek_nonce, dek_wrapped
        FROM users WHERE username = ?
        """,
        (username,),
    ).fetchone()
    return UserRow(*row) if row else None

# Insert a new user into the database with the provided credentials, encryption parameters, and metadata, returning the new user's ID.
def insert_user(conn: sqlite3.Connection, *,
                username: str,
                pw_hash: str,
                kek_salt: bytes, kek_time_cost: int, kek_memory_cost: int, kek_parallelism: int,
                dek_nonce: bytes, dek_wrapped: bytes,
                created_at: str) -> int:
    # cursor is the cursor object returned by the execute method, 
    # which allows us to retrieve the last inserted row ID after inserting a new user into the database.            
    cursor = conn.execute(
        """
        INSERT INTO users (
            username, pw_hash,
            kek_salt, kek_time_cost, kek_memory_cost, kek_parallelism,
            dek_nonce, dek_wrapped,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (username, pw_hash,
         kek_salt, kek_time_cost, kek_memory_cost, kek_parallelism,
         dek_nonce, dek_wrapped,
         created_at),
    )
    return int(cursor.lastrowid)

# Insert a new encrypted item into the database associated with a user, including metadata and the encrypted data blob, returning the new item's ID.
def insert_item(conn: sqlite3.Connection, *,
                user_id: int, name: str, created_at: str, size_bytes: int,
                nonce: bytes, aad: bytes, ciphertext: bytes) -> int:
    cursor = conn.execute(
        """
        INSERT INTO items (user_id, name, created_at, size_bytes, nonce, aad, ciphertext)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, name, created_at, size_bytes, nonce, aad, ciphertext),
    )
    return int(cursor.lastrowid)

# Retrieve an encrypted item from the database by its ID, returning a tuple of the item's fields if found, or None if not found.
def get_item(conn: sqlite3.Connection, item_id: int) -> Optional[Tuple]:
    return conn.execute(
        "SELECT id, user_id, name, created_at, size_bytes, nonce, aad, ciphertext FROM items WHERE id = ?",
        (item_id,),
    ).fetchone()

# List all encrypted items associated with a user, returning a list of tuples containing the item's ID, name, creation timestamp, and size in bytes.
def list_items(conn: sqlite3.Connection, user_id: int) -> List[Tuple]:
    return conn.execute(
        "SELECT id, name, created_at, size_bytes FROM items WHERE user_id = ? ORDER BY id ASC",
        (user_id,),
    ).fetchall()