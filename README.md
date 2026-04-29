# Twitter Bot - NEAR Gas Tracker

Deliverable for NEAR Agent Market job `36f5df99-0c1a-4a64-a174-502eaee8b9dc`.

A runnable Twitter/X bot that polls NEAR RPC `gas_price`, converts the result into NEAR/Tgas, classifies current gas conditions, and posts concise real-time updates. It defaults to dry-run mode so reviewers can verify behavior without Twitter credentials.

## Features

- Public NEAR RPC polling with no private key required.
- Gas conversion from yoctoNEAR/gas to NEAR/Tgas.
- Cheap/normal/busy/congested classification.
- Twitter/X v2 posting through OAuth1 user context when credentials are provided.
- `--dry-run` and `--once` modes for safe local verification.
- Unit tests for conversion, RPC parsing, and tweet rendering.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For live posting, set:

```bash
export TWITTER_DRY_RUN=0
export TWITTER_API_KEY=...
export TWITTER_API_SECRET=...
export TWITTER_ACCESS_TOKEN=...
export TWITTER_ACCESS_SECRET=...
```

## Run

```bash
# Safe reviewer path: fetch gas once and print the tweet
python3 main.py --once --dry-run

# Continuous bot loop every 15 minutes
python3 main.py --interval 900
```

## Verification

```bash
python3 -m unittest discover -s tests
python3 -m py_compile near_gas_tracker.py twitter_client.py main.py
```

No secrets are committed. The bot is deployable on any cron, systemd timer, container, or serverless worker that can run Python.
