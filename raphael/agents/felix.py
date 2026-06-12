from .base import BaseAgent
from raphael.tools.data_tools import fetch_market_data, calculate_indicators
from raphael.tools.binance_tools import (
    get_binance_ticker, get_binance_orderbook, get_binance_klines,
    get_binance_portfolio, get_binance_top_movers, get_funding_rates,
)


class Felix(BaseAgent):
    """Felix — Expert en Trading, Finance & Marchés (Binance avancé)."""

    name = "Felix"
    role = "Trading & Analyse Financière"
    expertise = [
        "trading", "analyse technique", "analyse fondamentale", "crypto", "forex",
        "actions", "options", "futures", "gestion de risque", "portfolio management",
        "DeFi", "market making", "arbitrage", "algorithmic trading",
        "analyse de marché", "prévision", "sentiment analysis", "on-chain analysis",
        "Binance", "spot trading", "futures trading", "funding rates", "orderbook",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Felix, trader et analyste financier de niveau Dieu dans le réseau Raphaël.

Tu combines l'expertise de Warren Buffett, Ray Dalio, et les meilleurs quant traders de Wall Street.

Tes compétences:
- Analyse technique avancée (price action, indicateurs, patterns, Wyckoff, SMC)
- Analyse fondamentale (valorisation, on-chain, macro, tokenomics)
- Gestion de risque rigoureuse (position sizing, stop-loss, risk/reward)
- Trading algorithmique et backtesting sur Binance
- Stratégies sur tous les marchés: crypto, forex, actions, commodities
- DeFi: yield farming, arbitrage, liquidation strategies
- Lecture du carnet d'ordres (order flow, liquidité, market depth)
- Analyse des taux de financement (funding rates) pour le sentiment
- Gestion de portefeuille crypto multi-actifs

RÈGLE D'OR — LA SÉCURITÉ D'ABORD:
- Ne JAMAIS recommander de risquer plus de 2% du capital par trade
- Toujours définir le stop-loss avant l'entrée
- Risk/Reward minimum de 1:2.5 pour chaque trade
- Diversification obligatoire (max 20% sur un seul actif)
- Mettre en garde contre les FOMO et biais émotionnels

Format d'analyse obligatoire:
📊 **Contexte Macro**
📈 **Analyse Technique** (multi-timeframe: 4H, 1H, 15min)
🎯 **Setup de Trade** (entrée, TP1, TP2, Stop-Loss)
⚠️ **Risques** (liquidations, résistances majeures, catalyseurs)
💼 **Position Sizing** (% recommandé du capital)

Tu es transparent sur l'incertitude des marchés. Tu fournis des analyses, pas des certitudes.
Tu réponds en français sauf demande contraire."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "get_binance_ticker",
                "description": "Prix temps réel et stats 24h d'un symbole Binance",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Ex: BTC/USDT, ETH/USDT"},
                        "market": {"type": "string", "enum": ["spot", "futures"], "default": "spot"},
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "get_binance_top_movers",
                "description": "Top hausses et baisses 24h sur Binance",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 10},
                    },
                },
            },
            {
                "name": "get_binance_orderbook",
                "description": "Carnet d'ordres pour analyser la liquidité et les niveaux clés",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "depth": {"type": "integer", "default": 10},
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "get_funding_rates",
                "description": "Taux de financement Binance Futures — indicateur de sentiment du marché",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbols": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Liste de symboles (vide = top 10 par magnitude)",
                        },
                    },
                },
            },
            {
                "name": "calculate_indicators",
                "description": "Calcule des indicateurs techniques (RSI, MACD, BB, EMA...)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "RSI, MACD, BB, EMA_20, SMA_50, ATR...",
                        },
                        "timeframe": {"type": "string", "default": "1h"},
                    },
                    "required": ["symbol", "indicators"],
                },
            },
            {
                "name": "get_binance_portfolio",
                "description": "Soldes du portefeuille Binance (nécessite clés API)",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "fetch_market_data",
                "description": "Données OHLCV historiques via CCXT",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "timeframe": {"type": "string", "default": "1h"},
                        "limit": {"type": "integer", "default": 200},
                    },
                    "required": ["symbol"],
                },
            },
        ]

    async def _call_tool(self, tool_name: str, tool_input: dict):
        if tool_name == "get_binance_ticker":
            return await get_binance_ticker(**tool_input)
        if tool_name == "get_binance_top_movers":
            return await get_binance_top_movers(**tool_input)
        if tool_name == "get_binance_orderbook":
            return await get_binance_orderbook(**tool_input)
        if tool_name == "get_funding_rates":
            return await get_funding_rates(**tool_input)
        if tool_name == "calculate_indicators":
            return await calculate_indicators(**tool_input)
        if tool_name == "get_binance_portfolio":
            return await get_binance_portfolio()
        if tool_name == "fetch_market_data":
            return await fetch_market_data(**tool_input)
        return await super()._call_tool(tool_name, tool_input)
