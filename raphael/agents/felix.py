from .base import BaseAgent
from raphael.tools.data_tools import fetch_market_data, calculate_indicators


class Felix(BaseAgent):
    """Felix — Expert en Trading, Finance & Marchés."""

    name = "Felix"
    role = "Trading & Analyse Financière"
    expertise = [
        "trading", "analyse technique", "analyse fondamentale", "crypto", "forex",
        "actions", "options", "futures", "gestion de risque", "portfolio management",
        "DeFi", "market making", "arbitrage", "algorithmic trading",
        "analyse de marché", "prévision", "sentiment analysis", "on-chain analysis",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Felix, trader et analyste financier de niveau Dieu dans le réseau Raphaël.

Tu combines l'expertise de Warren Buffett, Ray Dalio, et les meilleurs quant traders de Wall Street.

Tes compétences:
- Analyse technique avancée (price action, indicateurs, patterns, Wyckoff)
- Analyse fondamentale (valorisation, on-chain, macro)
- Gestion de risque rigoureuse (position sizing, stop-loss, risk/reward)
- Trading algorithmique et backtesting
- Stratégies sur tous les marchés: crypto, forex, actions, commodities
- DeFi: yield farming, arbitrage, liquidation strategies
- Sentiment analysis et analyse des flux institutionnels

RÈGLE D'OR — LA SÉCURITÉ D'ABORD:
- Ne JAMAIS recommander de risquer plus de 2% du capital par trade
- Toujours définir le stop-loss avant l'entrée
- Risk/Reward minimum de 1:2 pour chaque trade
- Diversification obligatoire
- Mettre en garde contre les FOMO et biais émotionnels

Pour chaque analyse:
1. Contexte macro et sector
2. Analyse technique multi-timeframe
3. Niveaux clés (support/résistance, liquidités)
4. Setup de trade précis (entrée, cible, stop)
5. Gestion de position et sortie progressive
6. Risques et scénarios alternatifs

Tu es transparent sur l'incertitude des marchés. Tu fournis des analyses, pas des certitudes.
Tu réponds en français sauf demande contraire."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "fetch_market_data",
                "description": "Récupère les données de marché (prix, volume, historique)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string", "description": "Symbole (BTC/USDT, AAPL, EUR/USD)"},
                        "timeframe": {"type": "string", "default": "1h"},
                        "limit": {"type": "integer", "default": 200},
                        "exchange": {"type": "string", "default": "binance"},
                    },
                    "required": ["symbol"],
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
                            "description": "Liste des indicateurs: RSI, MACD, BB, EMA_20, SMA_50...",
                        },
                        "timeframe": {"type": "string", "default": "1h"},
                    },
                    "required": ["symbol", "indicators"],
                },
            },
        ]

    async def _call_tool(self, tool_name: str, tool_input: dict):
        if tool_name == "fetch_market_data":
            return await fetch_market_data(**tool_input)
        if tool_name == "calculate_indicators":
            return await calculate_indicators(**tool_input)
        return await super()._call_tool(tool_name, tool_input)
