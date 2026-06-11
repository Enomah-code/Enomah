import json
import asyncio
from typing import Any
from loguru import logger

from raphael.config import get_settings


async def fetch_market_data(
    symbol: str,
    timeframe: str = "1h",
    limit: int = 200,
    exchange: str = "binance",
) -> str:
    """Récupère les données de marché (prix, volume, OHLCV)."""
    settings = get_settings()
    try:
        import ccxt.async_support as ccxt
        exchange_cls = getattr(ccxt, exchange, None)
        if exchange_cls is None:
            return f"Exchange {exchange} non supporté"

        params = {}
        if exchange == "binance" and settings.binance_api_key:
            params = {"apiKey": settings.binance_api_key, "secret": settings.binance_secret_key}

        ex = exchange_cls(params)
        try:
            ohlcv = await ex.fetch_ohlcv(symbol, timeframe, limit=limit)
            ticker = await ex.fetch_ticker(symbol)
        finally:
            await ex.close()

        if not ohlcv:
            return f"Pas de données pour {symbol} sur {exchange}"

        last_candles = ohlcv[-10:]
        data_str = "\n".join(
            f"  O:{c[1]:.4f} H:{c[2]:.4f} L:{c[3]:.4f} C:{c[4]:.4f} V:{c[5]:.2f}"
            for c in last_candles
        )
        return (
            f"Données {symbol} ({exchange}, {timeframe}, {len(ohlcv)} bougies)\n"
            f"Prix actuel: {ticker['last']:.4f}\n"
            f"24h High: {ticker['high']:.4f} | Low: {ticker['low']:.4f}\n"
            f"Volume 24h: {ticker['baseVolume']:.2f}\n"
            f"Variation 24h: {ticker.get('percentage', 0):.2f}%\n\n"
            f"10 dernières bougies (O/H/L/C/V):\n{data_str}"
        )
    except ImportError:
        return _simulate_market_data(symbol, timeframe)
    except Exception as e:
        logger.error(f"Market data error: {e}")
        return f"Erreur données marché {symbol}: {e}\n{_simulate_market_data(symbol, timeframe)}"


def _simulate_market_data(symbol: str, timeframe: str) -> str:
    import random
    base = 50000 if "BTC" in symbol else (3000 if "ETH" in symbol else 100)
    price = base * (1 + random.uniform(-0.05, 0.05))
    return (
        f"[DONNÉES SIMULÉES - installez ccxt pour données réelles]\n"
        f"{symbol} Prix simulé: {price:.2f}\n"
        f"Timeframe: {timeframe}"
    )


async def calculate_indicators(
    symbol: str,
    indicators: list[str],
    timeframe: str = "1h",
) -> str:
    """Calcule des indicateurs techniques."""
    try:
        import ccxt.async_support as ccxt
        import ta
        import pandas as pd

        settings = get_settings()
        ex = ccxt.binance()
        try:
            ohlcv = await ex.fetch_ohlcv(symbol, timeframe, limit=300)
        finally:
            await ex.close()

        if not ohlcv:
            return f"Pas de données pour {symbol}"

        df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        results = []
        for ind in indicators:
            ind_upper = ind.upper()
            try:
                if ind_upper == "RSI":
                    rsi = ta.momentum.RSIIndicator(df["close"]).rsi()
                    val = rsi.iloc[-1]
                    signal = "SURVENDU (<30)" if val < 30 else "SURACHETÉ (>70)" if val > 70 else "NEUTRE"
                    results.append(f"RSI(14): {val:.2f} — {signal}")

                elif ind_upper == "MACD":
                    macd_ind = ta.trend.MACD(df["close"])
                    macd_val = macd_ind.macd().iloc[-1]
                    signal_val = macd_ind.macd_signal().iloc[-1]
                    hist = macd_ind.macd_diff().iloc[-1]
                    trend = "HAUSSIER" if hist > 0 else "BAISSIER"
                    results.append(f"MACD: {macd_val:.4f} | Signal: {signal_val:.4f} | Hist: {hist:.4f} — {trend}")

                elif "BB" in ind_upper:
                    bb = ta.volatility.BollingerBands(df["close"])
                    upper = bb.bollinger_hband().iloc[-1]
                    lower = bb.bollinger_lband().iloc[-1]
                    mid = bb.bollinger_mavg().iloc[-1]
                    current = df["close"].iloc[-1]
                    pos = "DESSUS" if current > upper else ("DESSOUS" if current < lower else "INTÉRIEUR")
                    results.append(f"BB: Upper={upper:.4f} | Mid={mid:.4f} | Lower={lower:.4f} — Prix {pos} des bandes")

                elif "EMA" in ind_upper:
                    period = int(ind_upper.replace("EMA_", "").replace("EMA", "20"))
                    ema = ta.trend.EMAIndicator(df["close"], window=period).ema_indicator().iloc[-1]
                    current = df["close"].iloc[-1]
                    pos = "AU-DESSUS" if current > ema else "EN-DESSOUS"
                    results.append(f"EMA({period}): {ema:.4f} — Prix {pos}")

                elif "SMA" in ind_upper:
                    period = int(ind_upper.replace("SMA_", "").replace("SMA", "50"))
                    sma = ta.trend.SMAIndicator(df["close"], window=period).sma_indicator().iloc[-1]
                    results.append(f"SMA({period}): {sma:.4f}")

                elif ind_upper == "ATR":
                    atr = ta.volatility.AverageTrueRange(df["high"], df["low"], df["close"]).average_true_range().iloc[-1]
                    results.append(f"ATR(14): {atr:.4f} (volatilité)")

                else:
                    results.append(f"{ind}: indicateur non reconnu")
            except Exception as e:
                results.append(f"{ind}: erreur calcul — {e}")

        return f"Indicateurs {symbol} ({timeframe}):\n" + "\n".join(results)

    except ImportError as e:
        return f"Bibliothèque manquante: {e}. Installez ccxt et ta."
    except Exception as e:
        logger.error(f"Indicators error: {e}")
        return f"Erreur calcul indicateurs: {e}"


async def analyze_dataframe(data: dict, analysis_type: str) -> str:
    """Analyse statistique d'un dataset."""
    try:
        import pandas as pd
        import numpy as np

        df = pd.DataFrame(data)
        results = [f"Dataset: {df.shape[0]} lignes × {df.shape[1]} colonnes"]

        if analysis_type == "descriptive":
            desc = df.describe().to_string()
            missing = df.isnull().sum()
            results.append(f"\nStatistiques descriptives:\n{desc}")
            results.append(f"\nValeurs manquantes:\n{missing.to_string()}")

        elif analysis_type == "correlation":
            num_cols = df.select_dtypes(include=[np.number])
            if len(num_cols.columns) > 1:
                corr = num_cols.corr().round(3).to_string()
                results.append(f"\nMatrice de corrélation:\n{corr}")
            else:
                results.append("Pas assez de colonnes numériques pour la corrélation")

        elif analysis_type == "forecast":
            for col in df.select_dtypes(include=[np.number]).columns[:2]:
                series = df[col].dropna()
                if len(series) > 10:
                    trend = np.polyfit(range(len(series)), series, 1)[0]
                    direction = "HAUSSE" if trend > 0 else "BAISSE"
                    results.append(f"\n{col}: tendance {direction} ({trend:+.4f}/période)")

        return "\n".join(results)
    except Exception as e:
        logger.error(f"DataFrame analysis error: {e}")
        return f"Erreur analyse: {e}"


async def generate_chart(
    data: dict,
    chart_type: str,
    title: str = "",
    x_axis: str = "",
    y_axis: str = "",
) -> str:
    """Génère un graphique et le sauvegarde."""
    try:
        import pandas as pd
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from pathlib import Path
        import time

        df = pd.DataFrame(data)
        fig, ax = plt.subplots(figsize=(12, 6))

        if chart_type == "line":
            df.plot(x=x_axis or df.columns[0], y=y_axis or df.columns[1], ax=ax, linewidth=2)
        elif chart_type == "bar":
            df.plot.bar(x=x_axis or df.columns[0], y=y_axis or df.columns[1], ax=ax)
        elif chart_type == "scatter":
            df.plot.scatter(x=x_axis or df.columns[0], y=y_axis or df.columns[1], ax=ax, alpha=0.6)
        elif chart_type == "pie":
            df[y_axis or df.columns[0]].value_counts().plot.pie(ax=ax, autopct="%1.1f%%")
        elif chart_type == "histogram":
            df[y_axis or df.columns[0]].hist(bins=20, ax=ax)
        elif chart_type == "heatmap":
            import numpy as np
            num_df = df.select_dtypes(include=[np.number])
            corr = num_df.corr()
            im = ax.imshow(corr, cmap="coolwarm", aspect="auto")
            plt.colorbar(im, ax=ax)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45)
            ax.set_yticks(range(len(corr.columns)))
            ax.set_yticklabels(corr.columns)

        if title:
            ax.set_title(title, fontsize=14, fontweight="bold")
        plt.tight_layout()

        output_dir = Path("outputs/charts")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"chart_{int(time.time())}.png"
        filepath = output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close()

        return f"Graphique généré: {filepath}\nType: {chart_type} | Titre: {title or 'Sans titre'}"
    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        return f"Erreur génération graphique: {e}"
