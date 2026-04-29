"""NEAR gas tracker core logic.

Uses public NEAR RPC `gas_price` and produces concise Twitter/X updates.
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

DEFAULT_RPC_URL = "https://rpc.mainnet.near.org"
YOCTO_PER_NEAR = 10**24
TGAS = 10**12


@dataclass(frozen=True)
class GasSnapshot:
    gas_price: int
    near_per_tgas: float
    block_height: int | None
    fetched_at: str


def _post_json(url: str, payload: dict[str, Any], timeout: int = 20) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"content-type": "application/json", "user-agent": "near-gas-tracker/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def rpc_call(method: str, params: list[Any] | None = None, rpc_url: str = DEFAULT_RPC_URL, post_json: Callable[..., dict[str, Any]] = _post_json) -> dict[str, Any]:
    response = post_json(rpc_url, {"jsonrpc": "2.0", "id": "near-gas-tracker", "method": method, "params": params or [None]})
    if response.get("error"):
        raise RuntimeError(response["error"].get("message", "NEAR RPC error"))
    return response["result"]


def gas_price_to_near_per_tgas(gas_price: int) -> float:
    return (int(gas_price) * TGAS) / YOCTO_PER_NEAR


def fetch_gas_snapshot(rpc_url: str = DEFAULT_RPC_URL, post_json: Callable[..., dict[str, Any]] = _post_json) -> GasSnapshot:
    result = rpc_call("gas_price", [None], rpc_url=rpc_url, post_json=post_json)
    price = int(result["gas_price"])
    return GasSnapshot(
        gas_price=price,
        near_per_tgas=gas_price_to_near_per_tgas(price),
        block_height=result.get("block_height"),
        fetched_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )


def classify_gas(gas_price: int, baseline: int = 100_000_000) -> str:
    ratio = int(gas_price) / baseline
    if ratio < 0.8:
        return "cheap"
    if ratio < 1.5:
        return "normal"
    if ratio < 3:
        return "busy"
    return "congested"


def compose_tweet(snapshot: GasSnapshot, network: str = "mainnet") -> str:
    status = classify_gas(snapshot.gas_price)
    block = f" at block {snapshot.block_height}" if snapshot.block_height else ""
    return (
        f"⛽ NEAR gas is {status} on {network}{block}.\n"
        f"Current gas price: {snapshot.gas_price:,} yoctoNEAR/gas "
        f"(~{snapshot.near_per_tgas:.6f} NEAR/Tgas).\n"
        "Use NEAR when gas is cheap: fast finality, predictable fees. #NEAR #Web3"
    )[:280]


def run_loop(post_tweet: Callable[[str], Any], interval_seconds: int, rpc_url: str = DEFAULT_RPC_URL) -> None:
    while True:
        snapshot = fetch_gas_snapshot(rpc_url=rpc_url)
        post_tweet(compose_tweet(snapshot))
        time.sleep(interval_seconds)
