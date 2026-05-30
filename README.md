# Locksy

Locksy is a small FastAPI-based encrypted evidence locker. It lets a user register, add binary evidence, list stored evidence metadata, and retrieve evidence after authenticating with the same username and password.

The service stores user and item records in SQLite. Evidence bytes are encrypted before they are written to the database.

## What It Does

- Registers local users with Argon2id password hashes.
- Creates a random per-user data encryption key (DEK).
- Derives a key encryption key (KEK) from the user's password with Argon2id.
- Wraps the user's DEK with AES-GCM and stores only the wrapped key.
- Encrypts each evidence blob with AES-GCM.
- Authenticates selected item metadata as AES-GCM additional authenticated data (AAD).
- Exposes a JSON HTTP API and a small Python CLI client.

## Project Layout

```text
.
├── main.py                         # FastAPI app entrypoint
├── requirements.txt                # Runtime dependencies
└── locksy/
    ├── api/
    │   ├── routes.py               # HTTP endpoints
    │   └── settings.py             # Environment-backed settings
    ├── core/
    │   ├── config.py               # Crypto parameter constants
    │   └── crypto.py               # Password hashing, KEK derivation, AES-GCM helpers
    ├── db/
    │   ├── connection.py           # SQLite connection/init helpers
    │   ├── repo.py                 # Database access functions
    │   └── schema.py               # SQLite schema
    ├── server/
    │   ├── run_http.py             # Local HTTP dev server
    │   └── run_https.py            # Local HTTPS dev server
    └── tools/
        ├── bench_transit.py        # Simple register/add/get timing script
        └── client/
            ├── api_client.py       # HTTP client wrapper
            └── cli.py              # Command-line client
```

## Requirements

- Python 3.10 or newer
- SQLite
- The Python packages listed in `requirements.txt`

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run The API

Start the HTTP development server:

```bash
python3 -m locksy.server.run_http
```

The API will listen on:

```text
http://127.0.0.1:8000
```

You can also run the app directly with Uvicorn:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Visit the health endpoint:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"status":"ok","app":"Locksy","db":"locksy.db"}
```

## HTTPS Development Server

Locksy includes a local TLS runner:

```bash
python3 -m locksy.server.run_https
```

It expects:

```text
locksy/certs/server.crt
locksy/certs/server.key
```

The checked-in certificate material is suitable only for local development. Generate fresh certificates before using HTTPS in any environment that matters.

## Configuration

Locksy currently supports one environment variable:

| Variable | Default | Description |
| --- | --- | --- |
| `LOCKSY_DB_PATH` | `locksy.db` | Path to the SQLite database file. |

Example:

```bash
LOCKSY_DB_PATH=/tmp/locksy-dev.db python3 -m locksy.server.run_http
```

The database schema is initialized automatically when the FastAPI app starts.

## CLI Usage

Run these commands while the API server is running.

Register a user:

```bash
python3 -m locksy.tools.client.cli register alice test1234
```

Add an evidence file:

```bash
python3 -m locksy.tools.client.cli add alice test1234 --name note1 --file sample.txt
```

List evidence:

```bash
python3 -m locksy.tools.client.cli list alice test1234
```

Retrieve evidence by ID:

```bash
python3 -m locksy.tools.client.cli get alice test1234 --id 1 --out retrieved_note1.txt
```

For HTTPS with a self-signed local certificate, either disable verification for local testing:

```bash
python3 -m locksy.tools.client.cli \
  --base-url https://127.0.0.1:8443 \
  --verify false \
  list alice test1234
```

Or pass a CA/certificate bundle path:

```bash
python3 -m locksy.tools.client.cli \
  --base-url https://127.0.0.1:8443 \
  --verify locksy/certs/server.crt \
  list alice test1234
```

## API

All request and response bodies are JSON.

### `GET /`

Health check.

Response:

```json
{
  "status": "ok",
  "app": "Locksy",
  "db": "locksy.db"
}
```

### `POST /register`

Registers a new user.

Request:

```json
{
  "username": "alice",
  "password": "test1234"
}
```

Response:

```json
{
  "user_id": 1
}
```

### `POST /add`

Authenticates the user, encrypts the submitted bytes, and stores a new evidence item.

`data_b64` must be base64-encoded file bytes.

Request:

```json
{
  "username": "alice",
  "password": "test1234",
  "name": "note1",
  "data_b64": "SGVsbG8="
}
```

Response:

```json
{
  "item_id": 1
}
```

### `POST /list`

Authenticates the user and lists that user's evidence metadata.

Request:

```json
{
  "username": "alice",
  "password": "test1234"
}
```

Response:

```json
{
  "items": [
    {
      "id": 1,
      "name": "note1",
      "created_at": "2026-05-30T12:00:00+00:00",
      "size_bytes": 5
    }
  ]
}
```

### `POST /get`

Authenticates the user, verifies ownership, decrypts an evidence item, and returns the plaintext bytes as base64.

Request:

```json
{
  "username": "alice",
  "password": "test1234",
  "item_id": 1
}
```

Response:

```json
{
  "name": "note1",
  "data_b64": "SGVsbG8="
}
```

## Storage And Encryption Model

Locksy uses two layers of keys:

- The password hash is used for credential verification.
- A separate Argon2id-derived KEK is used to unwrap the user's DEK.
- The DEK encrypts and decrypts evidence blobs.

On registration:

1. Locksy hashes the user's password with Argon2id.
2. Locksy generates a random 256-bit DEK.
3. Locksy generates a KEK salt and derives a 256-bit KEK from the password.
4. Locksy wraps the DEK with AES-GCM.
5. Locksy stores the password hash, KEK parameters, wrapped DEK, and creation timestamp.

When adding evidence:

1. Locksy verifies the username and password.
2. Locksy derives the KEK and unwraps the DEK.
3. Locksy builds authenticated metadata containing `user_id`, `name`, `created_at`, and `size_bytes`.
4. Locksy encrypts the evidence bytes with AES-GCM and stores the nonce, AAD, and ciphertext.

When retrieving evidence, Locksy verifies the requester owns the item before decrypting it.

## Database

The SQLite database contains two tables:

- `users`: usernames, Argon2id password hashes, KEK parameters, wrapped DEKs, and creation timestamps.
- `items`: owner IDs, item names, creation timestamps, plaintext size metadata, AES-GCM nonces, AAD, and ciphertext.

The database does not store plaintext evidence bytes.

## Benchmark Script

With a server running, the simple timing script can register a temporary user and measure add/get round trips:

```bash
python3 -m locksy.tools.bench_transit \
  --base-url http://127.0.0.1:8000 \
  --iterations 5 \
  --size 1024
```

For local HTTPS with the bundled self-signed certificate:

```bash
python3 -m locksy.tools.bench_transit \
  --base-url https://127.0.0.1:8443 \
  --verify false
```

## Development Notes

- The current API sends usernames and passwords in JSON request bodies. Use HTTPS for anything outside local development.
- The API currently supports register, add, list, and get operations. There is no delete endpoint yet.
- Authentication errors and several operational failures are returned as HTTP 400 responses.
- Usernames are unique.
- Evidence names and size metadata are stored in plaintext.
- The project does not currently include an automated test suite.

