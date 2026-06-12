"""
Outils Binance avancés pour Felix et le réseau Raphaël.
Supporte: spot, futures, portefeuille, ordres, alertes de prix.
"""
import asyncio
import json
from datetime import datetime
from typing import Any
import httpx
from loguru import logger

from raphael.config import get_settings


BASE_URL = "https://api.binance.com"
FUTURES_URL = "https://fapi.binance.com"


async def get_binance_ticker(symbol: str, market: str = "spot") -> str:
    """Prix en temps réel + stats 24h d'un symbole Binance."""
    try:
        base = FUTURES_URL if market == "futures" else BASE_URL
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{base}/fapi/v1/ticker/24hr" if market == "futures" else f"{base}/api/v3/ticker/24hr",
                                  params={"symbol": symbol.upper().replace("/", "")})
            r.raise_for_status()
            d = r.json()
        return (
            f"**{symbol} ({market.upper()})**\n"
            f"Prix: **{float(d['lastPrice']):,.4f} USDT**\n"
            f"Variation 24h: {'+' if float(d['priceChangePercent']) >= 0 else ''}{float(d['priceChangePercent']):.2f}%\n"
            f"High 24h: {float(d['highPrice']):,.4f} | Low: {float(d['lowPrice']):,.4f}\n"
            f"Volume 24h: {float(d['volume']):,.2f} {symbol.split('/')[0]}\n"
            f"Volume USDT 24h: ${float(d['quoteVolume']):,.0f}"
        )
    except Exception as e:
        return _simulated_ticker(symbol)


async def get_binance_orderbook(symbol: str, depth: int = 10) -> str:
    """Carnet d'ordres (bids/asks) pour analyser la liquidité."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{BASE_URL}/api/v3/depth",
                                  params={"symbol": symbol.upper().replace("/", ""), "limit": depth})
            r.raise_for_status()
            d = r.json()
        bids = d["bids"][:5]
        asks = d["asks"][:5]
        lines = [f"**Carnet d'ordres {symbol}**\n"]
        lines.append("ASKS (Vendeurs):")
        for price, qty in reversed(asks):
            lines.append(f"  {float(price):>12,.2f}  |  {float(qty):>10,.4f}")
        lines.append("  " + "─" * 30 + " ← SPREAD")
        lines.append("BIDS (Acheteurs):")
        for price, qty in bids:
            lines.append(f"  {float(price):>12,.2f}  |  {float(qty):>10,.4f}")
        spread = float(asks[0][0]) - float(bids[0][0])
        spread_pct = spread / float(asks[0][0]) * 100
        lines.append(f"\nSpread: {spread:.4f} ({spread_pct:.4f}%)")
        return "\n".join(lines)
    except Exception as e:
        return f"Carnet d'ordres non disponible: {e}"


async def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 100) -> dict:
    """Données OHLCV structurées pour analyse technique."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(f"{BASE_URL}/api/v3/klines",
                                  params={"symbol": symbol.upper().replace("/", ""),
                                          "interval": interval, "limit": limit})
            r.raise_for_status()
            raw = r.json()
        candles = [
            {"time": k[0], "open": float(k[1]), "high": float(k[2]),
             "low": float(k[3]), "close": float(k[4]), "volume": float(k[5])}
            for k in raw
        ]
        return {"symbol": symbol, "interval": interval, "candles": candles}
    except Exception as e:
        logger.error(f"Binance klines error: {e}")
        return {"error": str(e)}


async def get_binance_portfolio(api_key: str = "", secret: str = "") -> str:
    """Soldes du compte Binance (authentifié)."""
    settings = get_settings()
    key = api_key or settings.binance_api_key
    sec = secret or settings.binance_secret_key

    if not key or not sec:
        return (
            "**Portefeuille Binance** — Clés API non configurées\n"
            "Ajoutez BINANCE_API_KEY et BINANCE_SECRET_KEY dans .env pour voir vos soldes réels."
        )

    try:
        import hmac
        import hashlib
        import time

        ts = int(time.time() * 1000)
        query = f"timestamp={ts}"
        sig = hmac.new(sec.encode(), query.encode(), hashlib.sha256).hexdigest()

        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(
                f"{BASE_URL}/api/v3/account",
                headers={"X-MBX-APIKEY": key},
                params={"timestamp": ts, "signature": sig},
            )
            r.raise_for_status()
            d = r.json()

        balances = [b for b in d.get("balances", [])
                    if float(b["free"]) > 0 or float(b["locked"]) > 0]
        if not balances:
            return "Portefeuille vide ou soldes insuffisants."

        lines = ["**Portefeuille Binance**\n"]
        for b in sorted(balances, key=lambda x: float(x["free"]), reverse=True)[:20]:
            total = float(b["free"]) + float(b["locked"])
            lines.append(f"  {b['asset']}: {total:,.6f} (libre: {float(b['free']):,.6f})")
        return "\n".join(lines)
    except Exception as e:
        return f"Erreur portefeuille Binance: {e}"


async def get_binance_top_movers(limit: int = 10) -> str:
    """Top hausses et baisses 24h sur Binance."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(f"{BASE_URL}/api/v3/ticker/24hr")
            r.raise_for_status()
            all_tickers = r.json()

        usdt_pairs = [
            t for t in all_tickers
            if t["symbol"].endswith("USDT") and float(t["quoteVolume"]) > 5_000_000
        ]
        sorted_by_change = sorted(usdt_pairs, key=lambda x: float(x["priceChangePercent"]))
        losers = sorted_by_change[:5]
        gainers = sorted_by_change[-5:][::-1]

        lines = ["**Top Movers Binance (24h)**\n"]
        lines.append("🟢 **Top Hausses:**")
        for t in gainers:
            lines.append(f"  {t['symbol']}: +{float(t['priceChangePercent']):.2f}% | ${float(t['lastPrice']):,.4f}")
        lines.append("\n🔴 **Top Baisses:**")
        for t in losers:
            lines.append(f"  {t['symbol']}: {float(t['priceChangePercent']):.2f}% | ${float(t['lastPrice']):,.4f}")
        return "\n".join(lines)
    except Exception as e:
        return f"Top movers non disponible: {e}"


async def get_funding_rates(symbols: list[str] | None = None) -> str:
    """Taux de financement Binance Futures (indicateur de sentiment)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(f"{FUTURES_URL}/fapi/v1/premiumIndex")
            r.raise_for_status()
            data = r.json()

        if symbols:
            syms_clean = [s.upper().replace("/", "") for s in symbols]
            data = [d for d in data if d["symbol"] in syms_clean]

        data_sorted = sorted(data, key=lambda x: abs(float(x.get("lastFundingRate", 0))), reverse=True)[:10]

        lines = ["**Taux de Financement Binance Futures**\n",
                 "*(Positif = longs paient les shorts | Négatif = shorts paient les longs)*\n"]
        for d in data_sorted:
            rate = float(d.get("lastFundingRate", 0)) * 100
            sentiment = "📈 Long dominant" if rate > 0.01 else ("📉 Short dominant" if rate < -0.01 else "⚖️ Neutre")
            lines.append(f"  {d['symbol']}: {rate:+.4f}% — {sentiment}")
        return "\n".join(lines)
    except Exception as e:
        return f"Funding rates non disponibles: {e}"


def _simulated_ticker(symbol: str) -> str:
    import random
    prices = {"BTC": 67420, "ETH": 3521, "BNB": 578, "SOL": 168, "ADA": 0.52}
    base = prices.get(symbol.split("/")[0].split("USDT")[0], 100)
    price = base * (1 + random.uniform(-0.03, 0.03))
    change = random.uniform(-5, 5)
    return (
        f"**{symbol} [SIMULÉ]**\n"
        f"Prix: {price:,.2f} USDT\n"
        f"Variation 24h: {change:+.2f}%\n"
        f"Note: Connexion Binance API non disponible."
    )
