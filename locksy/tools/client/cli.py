# How to run:
# 1. Start the server (in another terminal):
#    $ uvicorn main:app --reload
# 2. Register a new user:
#   python -m tools.client.cli register alice test1234
# 3. Add a new item (evidence) for the user:
#   python -m tools.client.cli add alice test1234 --name note1 --file sample.txt
# 4. List items for the user:
#   python -m tools.client.cli list alice test1234
# 5. Get an item by ID (assuming the item ID is 1) and save it to a file:
#   python -m tools.client.cli get alice test1234 --id 1 --out retrieved_note1.txt

from __future__ import annotations

import argparse
from pathlib import Path

from tools.client.api_client import LocksyClient


def parse_verify(value: str) -> bool | str:
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    return value  # treat as path to cert/CA bundle


def main() -> int:
    p = argparse.ArgumentParser(prog="locksy-client", description="Locksy client CLI")
    p.add_argument("--base-url", default="http://127.0.0.1:8000")
    p.add_argument("--verify", default="true", help="TLS verify: true | false | path")

    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("register")
    r.add_argument("username")
    r.add_argument("password")

    a = sub.add_parser("add")
    a.add_argument("username")
    a.add_argument("password")
    a.add_argument("--name", required=True)
    a.add_argument("--file", required=True)

    l = sub.add_parser("list")
    l.add_argument("username")
    l.add_argument("password")

    g = sub.add_parser("get")
    g.add_argument("username")
    g.add_argument("password")
    g.add_argument("--id", type=int, required=True)
    g.add_argument("--out", required=True)

    args = p.parse_args()

    client = LocksyClient(
        base_url=args.base_url,
        verify=parse_verify(args.verify),
    )

    try:
        if args.cmd == "register":
            print(client.register(args.username, args.password))

        elif args.cmd == "add":
            data = Path(args.file).read_bytes()
            print(
                client.add_evidence(
                    username=args.username,
                    password=args.password,
                    name=args.name,
                    data=data,
                )
            )

        elif args.cmd == "list":
            print(client.list_evidence(username=args.username, password=args.password))

        elif args.cmd == "get":
            data = client.get_evidence(
                username=args.username,
                password=args.password,
                item_id=args.id,
            )
            Path(args.out).write_bytes(data)
            print({"saved_to": args.out})

    finally:
        client.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())