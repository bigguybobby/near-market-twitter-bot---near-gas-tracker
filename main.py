#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

from near_gas_tracker import compose_tweet, fetch_gas_snapshot, run_loop
from twitter_client import TwitterConfig, TwitterPoster


def main() -> None:
    parser = argparse.ArgumentParser(description="Post NEAR gas tracker updates to Twitter/X")
    parser.add_argument("--rpc-url", default=os.environ.get("NEAR_RPC_URL", "https://rpc.mainnet.near.org"))
    parser.add_argument("--interval", type=int, default=int(os.environ.get("GAS_TRACKER_INTERVAL", "900")))
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--dry-run", action="store_true", help="Print tweet instead of posting")
    args = parser.parse_args()

    poster = TwitterPoster(TwitterConfig(dry_run=args.dry_run or os.environ.get("TWITTER_DRY_RUN", "1") != "0"))
    if args.once:
        snapshot = fetch_gas_snapshot(args.rpc_url)
        poster.post(compose_tweet(snapshot))
        return
    run_loop(poster.post, interval_seconds=args.interval, rpc_url=args.rpc_url)


if __name__ == "__main__":
    main()
