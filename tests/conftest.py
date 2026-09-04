import sys
from pathlib import Path

# Adiciona a raiz do projeto ao PYTHONPATH para execução determinística
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
