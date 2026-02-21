# This module provides authentication services for the Locksy application, 
# including user registration and unlocking the data encryption key (DEK) using the user's password. 
# It interacts with the database to store and retrieve user credentials and encryption parameters, 
# and uses cryptographic functions to securely manage the DEK.

from __future__ import annotations

from datetime import datetime, timezone
from typing import Tuple

from locksy.core.crypto import (
    hash_password, verify_password, derive_kek,
    rand_bytes, wrap_dek, unwrap_dek
)
from locksy.core.config import (
    SALT_LEN, DEK_LEN,
    KEK_TIME_COST, KEK_MEMORY_COST, KEK_PARALLELISM
)
from locksy.db.connection import connect
from locksy.db.repo import get_user_by_username, insert_user

# Utility function to get the current UTC time in ISO 8601 format for timestamping user creation and item metadata.
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Register a new user with the given username and password, 
# creating the necessary password hash, KEK parameters, and DEK encryption, 
# and store this information in the database.
def register(db_path: str, username: str, password: str) -> int:
    conn = connect(db_path)
    with conn:
        if get_user_by_username(conn, username):
            raise ValueError("Registration failed.")

        pw_hash = hash_password(password)

        dek = rand_bytes(DEK_LEN)
        kek_salt = rand_bytes(SALT_LEN)
        kek = derive_kek(password, kek_salt, KEK_TIME_COST, KEK_MEMORY_COST, KEK_PARALLELISM)
        dek_nonce, dek_wrapped = wrap_dek(kek, dek)

        user_id = insert_user(
            conn,
            username=username,
            pw_hash=pw_hash,
            kek_salt=kek_salt,
            kek_time_cost=KEK_TIME_COST,
            kek_memory_cost=KEK_MEMORY_COST,
            kek_parallelism=KEK_PARALLELISM,
            dek_nonce=dek_nonce,
            dek_wrapped=dek_wrapped,
            created_at=utc_now_iso(),
        )
    conn.close()
    return user_id

# Unlock the DEK for a user by verifying their password and deriving the KEK to unwrap the DEK,
# returning the user's ID and the unwrapped DEK for use in encrypting/decrypting their data items.
def unlock_dek(db_path: str, username: str, password: str) -> Tuple[int, bytes]:
    conn = connect(db_path)
    user = get_user_by_username(conn, username)
    conn.close()

    if not user or not verify_password(user.pw_hash, password):
        raise ValueError("Invalid username or password.")

    kek = derive_kek(password, user.kek_salt, user.kek_time_cost, user.kek_memory_cost, user.kek_parallelism)
    dek = unwrap_dek(kek, user.dek_nonce, user.dek_wrapped)
    return user.id, dek