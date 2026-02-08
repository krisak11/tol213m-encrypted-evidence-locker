# This file contains configuration constants for Locksy, such as database paths and parameters for password hashing and encryption.

from __future__ import annotations

# DB
DB_PATH_DEFAULT = "locksy.db"

# Argon2id password hashing (credential storage)
PH_TIME_COST = 2
PH_MEMORY_COST = 19456  # KiB (19 MiB)
PH_PARALLELISM = 1
PH_HASH_LEN = 32
PH_SALT_LEN = 16

# KEK derivation (separate from password hash salt)
KEK_TIME_COST = 2
KEK_MEMORY_COST = 19456  # KiB
KEK_PARALLELISM = 1
KEK_LEN = 32  # 256-bit

# Symmetric encryption
AESGCM_NONCE_LEN = 12  # 96-bit nonce for GCM
DEK_LEN = 32          # 256-bit DEK
SALT_LEN = 16