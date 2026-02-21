from __future__ import annotations

import ssl
import uvicorn

CERT_FILE = "certs/server.crt"
KEY_FILE = "certs/server.key"

# Restrict TLS settings (non-default hardening)
# - TLS 1.2+ minimum
# - Modern AEAD cipher suites for TLS 1.2
TLS12_CIPHERS = "ECDHE+AESGCM:ECDHE+CHACHA20:!aNULL:!eNULL:!MD5:!3DES:!DES:!RC4"

def build_ssl_context() -> ssl.SSLContext:
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.set_ciphers(TLS12_CIPHERS)
    ctx.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    return ctx

if __name__ == "__main__":
    ssl_ctx = build_ssl_context()

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8443,
        reload=True,
        ssl_keyfile=KEY_FILE,
        ssl_certfile=CERT_FILE,
        ssl_version=ssl.PROTOCOL_TLS_SERVER,
        ssl_ciphers=TLS12_CIPHERS,
    )