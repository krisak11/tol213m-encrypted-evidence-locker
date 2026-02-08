# This module provides the core functionality for managing encrypted data items (evidence) in the Locksy application.
# It includes functions to add new encrypted items, retrieve and decrypt existing items, and list all items associated with a user. 
# The module interacts with the database to store and retrieve encrypted data blobs and their associated metadata, 
# and uses the user's DEK to perform encryption and decryption operations securely.

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import List, Tuple

from locksy.core.crypto import encrypt_blob, decrypt_blob
from locksy.db.connection import connect
from locksy.db.repo import insert_item, get_item, list_items

# Utility function to get the current UTC time in ISO 8601 format for timestamping user creation and item metadata.
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# Add a new encrypted item (evidence) to the database for a user, including metadata and the encrypted data blob, returning the new item's ID.
def add_evidence(db_path: str, user_id: int, dek: bytes, name: str, data: bytes) -> int:
    created_at = utc_now_iso()
    size_bytes = len(data)

    aad_dict = {"user_id": user_id, "name": name, "created_at": created_at, "size_bytes": size_bytes}
    aad = json.dumps(aad_dict, separators=(",", ":"), sort_keys=True).encode("utf-8")

    nonce, ciphertext = encrypt_blob(dek, data, aad)

    conn = connect(db_path)
    with conn:
        item_id = insert_item(
            conn,
            user_id=user_id,
            name=name,
            created_at=created_at,
            size_bytes=size_bytes,
            nonce=nonce,
            aad=aad,
            ciphertext=ciphertext,
        )
    conn.close()
    return item_id

# Retrieve and decrypt an encrypted item (evidence) from the database by its ID, 
# verifying ownership and returning the item's name and plaintext data.
def get_evidence(db_path: str, user_id: int, dek: bytes, item_id: int) -> Tuple[str, bytes]:
    conn = connect(db_path)
    row = get_item(conn, item_id)
    conn.close()

    if not row:
        raise ValueError("Item not found.")

    _id, owner_id, name, _created_at, _size, nonce, aad, ciphertext = row
    if owner_id != user_id:
        raise ValueError("Access denied.")

    plaintext = decrypt_blob(dek, nonce, ciphertext, aad)
    return name, plaintext

# List all encrypted items (evidence) associated with a user, 
# returning a list of tuples containing the item's ID, name, creation timestamp, and size in bytes.
def list_evidence(db_path: str, user_id: int) -> List[Tuple]:
    conn = connect(db_path)
    rows = list_items(conn, user_id)
    conn.close()
    return rows