from __future__ import annotations

import argparse
import time
import statistics
from pathlib import Path

from locksy.tools.client.api_client import LocksyClient


def benchmark(base_url: str, verify: str | bool, iterations: int, file_size: int):
    client = LocksyClient(base_url=base_url, verify=verify)

    username = f"user_{int(time.time())}"
    password = "benchmark123"

    # Prepare test data
    data = b"A" * file_size

    times_register = []
    times_add = []
    times_get = []

    # Register
    start = time.perf_counter()
    client.register(username, password)
    times_register.append(time.perf_counter() - start)

    # Repeat add/get
    for i in range(iterations):
        # Add
        start = time.perf_counter()
        item = client.add_evidence(
            username=username,
            password=password,
            name=f"item{i}",
            data=data,
        )
        times_add.append(time.perf_counter() - start)

        # Get
        start = time.perf_counter()
        _ = client.get_evidence(
            username=username,
            password=password,
            item_id=item["item_id"],
        )
        times_get.append(time.perf_counter() - start)

    return {
        "register_avg_ms": statistics.mean(times_register) * 1000,
        "add_avg_ms": statistics.mean(times_add) * 1000,
        "get_avg_ms": statistics.mean(times_get) * 1000,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--verify", default="false")
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--size", type=int, default=1024)
    args = parser.parse_args()

    verify = False if args.verify == "false" else args.verify

    results = benchmark(
        base_url=args.base_url,
        verify=verify,
        iterations=args.iterations,
        file_size=args.size,
    )

    print("\nResults:")
    for k, v in results.items():
        print(f"{k}: {v:.2f} ms")


if __name__ == "__main__":
    main()