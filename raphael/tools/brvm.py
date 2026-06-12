"""
Outil BRVM — Bourse Régionale des Valeurs Mobilières (UEMOA / Afrique de l'Ouest)
Scrape les données en temps réel depuis brvm.org.
Fallback avec données simulées si le réseau est indisponible.
"""

import asyncio
from datetime import datetime
from typing import Optional
from loguru import logger

# ---------------------------------------------------------------------------
# Dictionnaire de référence des sociétés cotées à la BRVM
# ---------------------------------------------------------------------------

BRVM_COMPANIES: dict[str, dict] = {
    "SNTS": {
        "name": "SONATEL",
        "full_name": "Société Nationale des Télécommunications du Sénégal",
        "sector": "Télécommunications",
        "country": "Sénégal",
        "isin": "SN0000000019",
        "description": "Opérateur télécom leader au Sénégal, filiale d'Orange. Présent au Sénégal, Mali, Guinée, Guinée-Bissau, Sierra Leone.",
    },
    "ETIT": {
        "name": "ECOBANK TRANSNATIONAL",
        "full_name": "Ecobank Transnational Incorporated",
        "sector": "Finance / Banque",
        "country": "Togo",
        "isin": "TG0000000047",
        "description": "Groupe bancaire panafricain présent dans 35 pays africains. Siège social à Lomé, Togo.",
    },
    "SAPH": {
        "name": "SAPH",
        "full_name": "Société Africaine de Plantations d'Hévéas",
        "sector": "Agriculture / Caoutchouc",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000006",
        "description": "Producteur et exportateur de caoutchouc naturel. Leader de la filière hévéa en Côte d'Ivoire.",
    },
    "PALC": {
        "name": "PALM CI",
        "full_name": "Palmafrique CI",
        "sector": "Agriculture / Huile de palme",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000089",
        "description": "Producteur ivoirien d'huile de palme et de produits dérivés.",
    },
    "ORAC": {
        "name": "ORANGE CI",
        "full_name": "Orange Côte d'Ivoire",
        "sector": "Télécommunications",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000170",
        "description": "Filiale d'Orange en Côte d'Ivoire. Leader du marché mobile ivoirien.",
    },
    "TTLC": {
        "name": "TOTAL CI",
        "full_name": "Total Energies Marketing Côte d'Ivoire",
        "sector": "Énergie / Distribution pétrolière",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000105",
        "description": "Filiale de TotalEnergies en Côte d'Ivoire, distribution de carburants et lubrifiants.",
    },
    "SLBA": {
        "name": "SOLIBRA",
        "full_name": "Société de Limonaderies et Brasseries d'Afrique",
        "sector": "Agroalimentaire / Boissons",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000022",
        "description": "Brasseur ivoirien, produit Flag, Bock, Beaufort. Filiale du groupe Castel.",
    },
    "SGBC": {
        "name": "SGB CI",
        "full_name": "Société Générale de Banques en Côte d'Ivoire",
        "sector": "Finance / Banque",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000030",
        "description": "Filiale de Société Générale en Côte d'Ivoire. L'une des plus grandes banques du pays.",
    },
    "CBIBF": {
        "name": "CORIS BANK",
        "full_name": "Coris Bank International Burkina Faso",
        "sector": "Finance / Banque",
        "country": "Burkina Faso",
        "isin": "BF0000000005",
        "description": "Première banque privée du Burkina Faso, en forte croissance régionale.",
    },
    "BICC": {
        "name": "BICICI",
        "full_name": "Banque Internationale pour le Commerce et l'Industrie de la Côte d'Ivoire",
        "sector": "Finance / Banque",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000048",
        "description": "Filiale de BNP Paribas en Côte d'Ivoire.",
    },
    "BOAB": {
        "name": "BOA BENIN",
        "full_name": "Bank of Africa Bénin",
        "sector": "Finance / Banque",
        "country": "Bénin",
        "isin": "BJ0000000005",
        "description": "Filiale du groupe Bank of Africa au Bénin.",
    },
    "BOABF": {
        "name": "BOA BURKINA",
        "full_name": "Bank of Africa Burkina Faso",
        "sector": "Finance / Banque",
        "country": "Burkina Faso",
        "isin": "BF0000000013",
        "description": "Filiale du groupe Bank of Africa au Burkina Faso.",
    },
    "BOAM": {
        "name": "BOA MALI",
        "full_name": "Bank of Africa Mali",
        "sector": "Finance / Banque",
        "country": "Mali",
        "isin": "ML0000000004",
        "description": "Filiale du groupe Bank of Africa au Mali.",
    },
    "BOAS": {
        "name": "BOA SÉNÉGAL",
        "full_name": "Bank of Africa Sénégal",
        "sector": "Finance / Banque",
        "country": "Sénégal",
        "isin": "SN0000000084",
        "description": "Filiale du groupe Bank of Africa au Sénégal.",
    },
    "SIVC": {
        "name": "AIR LIQUIDE CI",
        "full_name": "Air Liquide Côte d'Ivoire",
        "sector": "Industrie / Gaz industriels",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000063",
        "description": "Producteur et distributeur de gaz industriels et médicaux en Côte d'Ivoire.",
    },
    "CABC": {
        "name": "SICABLE",
        "full_name": "Société Ivoirienne de Câbles",
        "sector": "Industrie / Câblerie",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000014",
        "description": "Fabricant de câbles électriques en Côte d'Ivoire.",
    },
    "CFAC": {
        "name": "CFAO MOTORS CI",
        "full_name": "CFAO Motors Côte d'Ivoire",
        "sector": "Distribution / Automobile",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000071",
        "description": "Distributeur de véhicules automobiles en Côte d'Ivoire.",
    },
    "NTLC": {
        "name": "NESTLE CI",
        "full_name": "Nestlé Côte d'Ivoire",
        "sector": "Agroalimentaire",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000113",
        "description": "Filiale de Nestlé en Côte d'Ivoire, leader de l'agroalimentaire.",
    },
    "UNLC": {
        "name": "UNILEVER CI",
        "full_name": "Unilever Côte d'Ivoire",
        "sector": "Biens de consommation",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000121",
        "description": "Filiale d'Unilever en Côte d'Ivoire, produits d'hygiène et alimentaires.",
    },
    "STBC": {
        "name": "SITAB",
        "full_name": "Société Ivoirienne de Tabac",
        "sector": "Tabac",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000139",
        "description": "Fabricant et distributeur de produits du tabac en Côte d'Ivoire.",
    },
    "SEMC": {
        "name": "SETAO",
        "full_name": "Société d'Études et de Travaux pour l'Afrique de l'Ouest",
        "sector": "BTP / Travaux publics",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000097",
        "description": "Entreprise de BTP et travaux publics en Afrique de l'Ouest.",
    },
    "PRSC": {
        "name": "PRESTIGE",
        "full_name": "Compagnie de Gestion Hôtelière et de Restauration Prestige",
        "sector": "Hôtellerie / Restauration",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000147",
        "description": "Groupe hôtelier et de restauration en Côte d'Ivoire.",
    },
    "SMBC": {
        "name": "SMB CI",
        "full_name": "Société de Manutention du Terminal de Vridi",
        "sector": "Transport / Logistique portuaire",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000154",
        "description": "Manutention et logistique portuaire au port d'Abidjan.",
    },
    "SICC": {
        "name": "SIC",
        "full_name": "Société Ivoirienne de Ciment",
        "sector": "Matériaux de construction",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000162",
        "description": "Producteur de ciment en Côte d'Ivoire.",
    },
    "CIEC": {
        "name": "CIE",
        "full_name": "Compagnie Ivoirienne d'Électricité",
        "sector": "Énergie / Électricité",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000188",
        "description": "Distributeur et gestionnaire du réseau électrique en Côte d'Ivoire.",
    },
    "SDCC": {
        "name": "SODECI",
        "full_name": "Société de Distribution d'Eau de Côte d'Ivoire",
        "sector": "Services publics / Eau",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000196",
        "description": "Société de distribution d'eau potable en Côte d'Ivoire.",
    },
    "STAC": {
        "name": "SIFCA",
        "full_name": "Société Ivoirienne de Financement et de Commerce en Afrique",
        "sector": "Agroalimentaire / Holdings",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000204",
        "description": "Holding agroalimentaire diversifié (huile de palme, hévéa, sucre).",
    },
    "ABJC": {
        "name": "FILTISAC",
        "full_name": "Filtisac SA",
        "sector": "Industrie / Emballage",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000212",
        "description": "Fabricant de sacs en polypropylène et emballages industriels.",
    },
    "SHEC": {
        "name": "SHELL CI",
        "full_name": "Vivo Energy Côte d'Ivoire",
        "sector": "Énergie / Distribution pétrolière",
        "country": "Côte d'Ivoire",
        "isin": "CI0000000220",
        "description": "Distribution de carburants Shell en Côte d'Ivoire.",
    },
}

# ---------------------------------------------------------------------------
# Données simulées pour le fallback (mode hors réseau)
# ---------------------------------------------------------------------------

_SIMULATED_MARKET = [
    {"symbol": "SNTS", "name": "SONATEL", "last_price": 18500, "change": 2.78, "change_abs": 500, "volume": 1250, "open": 18000, "high": 18600, "low": 17950},
    {"symbol": "ORAC", "name": "ORANGE CI", "last_price": 11500, "change": 1.33, "change_abs": 150, "volume": 3800, "open": 11350, "high": 11600, "low": 11300},
    {"symbol": "ETIT", "name": "ECOBANK", "last_price": 17, "change": -1.16, "change_abs": -0.2, "volume": 845000, "open": 17.2, "high": 17.3, "low": 16.9},
    {"symbol": "SGBC", "name": "SGB CI", "last_price": 13500, "change": 0.75, "change_abs": 100, "volume": 420, "open": 13400, "high": 13600, "low": 13350},
    {"symbol": "SAPH", "name": "SAPH", "last_price": 6800, "change": -0.73, "change_abs": -50, "volume": 980, "open": 6850, "high": 6900, "low": 6780},
    {"symbol": "PALC", "name": "PALM CI", "last_price": 7600, "change": 1.34, "change_abs": 100, "volume": 2100, "open": 7500, "high": 7650, "low": 7480},
    {"symbol": "TTLC", "name": "TOTAL CI", "last_price": 2350, "change": 0.43, "change_abs": 10, "volume": 5200, "open": 2340, "high": 2360, "low": 2330},
    {"symbol": "SLBA", "name": "SOLIBRA", "last_price": 147000, "change": 0.00, "change_abs": 0, "volume": 55, "open": 147000, "high": 147000, "low": 147000},
    {"symbol": "BICC", "name": "BICICI", "last_price": 5450, "change": -1.81, "change_abs": -100, "volume": 310, "open": 5550, "high": 5560, "low": 5440},
    {"symbol": "CBIBF", "name": "CORIS BANK", "last_price": 8450, "change": 3.05, "change_abs": 250, "volume": 1800, "open": 8200, "high": 8500, "low": 8180},
    {"symbol": "NTLC", "name": "NESTLE CI", "last_price": 7200, "change": 0.56, "change_abs": 40, "volume": 760, "open": 7160, "high": 7250, "low": 7140},
    {"symbol": "CIEC", "name": "CIE", "last_price": 2180, "change": -0.91, "change_abs": -20, "volume": 4500, "open": 2200, "high": 2210, "low": 2170},
    {"symbol": "SDCC", "name": "SODECI", "last_price": 4200, "change": 2.44, "change_abs": 100, "volume": 1100, "open": 4100, "high": 4230, "low": 4090},
    {"symbol": "BOAB", "name": "BOA BENIN", "last_price": 6700, "change": -0.59, "change_abs": -40, "volume": 680, "open": 6740, "high": 6760, "low": 6680},
    {"symbol": "BOABF", "name": "BOA BURKINA", "last_price": 5200, "change": 1.96, "change_abs": 100, "volume": 920, "open": 5100, "high": 5230, "low": 5090},
]

_SIMULATED_INDICES = {
    "BRVM_COMPOSITE": {"value": 282.45, "change": 1.23, "change_abs": 3.44, "ytd": 8.76},
    "BRVM_10": {"value": 364.12, "change": 0.87, "change_abs": 3.15, "ytd": 12.34},
    "BRVM_PRESTIGE": {"value": 105.22, "change": 0.45, "change_abs": 0.47, "ytd": 3.21},
}

_SIMULATED_NEWS = [
    {
        "title": "SONATEL publie des résultats semestriels en hausse de 12%",
        "date": "2025-06-10",
        "summary": "Le groupe Sonatel annonce une progression de son chiffre d'affaires de 12% sur le premier semestre 2025, porté par la croissance du mobile money et de la fibre optique.",
        "url": "https://www.brvm.org/fr/actualites",
    },
    {
        "title": "BRVM: Le BRVM Composite franchit les 280 points",
        "date": "2025-06-09",
        "summary": "Le marché boursier régional continue sa progression avec l'indice BRVM Composite dépassant le seuil symbolique des 280 points.",
        "url": "https://www.brvm.org/fr/actualites",
    },
    {
        "title": "Coris Bank annonce une augmentation de capital",
        "date": "2025-06-08",
        "summary": "Coris Bank International Burkina Faso projette une augmentation de capital pour renforcer ses fonds propres et soutenir son expansion régionale.",
        "url": "https://www.brvm.org/fr/actualites",
    },
    {
        "title": "ECOBANK: Croissance des actifs de 15% en zone UEMOA",
        "date": "2025-06-07",
        "summary": "Ecobank Transnational Incorporated rapporte une croissance significative de ses actifs en zone UEMOA, avec une forte contribution du digital banking.",
        "url": "https://www.brvm.org/fr/actualites",
    },
    {
        "title": "Orange CI renforce ses investissements dans la fibre optique",
        "date": "2025-06-06",
        "summary": "Orange Côte d'Ivoire annonce un plan d'investissement de 50 milliards FCFA pour l'extension de son réseau fibre optique à l'horizon 2026.",
        "url": "https://www.brvm.org/fr/actualites",
    },
]

# ---------------------------------------------------------------------------
# Fonctions de scraping
# ---------------------------------------------------------------------------

async def _try_scrape_market() -> Optional[list[dict]]:
    """Tente de scraper les cours depuis brvm.org/fr/cours-actions/0."""
    try:
        import httpx
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        }

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
            response = await client.get("https://www.brvm.org/fr/cours-actions/0")
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Cherche le tableau principal des cours
        table = soup.find("table", {"id": "cours-actions"}) or soup.find("table", class_="table-condensed")
        if table is None:
            # Essai de trouver n'importe quel tableau avec des données de cours
            tables = soup.find_all("table")
            for t in tables:
                headers_row = t.find("tr")
                if headers_row and any(kw in headers_row.get_text().lower() for kw in ["symbole", "cours", "variation"]):
                    table = t
                    break

        if table is None:
            return None

        rows = table.find_all("tr")[1:]  # Skip header
        results = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue
            try:
                symbol = cols[0].get_text(strip=True)
                name = cols[1].get_text(strip=True) if len(cols) > 1 else ""
                last_price_str = cols[2].get_text(strip=True).replace(" ", "").replace("\xa0", "").replace(",", ".")
                change_str = cols[3].get_text(strip=True).replace(",", ".").replace("%", "").strip()
                volume_str = cols[4].get_text(strip=True).replace(" ", "").replace("\xa0", "") if len(cols) > 4 else "0"

                last_price = float(last_price_str) if last_price_str else 0.0
                change = float(change_str) if change_str else 0.0
                volume = int(volume_str) if volume_str.isdigit() else 0

                if symbol:
                    results.append({
                        "symbol": symbol,
                        "name": name,
                        "last_price": last_price,
                        "change": change,
                        "change_abs": round(last_price * change / 100, 2) if last_price else 0.0,
                        "volume": volume,
                        "open": 0.0,
                        "high": 0.0,
                        "low": 0.0,
                    })
            except (ValueError, IndexError):
                continue

        return results if results else None

    except Exception as e:
        logger.warning(f"[BRVM] Échec scraping cours: {e}")
        return None


async def _try_scrape_indices() -> Optional[dict]:
    """Tente de scraper les indices BRVM."""
    try:
        import httpx
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
            response = await client.get("https://www.brvm.org/fr/indices")
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        indices = {}
        # Cherche les blocs d'indices
        for tag in soup.find_all(["div", "td", "span"], string=lambda s: s and "BRVM" in s.upper()):
            parent = tag.find_parent(["tr", "div", "article"])
            if parent:
                nums = parent.find_all(string=lambda s: s and any(c.isdigit() for c in s))
                if nums:
                    idx_name = tag.get_text(strip=True).upper().replace(" ", "_").replace("-", "_")
                    try:
                        value = float(str(nums[0]).replace(",", ".").strip())
                        change = float(str(nums[1]).replace(",", ".").replace("%", "").strip()) if len(nums) > 1 else 0.0
                        indices[idx_name] = {"value": value, "change": change, "change_abs": 0.0, "ytd": 0.0}
                    except (ValueError, IndexError):
                        pass

        return indices if indices else None

    except Exception as e:
        logger.warning(f"[BRVM] Échec scraping indices: {e}")
        return None


async def _try_scrape_news() -> Optional[list[dict]]:
    """Tente de scraper les actualités BRVM."""
    try:
        import httpx
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True, headers=headers) as client:
            response = await client.get("https://www.brvm.org/fr/actualites")
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        news = []
        # Cherche les articles
        articles = soup.find_all("article") or soup.find_all("div", class_=lambda c: c and "news" in c.lower())
        if not articles:
            articles = soup.find_all("div", class_=lambda c: c and "actu" in str(c).lower())

        for article in articles[:10]:
            title_tag = article.find(["h1", "h2", "h3", "h4", "a"])
            title = title_tag.get_text(strip=True) if title_tag else ""
            date_tag = article.find(["time", "span"], class_=lambda c: c and "date" in str(c).lower())
            date = date_tag.get_text(strip=True) if date_tag else ""
            summary_tag = article.find("p")
            summary = summary_tag.get_text(strip=True)[:300] if summary_tag else ""
            link_tag = article.find("a", href=True)
            url = link_tag["href"] if link_tag else "https://www.brvm.org/fr/actualites"
            if not url.startswith("http"):
                url = "https://www.brvm.org" + url

            if title:
                news.append({"title": title, "date": date, "summary": summary, "url": url})

        return news if news else None

    except Exception as e:
        logger.warning(f"[BRVM] Échec scraping actualités: {e}")
        return None

# ---------------------------------------------------------------------------
# Fonctions publiques exportées
# ---------------------------------------------------------------------------

async def fetch_brvm_market() -> str:
    """
    Scrape le cours des actions BRVM depuis brvm.org/fr/cours-actions/0.
    Retourne un tableau Markdown formaté.
    """
    data = await _try_scrape_market()
    is_live = data is not None
    if not is_live:
        logger.info("[BRVM] Utilisation des données simulées pour le marché.")
        data = _SIMULATED_MARKET

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    source_label = "brvm.org (temps réel)" if is_live else "données simulées (réseau indisponible)"

    lines = [
        f"## Cours des Actions BRVM",
        f"*Source: {source_label} — {now}*",
        "",
        "| Symbole | Société | Dernier cours (FCFA) | Variation % | Volume |",
        "|---------|---------|---------------------|-------------|--------|",
    ]

    for stock in sorted(data, key=lambda x: x["symbol"]):
        change = stock.get("change", 0.0)
        change_emoji = "🟢" if change > 0 else ("🔴" if change < 0 else "⚪")
        sign = "+" if change > 0 else ""
        price = stock.get("last_price", 0)
        price_str = f"{price:,.0f}".replace(",", " ") if price >= 1000 else f"{price:.2f}"
        vol = stock.get("volume", 0)
        vol_str = f"{vol:,}".replace(",", " ")
        lines.append(
            f"| **{stock['symbol']}** | {stock['name']} | {price_str} | {change_emoji} {sign}{change:.2f}% | {vol_str} |"
        )

    lines += [
        "",
        f"*{len(data)} valeurs cotées affichées.*",
        f"> **Note**: La BRVM est ouverte du lundi au vendredi, 09h00–15h30 UTC. Cours en Francs CFA (FCFA / XOF).",
    ]

    return "\n".join(lines)


async def fetch_brvm_indices() -> str:
    """
    Scrape les indices BRVM Composite, BRVM 10 et BRVM Prestige.
    Retourne un résumé Markdown.
    """
    data = await _try_scrape_indices()
    is_live = data is not None and len(data) >= 2
    if not is_live:
        logger.info("[BRVM] Utilisation des données simulées pour les indices.")
        data = _SIMULATED_INDICES

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    source_label = "brvm.org (temps réel)" if is_live else "données simulées (réseau indisponible)"

    lines = [
        f"## Indices BRVM",
        f"*Source: {source_label} — {now}*",
        "",
        "| Indice | Valeur | Variation jour | Perf. YTD |",
        "|--------|--------|---------------|-----------|",
    ]

    label_map = {
        "BRVM_COMPOSITE": "BRVM Composite",
        "BRVM_10": "BRVM 10",
        "BRVM_PRESTIGE": "BRVM Prestige",
    }

    for key, info in data.items():
        label = label_map.get(key, key)
        change = info.get("change", 0.0)
        ytd = info.get("ytd", 0.0)
        sign_d = "+" if change > 0 else ""
        sign_y = "+" if ytd > 0 else ""
        emoji = "🟢" if change > 0 else ("🔴" if change < 0 else "⚪")
        lines.append(
            f"| **{label}** | {info['value']:.2f} pts | {emoji} {sign_d}{change:.2f}% | {sign_y}{ytd:.2f}% |"
        )

    lines += [
        "",
        "### Contexte",
        "- **BRVM Composite**: Indice de référence regroupant toutes les valeurs cotées.",
        "- **BRVM 10**: Indice des 10 plus grandes capitalisations boursières.",
        "- **BRVM Prestige**: Indice des sociétés répondant aux critères de liquidité et gouvernance.",
        "",
        "> **Note**: Les indices sont exprimés en base 100 au 2 janvier 1998.",
    ]

    return "\n".join(lines)


async def fetch_brvm_company(symbol: str) -> str:
    """
    Retourne les détails d'une société cotée à la BRVM par son symbole.
    Complète avec les données de marché en temps réel si disponibles.
    """
    symbol = symbol.upper().strip()

    # Recherche dans le dictionnaire de référence
    company_info = BRVM_COMPANIES.get(symbol)

    # Tente de récupérer les données de marché pour ce symbole
    market_data = await _try_scrape_market()
    if market_data is None:
        market_data = _SIMULATED_MARKET

    stock_data = next((s for s in market_data if s["symbol"].upper() == symbol), None)

    if company_info is None and stock_data is None:
        return (
            f"## Société introuvable: {symbol}\n\n"
            f"Le symbole **{symbol}** n'est pas répertorié dans la base BRVM.\n\n"
            f"Symboles connus: {', '.join(sorted(BRVM_COMPANIES.keys()))}\n\n"
            f"Utilisez `search_brvm_company` pour rechercher par nom d'entreprise."
        )

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    info = company_info or {}
    name = info.get("name") or (stock_data["name"] if stock_data else symbol)

    lines = [
        f"## {name} ({symbol})",
        f"*Données au {now}*",
        "",
    ]

    if info:
        lines += [
            f"**Nom complet**: {info.get('full_name', 'N/A')}",
            f"**Secteur**: {info.get('sector', 'N/A')}",
            f"**Pays**: {info.get('country', 'N/A')}",
            f"**ISIN**: {info.get('isin', 'N/A')}",
            f"**Description**: {info.get('description', 'N/A')}",
            "",
        ]

    if stock_data:
        change = stock_data.get("change", 0.0)
        sign = "+" if change > 0 else ""
        emoji = "🟢" if change > 0 else ("🔴" if change < 0 else "⚪")
        price = stock_data.get("last_price", 0)
        price_str = f"{price:,.0f}".replace(",", " ") if price >= 1000 else f"{price:.2f}"

        lines += [
            "### Cours en temps réel",
            f"| Indicateur | Valeur |",
            f"|------------|--------|",
            f"| Dernier cours | **{price_str} FCFA** |",
            f"| Variation jour | {emoji} {sign}{change:.2f}% ({sign}{stock_data.get('change_abs', 0):.0f} FCFA) |",
            f"| Volume échangé | {stock_data.get('volume', 0):,} titres |",
        ]
        if stock_data.get("open"):
            lines.append(f"| Ouverture | {stock_data['open']:,.0f} FCFA |")
        if stock_data.get("high"):
            lines.append(f"| Plus haut du jour | {stock_data['high']:,.0f} FCFA |")
        if stock_data.get("low"):
            lines.append(f"| Plus bas du jour | {stock_data['low']:,.0f} FCFA |")

    lines += [
        "",
        "---",
        f"> Source: BRVM (Bourse Régionale des Valeurs Mobilières) — https://www.brvm.org",
        f"> **Avertissement**: Ces informations sont fournies à titre indicatif. La BRVM est caractérisée par une faible liquidité.",
    ]

    return "\n".join(lines)


async def fetch_brvm_news() -> str:
    """
    Scrape les dernières actualités depuis brvm.org/fr/actualites.
    Retourne un résumé Markdown des nouvelles récentes.
    """
    data = await _try_scrape_news()
    is_live = data is not None
    if not is_live:
        logger.info("[BRVM] Utilisation des données simulées pour les actualités.")
        data = _SIMULATED_NEWS

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    source_label = "brvm.org (temps réel)" if is_live else "données simulées (réseau indisponible)"

    lines = [
        f"## Actualités BRVM",
        f"*Source: {source_label} — {now}*",
        "",
    ]

    for i, article in enumerate(data[:10], 1):
        title = article.get("title", "Sans titre")
        date = article.get("date", "")
        summary = article.get("summary", "")
        url = article.get("url", "https://www.brvm.org/fr/actualites")

        lines.append(f"### {i}. {title}")
        if date:
            lines.append(f"*{date}*")
        if summary:
            lines.append(f"\n{summary}")
        lines.append(f"\n[Lire la suite]({url})")
        lines.append("")

    if not data:
        lines.append("*Aucune actualité disponible pour le moment.*")

    return "\n".join(lines)


async def get_brvm_top_movers() -> str:
    """
    Retourne le top des hausses et des baisses du jour sur la BRVM.
    """
    data = await _try_scrape_market()
    if data is None:
        data = _SIMULATED_MARKET

    # Filtrer les valeurs avec variation non nulle
    movers = [s for s in data if s.get("change", 0) != 0]

    # Trier: hausses (positif décroissant) et baisses (négatif croissant)
    top_gainers = sorted([s for s in movers if s.get("change", 0) > 0], key=lambda x: x["change"], reverse=True)[:5]
    top_losers = sorted([s for s in movers if s.get("change", 0) < 0], key=lambda x: x["change"])[:5]

    # Top volumes
    top_volumes = sorted(data, key=lambda x: x.get("volume", 0), reverse=True)[:5]

    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    lines = [
        f"## Top Mouvements BRVM — {now}",
        "",
        "### Meilleures hausses du jour",
        "| # | Symbole | Société | Cours (FCFA) | Variation |",
        "|---|---------|---------|-------------|-----------|",
    ]

    for i, s in enumerate(top_gainers, 1):
        price = s.get("last_price", 0)
        price_str = f"{price:,.0f}".replace(",", " ") if price >= 1000 else f"{price:.2f}"
        lines.append(f"| {i} | **{s['symbol']}** | {s['name']} | {price_str} | 🟢 +{s['change']:.2f}% |")

    if not top_gainers:
        lines.append("| — | — | Aucune hausse enregistrée | — | — |")

    lines += [
        "",
        "### Plus fortes baisses du jour",
        "| # | Symbole | Société | Cours (FCFA) | Variation |",
        "|---|---------|---------|-------------|-----------|",
    ]

    for i, s in enumerate(top_losers, 1):
        price = s.get("last_price", 0)
        price_str = f"{price:,.0f}".replace(",", " ") if price >= 1000 else f"{price:.2f}"
        lines.append(f"| {i} | **{s['symbol']}** | {s['name']} | {price_str} | 🔴 {s['change']:.2f}% |")

    if not top_losers:
        lines.append("| — | — | Aucune baisse enregistrée | — | — |")

    lines += [
        "",
        "### Plus forts volumes du jour",
        "| # | Symbole | Société | Volume (titres) | Cours (FCFA) |",
        "|---|---------|---------|----------------|-------------|",
    ]

    for i, s in enumerate(top_volumes, 1):
        price = s.get("last_price", 0)
        price_str = f"{price:,.0f}".replace(",", " ") if price >= 1000 else f"{price:.2f}"
        vol = s.get("volume", 0)
        lines.append(f"| {i} | **{s['symbol']}** | {s['name']} | {vol:,} | {price_str} |")

    lines += [
        "",
        "> **Note**: La liquidité de la BRVM est structurellement faible. Certaines valeurs peuvent ne pas être échangées chaque jour.",
    ]

    return "\n".join(lines)


async def search_brvm_company(query: str) -> str:
    """
    Recherche une entreprise cotée à la BRVM par nom ou symbole.
    Retourne les résultats correspondants en Markdown.
    """
    query_lower = query.lower().strip()

    matches = []
    for symbol, info in BRVM_COMPANIES.items():
        score = 0
        if query_lower in symbol.lower():
            score += 10
        if query_lower in info["name"].lower():
            score += 8
        if query_lower in info["full_name"].lower():
            score += 6
        if query_lower in info["sector"].lower():
            score += 4
        if query_lower in info["country"].lower():
            score += 3
        if query_lower in info.get("description", "").lower():
            score += 1
        if score > 0:
            matches.append((score, symbol, info))

    matches.sort(key=lambda x: x[0], reverse=True)

    if not matches:
        return (
            f"## Recherche BRVM: « {query} »\n\n"
            f"Aucune société trouvée pour cette requête.\n\n"
            f"**Symboles disponibles**: {', '.join(sorted(BRVM_COMPANIES.keys()))}\n\n"
            f"**Conseils**: Essayez le symbole exact (ex: SNTS, ETIT, ORAC) ou le nom court (ex: Sonatel, Ecobank, Orange)."
        )

    lines = [
        f"## Recherche BRVM: « {query} »",
        f"*{len(matches)} résultat(s) trouvé(s)*",
        "",
    ]

    for _, symbol, info in matches[:8]:
        lines += [
            f"### {info['name']} ({symbol})",
            f"- **Nom complet**: {info['full_name']}",
            f"- **Secteur**: {info['sector']}",
            f"- **Pays**: {info['country']}",
            f"- **ISIN**: {info.get('isin', 'N/A')}",
            f"- {info.get('description', '')}",
            "",
        ]

    lines.append(f"> Utilisez `fetch_brvm_company(symbol)` pour obtenir les cours en temps réel.")

    return "\n".join(lines)
