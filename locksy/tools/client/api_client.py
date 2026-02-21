from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict

import httpx


class LocksyClient:
    """
    Transport-layer client for Locksy.
    Handles HTTP(S) communication only.
    """

    def __init__(self, base_url: str, verify: bool | str = True, timeout: float = 60.0):
        self._client = httpx.Client(
            base_url=base_url,
            verify=verify,
            timeout=timeout,
        )

    def close(self) -> None:
        self._client.close()

    # ---------- Auth ----------

    def register(self, username: str, password: str) -> Dict[str, Any]:
        r = self._client.post(
            "/register",
            json={"username": username, "password": password},
        )
        r.raise_for_status()
        return r.json()

    # ---------- Evidence ----------

    def add_evidence(self, *, username: str, password: str, name: str, data: bytes) -> Dict[str, Any]:
        data_b64 = base64.b64encode(data).decode("utf-8")
        r = self._client.post(
            "/add",
            json={
                "username": username,
                "password": password,
                "name": name,
                "data_b64": data_b64,
            },
        )
        r.raise_for_status()
        return r.json()

    def list_evidence(self, *, username: str, password: str) -> Dict[str, Any]:
        r = self._client.post(
            "/list",
            json={"username": username, "password": password},
        )
        r.raise_for_status()
        return r.json()

    def get_evidence(self, *, username: str, password: str, item_id: int) -> bytes:
        r = self._client.post(
            "/get",
            json={
                "username": username,
                "password": password,
                "item_id": item_id,
            },
        )
        r.raise_for_status()
        payload = r.json()
        return base64.b64decode(payload["data_b64"])