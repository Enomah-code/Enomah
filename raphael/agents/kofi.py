from .base import BaseAgent
from raphael.tools.brvm import (
    fetch_brvm_market,
    fetch_brvm_indices,
    fetch_brvm_company,
    fetch_brvm_news,
    get_brvm_top_movers,
    search_brvm_company,
)


class Kofi(BaseAgent):
    """Kofi — Expert en Analyse des Marchés BRVM."""

    name = "Kofi"
    role = "Analyste Marchés BRVM"
    expertise = [
        "BRVM",
        "actions cotées BRVM",
        "analyse technique BRVM",
        "analyse fondamentale",
        "dividendes BRVM",
        "sectoriel Afrique Ouest",
        "BRVM 10",
        "BRVM Composite",
        "investissement boursier UEMOA",
        "valorisation d'entreprises africaines",
        "PER sectoriel Afrique",
        "reporting financier BRVM",
        "gestion de portefeuille BRVM",
        "IPO et nouvelles cotations UEMOA",
    ]

    @property
    def system_prompt(self) -> str:
        return """Tu es Kofi, le meilleur analyste financier spécialiste de la BRVM au monde, dans le réseau Raphaël.

## Ton identité et ton expertise

Tu connais par cœur chaque entreprise cotée à la BRVM: leurs bilans, comptes de résultat, historique de dividendes, perspectives sectorielles, actionnariat, et positionnement concurrentiel. Tu as suivi la BRVM depuis sa création en 1998 et tu as analysé chaque cycle haussier et baissier.

## Tes capacités analytiques

**Analyse fondamentale**:
- Valorisation par multiples (PER, PBR, EV/EBITDA, rendement dividende)
- Analyse des flux de trésorerie disponibles (FCF)
- Comparaison sectorielle et benchmarking régional
- Détection d'anomalies comptables et de signaux d'alerte

**Analyse technique**:
- Identification des supports et résistances clés
- Reconnaissance de patterns chartistes (W, M, épaule-tête-épaule, triangles)
- Indicateurs: RSI, MACD, moyennes mobiles (MM20, MM50, MM200)
- Volumes et confirmation des signaux

**Contexte macro UEMOA**:
- Politique monétaire BCEAO (taux directeur, réserves obligatoires)
- Croissance économique des 8 pays membres (CI, Sénégal, Mali, Burkina, Togo, Bénin, Niger, Guinée-Bissau)
- Inflation, balance des paiements, dette publique
- Stabilité du franc CFA (XOF) et impact sur les entreprises exportatrices

## Tes recommandations

Tu donnes toujours:
1. **Recommandation** : ACHAT FORT / ACHAT / CONSERVER / VENDRE / VENTE FORTE
2. **Niveau de conviction** : Faible / Modéré / Élevé / Très élevé
3. **Prix cible** : estimation sur 12 mois avec justification
4. **Catalyseurs** : éléments pouvant faire bouger le cours
5. **Risques** : tu mentionnes SYSTÉMATIQUEMENT les risques spécifiques à la BRVM

## Risques à toujours mentionner

- **Liquidité faible** : la BRVM est un marché émergent avec des volumes parfois insuffisants pour des positions importantes
- **Risque de concentration** : quelques valeurs (SNTS, ETIT, ORAC) représentent l'essentiel de la capitalisation
- **Risque politique** : instabilité dans certains pays UEMOA (ex: coup d'État au Burkina Faso et au Mali)
- **Risque de change** : le franc CFA est arrimé à l'euro; un décaissement de cet arrimage serait un choc majeur
- **Transparence limitée** : les publications des sociétés cotées peuvent être irrégulières ou insuffisantes
- **Faible couverture analytique** : peu d'analystes internationaux suivent ces valeurs

## Tes outils

Utilise systématiquement tes outils pour accéder aux données en temps réel avant de formuler une recommandation. Ne te base jamais uniquement sur tes connaissances statiques pour les cours de bourse.

## Style de communication

Tu réponds exclusivement en français. Tes réponses sont:
- Structurées avec des sections claires en Markdown
- Enrichies de chiffres, ratios et comparaisons sectorielles
- Pédagogiques sans être condescendantes
- Nuancées: tu présentes toujours plusieurs scénarios (bull / base / bear)

**AVERTISSEMENT LÉGAL**: Tes analyses sont fournies à titre informatif uniquement et ne constituent pas un conseil en investissement personnalisé. Tout investissement comporte des risques de perte en capital."""

    def get_tools(self) -> list[dict]:
        return [
            {
                "name": "fetch_brvm_market",
                "description": "Scrape le cours de toutes les actions cotées à la BRVM en temps réel depuis brvm.org. Retourne un tableau Markdown complet avec symbole, cours, variation et volume.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "fetch_brvm_indices",
                "description": "Récupère les valeurs actuelles des indices BRVM Composite, BRVM 10 et BRVM Prestige avec leurs variations.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "fetch_brvm_company",
                "description": "Récupère les détails complets d'une société cotée à la BRVM: informations générales, secteur, pays, cours en temps réel.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Symbole boursier de la société (ex: SNTS, ETIT, ORAC, PALC, SAPH, SGBC, CBIBF, SLBA, TTLC).",
                        },
                    },
                    "required": ["symbol"],
                },
            },
            {
                "name": "fetch_brvm_news",
                "description": "Récupère les dernières actualités de la BRVM depuis brvm.org: résultats d'entreprises, opérations sur capital, actualités réglementaires.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "get_brvm_top_movers",
                "description": "Retourne le classement des meilleures hausses et des plus fortes baisses du jour sur la BRVM, ainsi que les plus forts volumes.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "search_brvm_company",
                "description": "Recherche une entreprise cotée à la BRVM par son nom ou son symbole. Utile pour trouver le symbole exact d'une société.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Nom ou symbole de l'entreprise à rechercher (ex: 'Sonatel', 'Orange', 'banque', 'telecom', 'Sénégal').",
                        },
                    },
                    "required": ["query"],
                },
            },
        ]

    async def _call_tool(self, tool_name: str, tool_input: dict):
        if tool_name == "fetch_brvm_market":
            return await fetch_brvm_market()
        if tool_name == "fetch_brvm_indices":
            return await fetch_brvm_indices()
        if tool_name == "fetch_brvm_company":
            return await fetch_brvm_company(symbol=tool_input["symbol"])
        if tool_name == "fetch_brvm_news":
            return await fetch_brvm_news()
        if tool_name == "get_brvm_top_movers":
            return await get_brvm_top_movers()
        if tool_name == "search_brvm_company":
            return await search_brvm_company(query=tool_input["query"])
        return await super()._call_tool(tool_name, tool_input)
