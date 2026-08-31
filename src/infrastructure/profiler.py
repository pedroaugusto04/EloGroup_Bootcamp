"""
src/infrastructure/profiler.py
Gera relatórios de profiling em HTML para os 5 datasets originais da pasta data/raw
usando ydata-profiling, facilitando a identificação de nulos, outliers, tipos de dados e correlações.
"""

import sys
from pathlib import Path
import pandas as pd

# Adiciona o diretório raiz ao path se necessário
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.config import RAW_DATA_DIR, RAW_FILES

# Diretório de destino para os relatórios
PROFILING_DIR = ROOT_DIR / "docs" / "profiling"


def run_profiling():
    try:
        from ydata_profiling import ProfileReport
    except ImportError:
        print("Erro: 'ydata-profiling' não está instalado no ambiente virtual.")
        print("Instale executando: pip install ydata-profiling")
        sys.exit(1)

    print(f"Diretório de saída: {PROFILING_DIR}")
    PROFILING_DIR.mkdir(parents=True, exist_ok=True)

    for key, filename in RAW_FILES.items():
        csv_path = RAW_DATA_DIR / filename
        if not csv_path.exists():
            # Tenta buscar diretamente do diretório raiz se necessário
            csv_path = ROOT_DIR / filename

        if not csv_path.exists():
            print(f"[-] Arquivo não encontrado: {filename}. Pulando...")
            continue

        print(f"\n[+] Carregando {key} ({filename})...")
        df = pd.read_csv(csv_path)
        
        output_file = PROFILING_DIR / f"{key}_report.html"
        print(f"[+] Gerando profiling para {key} (isso pode levar alguns instantes)...")
        
        # Gerando o relatório com o modo explorativo habilitado
        profile = ProfileReport(
            df, 
            title=f"Profiling Report - {key.capitalize()}", 
            explorative=True,
            minimal=False # Altere para True se ficar muito lento em arquivos muito grandes
        )
        
        profile.to_file(output_file)
        print(f"[✔] Relatório salvo com sucesso: {output_file}")


if __name__ == "__main__":
    run_profiling()
