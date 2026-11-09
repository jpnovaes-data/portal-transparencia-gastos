"""Configuração central do projeto."""
from pathlib import Path

# Arquivo mensal de execução da despesa (Portal da Transparência, dados abertos).
# Padrão confirmado: .../despesas-execucao/AAAAMM_Despesas.zip
URL_MODELO_DESPESAS = (
    "https://dadosabertos-download.cgu.gov.br/PortalDaTransparencia/saida/"
    "despesas-execucao/{ano}{mes}_Despesas.zip"
)

RAIZ_DADOS = Path("data")
PASTA_RAW = RAIZ_DADOS / "raw"
PASTA_PROCESSED = RAIZ_DADOS / "processed"

ENCODING_CSV = "latin-1"
SEPARADOR_CSV = ";"
DECIMAL_CSV = ","

TIMEOUT_SEGUNDOS = 120
MAX_TENTATIVAS = 4
ESPERAS_RETENTATIVA = (5, 10, 20)