"""Leitura e tipagem do CSV de despesas. Códigos ficam como texto; valores viram float."""
from pathlib import Path

import pandas as pd

from config import DECIMAL_CSV, ENCODING_CSV, SEPARADOR_CSV

COLUNA_PERIODO = "Ano e mês do lançamento"

COLUNAS_CODIGO = [
    "Código Órgão Superior",
    "Código Órgão Subordinado",
    "Código Unidade Gestora",
    "Código Gestão",
    "Código Função",
    "Código Subfução",
    "Código Programa Orçamentário",
    "Código Ação",
    "Código Categoria Econômica",
    "Código Grupo de Despesa",
    "Código Elemento de Despesa",
    "Código Modalidade da Despesa",
]

COLUNAS_VALOR = [
    "Valor Empenhado (R$)",
    "Valor Liquidado (R$)",
    "Valor Pago (R$)",
    "Valor Restos a Pagar Inscritos (R$)",
    "Valor Restos a Pagar Cancelado (R$)",
    "Valor Restos a Pagar Pagos (R$)",
]


def converter_valor(serie: pd.Series) -> pd.Series:
    """Converte '1.234,56' em 1234.56. Valores vazios viram 0."""
    limpo = serie.fillna("").str.strip().replace("", "0")
    limpo = limpo.str.replace(".", "", regex=False).str.replace(DECIMAL_CSV, ".", regex=False)
    return pd.to_numeric(limpo, errors="raise")


def ler_csv(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(
        caminho,
        sep=SEPARADOR_CSV,
        encoding=ENCODING_CSV,
        dtype=str,
        keep_default_na=False,
    )
    df.columns = [c.strip() for c in df.columns]
    for coluna in COLUNAS_VALOR:
        if coluna in df.columns:
            df[coluna] = converter_valor(df[coluna])
    if COLUNA_PERIODO in df.columns:
        periodo = df[COLUNA_PERIODO].str.split("/", expand=True)
        df["ano"] = periodo[0].astype(int)
        df["mes"] = periodo[1].astype(int)
    return df
