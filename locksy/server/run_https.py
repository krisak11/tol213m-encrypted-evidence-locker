from __future__ import annotations

import ssl
from pathlib import Path

import uvicorn

LOCKSY_DIR = Path(__file__).resolve().parents[1]  # <root>/locksy
CERT_FILE = LOCKSY_DIR / "certs" / "server.crt"
KEY_FILE = LOCKSY_DIR / "certs" / "server.key"

TLS12_CIPHERS = (
    "ECDHE-ECDSA-AES256-GCM-SHA384:"
    "ECDHE-RSA-AES256-GCM-SHA384:"
    "ECDHE-ECDSA-AES128-GCM-SHA256:"
    "ECDHE-RSA-AES128-GCM-SHA256:"
    "ECDHE-ECDSA-CHACHA20-POLY1305:"
    "ECDHE-RSA-CHACHA20-POLY1305:"
    "!aNULL:!eNULL:!MD5:!3DES:!DES:!RC4"
)

if __name__ == "__main__":
    assert CERT_FILE.exists(), f"Missing cert: {CERT_FILE}"
    assert KEY_FILE.exists(), f"Missing key: {KEY_FILE}"

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8443,
        reload=True,
        ssl_certfile=str(CERT_FILE),
        ssl_keyfile=str(KEY_FILE),
        ssl_version=ssl.PROTOCOL_TLS_SERVER,
        ssl_ciphers=TLS12_CIPHERS,
    )