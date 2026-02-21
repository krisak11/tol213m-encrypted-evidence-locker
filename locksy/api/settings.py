# locksy.api.settings
# This module defines the Settings dataclass which holds configuration settings for the Locksy application.

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_path: str = os.getenv("LOCKSY_DB_PATH", "locksy.db")


settings = Settings()