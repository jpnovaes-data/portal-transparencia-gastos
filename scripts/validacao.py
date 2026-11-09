"""Checagens antes de carregar.

problemas: bloqueiam a carga. avisos: são registrados, mas não bloqueiam.
"""
import pandas as pd

from tratamento import COLUNA_PERIODO, COLUNAS_VALOR

COLUNAS_OBRIGATORIAS = [COLUNA_PERIODO, "Código Órgão Superior", "Código Unidade Gestora", *COLUNAS_VALOR]


def validar(df: pd.DataFrame) -> list[str]:
    """Retorna os problemas que bloqueiam a carga (lista vazia quando está ok)."""
    problemas = []
    if df.empty:
        problemas.append("arquivo sem linhas")
        return problemas
    faltando = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltando:
        problemas.append(f"colunas ausentes: {faltando}")
        return problemas
    if df[COLUNAS_OBRIGATORIAS].isna().any().any():
        problemas.append("valores nulos em colunas obrigatórias")
    periodos = df[COLUNA_PERIODO].unique()
    if len(periodos) != 1:
        problemas.append(f"mais de um período no mesmo arquivo: {list(periodos)[:5]}")
    return problemas


def avisos(df: pd.DataFrame) -> list[str]:
    """Retorna avisos que não bloqueiam a carga."""
    lista = []
    negativos = df[df["Valor Pago (R$)"] < 0]
    if not negativos.empty:
        lista.append(
            f"{len(negativos)} registro(s) com valor pago negativo "
            f"(soma {negativos['Valor Pago (R$)'].sum():,.2f}), provavelmente estornos"
        )
    return lista