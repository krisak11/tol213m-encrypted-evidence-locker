# This file contains cryptographic functions for password hashing, key derivation, and data encryption/decryption used in Locksy.

from __future__ import annotations

import os
from typing import Tuple

from argon2 import PasswordHasher
from argon2.low_level import Type, hash_secret_raw
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .config import (
    PH_TIME_COST, PH_MEMORY_COST, PH_PARALLELISM, PH_HASH_LEN, PH_SALT_LEN,
    KEK_TIME_COST, KEK_MEMORY_COST, KEK_PARALLELISM, KEK_LEN,
    AESGCM_NONCE_LEN
)

PH = PasswordHasher(
    time_cost=PH_TIME_COST,
    memory_cost=PH_MEMORY_COST,
    parallelism=PH_PARALLELISM,
    hash_len=PH_HASH_LEN,
    salt_len=PH_SALT_LEN,
)

# random bytes generator using cryptographically secure RNG
def rand_bytes(n: int) -> bytes:
    return os.urandom(n)

# Password hashing for credential storage, using Argon2id
def hash_password(password: str) -> str:
    return PH.hash(password)

# Password verification for unlock/login operations
def verify_password(pw_hash: str, password: str) -> bool:
    try:
        return PH.verify(pw_hash, password)
    except Exception:
        return False

# KEK derivation using Argon2id, separate from password hash salt.abs
# KEK (Key Encryption Key) is used to encrypt the DEK (Data Encryption Key) which in turn encrypts the actual data.
def derive_kek(password: str, salt: bytes,
               time_cost: int = KEK_TIME_COST,
               memory_cost: int = KEK_MEMORY_COST,
               parallelism: int = KEK_PARALLELISM) -> bytes:
    return hash_secret_raw(
        secret=password.encode("utf-8"),
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        parallelism=parallelism,
        hash_len=KEK_LEN,
        type=Type.ID,
    )

# Symmetric encryption using AES-GCM for encrypting the DEK and the actual data blobs.
def wrap_dek(kek: bytes, dek: bytes) -> Tuple[bytes, bytes]:
    aesgcm = AESGCM(kek)
    nonce = rand_bytes(AESGCM_NONCE_LEN)
    wrapped = aesgcm.encrypt(nonce, dek, None)
    return nonce, wrapped

# Unwrap the DEK using the KEK and nonce (number used once) to retrieve the original DEK for data decryption.
def unwrap_dek(kek: bytes, nonce: bytes, wrapped: bytes) -> bytes:
    aesgcm = AESGCM(kek)
    return aesgcm.decrypt(nonce, wrapped, None)

# Encrypt a data blob using the DEK and return the nonce (number used once) and ciphertext.
def encrypt_blob(dek: bytes, plaintext: bytes, aad: bytes) -> Tuple[bytes, bytes]:
    aesgcm = AESGCM(dek)
    nonce = rand_bytes(AESGCM_NONCE_LEN)
    ciphertext = aesgcm.encrypt(nonce, plaintext, aad)
    return nonce, ciphertext

# Decrypt a data blob using the DEK, nonce (number used once), and additional authenticated data (AAD) to retrieve the original plaintext.
def decrypt_blob(dek: bytes, nonce: bytes, ciphertext: bytes, aad: bytes) -> bytes:
    aesgcm = AESGCM(dek)
    return aesgcm.decrypt(nonce, ciphertext, aad)