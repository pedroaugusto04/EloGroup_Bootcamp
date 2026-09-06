"""
src/config.py
Configurações centrais do projeto Vértice Analytics (EloGroup Bootcamp).
"""

from pathlib import Path
from dotenv import load_dotenv

# Diretórios base
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
STORAGE_DIR = DATA_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = ROOT_DIR / "relatorios_analise"

# Carrega variáveis de ambiente do arquivo .env se presente
load_dotenv(ROOT_DIR / ".env")

# Banco DuckDB
DB_PATH = DATA_DIR / "vertice_analytics.duckdb"
AUDIT_LOG_PATH = STORAGE_DIR / "audit_log.json"

# Nomes dos arquivos brutos
RAW_FILES = {
    "vendas": "[BootCamp EloGroup 2026] Vendas.csv",
    "marketing": "[BootCamp EloGroup 2026] Marketing.csv",
    "estoque": "[BootCamp EloGroup 2026] Estoque.csv",
    "clientes": "[BootCamp EloGroup 2026] Clientes.csv",
    "atendimento": "[BootCamp EloGroup 2026] Atendimento.csv",
}

# Paleta de Cores EloGroup & Design Tokens (Padrão Corporativo Preto e Branco)
ELOGROUP_THEME = {
    "primary": "#FFFFFF",
    "primary_dark": "#09090B",
    "surface": "#121215",
    "surface_secondary": "#18181B",
    "border": "#27272A",
    "border_light": "#3F3F46",
    "text_main": "#FFFFFF",
    "text_secondary": "#A1A1AA",
    "text_muted": "#71717A",
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "info": "#38BDF8",
    "dark_bg": "#09090B",
}
