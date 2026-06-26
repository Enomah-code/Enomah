"""Boîte à outils partagée par les agents (lecture fichiers, web, analyse)."""
from .analysis_tools import analyze_tabular, describe_dataframe
from .file_reader import read_upload
from .web_tools import fetch_url, web_search

# Registre nom -> callable, consommé par les agents et le recruteur.
TOOL_REGISTRY = {
    "read_upload": read_upload,
    "web_search": web_search,
    "fetch_url": fetch_url,
    "analyze_tabular": analyze_tabular,
    "describe_dataframe": describe_dataframe,
}

__all__ = [
    "TOOL_REGISTRY",
    "read_upload",
    "web_search",
    "fetch_url",
    "analyze_tabular",
    "describe_dataframe",
]
