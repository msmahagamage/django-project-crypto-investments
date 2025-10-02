# dashboard/crypto.py
from __future__ import annotations
import requests
from django.core.cache import cache

# Normalize common symbols AND names → CoinGecko IDs
# (add more as you need)
ALIASES = {
    # Bitcoin
    "btc": "bitcoin",
    "xbt": "bitcoin",
    "bitcoin": "bitcoin",
    # Ethereum
    "eth": "ethereum",
    "ethereum": "ethereum",
    # Tether
    "usdt": "tether",
    "tether": "tether",
    # Tron
    "trx": "tron",
    "tron": "tron",
    # Cardano
    "ada": "cardano",
    "cardano": "cardano",
    # BNB
    "bnb": "binancecoin",
    "binance": "binancecoin",
    "binancecoin": "binancecoin",
    # XRP
    "xrp": "ripple",
    "ripple": "ripple",
    # Solana
    "sol": "solana",
    "solana": "solana",
    # Polygon
    "matic": "polygon-pos",
    "polygon": "polygon-pos",
    "polygonpos": "polygon-pos",
    # Polkadot
    "dot": "polkadot",
    "polkadot": "polkadot",
    # Avalanche
    "avax": "avalanche-2",
    "avalanche": "avalanche-2",
    # Litecoin
    "ltc": "litecoin",
    "litecoin": "litecoin",
    # Chainlink
    "link": "chainlink",
    "chainlink": "chainlink",
}

API = "https://api.coingecko.com/api/v3/simple/price"


def to_cg_id(coin: str | None) -> str | None:
    if not coin:
        return None
    key = coin.strip().lower().replace(" ", "").replace("-", "")
    return ALIASES.get(key)


def get_prices_usd_by_ids(ids: list[str], ttl=60) -> dict[str, dict]:
    """
    ids: list of CoinGecko IDs (e.g., ['bitcoin','ethereum'])
    returns: { 'bitcoin': {'price': 63123.45, 'change_24h': 2.1}, ... }
    """
    uniq_ids = sorted(set([i for i in ids if i]))
    if not uniq_ids:
        return {}

    cache_key = "cg:simple:" + ",".join(uniq_ids)
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        r = requests.get(
            API,
            params={
                "ids": ",".join(uniq_ids),
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=8,
        )
        r.raise_for_status()
        raw = r.json()
    except Exception:
        return {}

    out: dict[str, dict] = {}
    for cg_id, payload in raw.items():
        price = payload.get("usd")
        change = payload.get("usd_24h_change")
        if price is not None:
            out[cg_id] = {
                "price": float(price),
                "change_24h": float(change) if change is not None else None,
            }

    cache.set(cache_key, out, ttl)
    return out
