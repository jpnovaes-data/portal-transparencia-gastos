import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import pandas as pd  # noqa: E402

from tratamento import COLUNA_PERIODO, ler_csv  # noqa: E402
from validacao import validar  # noqa: E402

CABECALHO = [
    COLUNA_PERIODO, "Código Órgão Superior", "Código Unidade Gestora", "Código Gestão",
    "Valor Empenhado (R$)", "Valor Liquidado (R$)", "Valor Pago (R$)",
    "Valor Restos a Pagar Inscritos (R$)", "Valor Restos a Pagar Cancelado (R$)",
    "Valor Restos a Pagar Pagos (R$)",
]
LINHA = ["2024/01", "00", "155914", "-1", "403260,47", "5976,93", "0", "0", "0", "0"]


def escrever_csv(tmp_path, linhas):
    caminho = tmp_path / "despesas.csv"
    texto = ";".join(CABECALHO) + "\n" + "\n".join(";".join(l) for l in linhas) + "\n"
    caminho.write_bytes(texto.encode("latin-1"))
    return caminho


def test_converte_valor_com_virgula_decimal(tmp_path):
    df = ler_csv(escrever_csv(tmp_path, [LINHA]))
    assert df.loc[0, "Valor Empenhado (R$)"] == 403260.47
    assert df.loc[0, "Valor Liquidado (R$)"] == 5976.93


def test_preserva_codigos_com_zero_e_sinal(tmp_path):
    df = ler_csv(escrever_csv(tmp_path, [LINHA]))
    assert df.loc[0, "Código Órgão Superior"] == "00"
    assert df.loc[0, "Código Gestão"] == "-1"


def test_separa_ano_e_mes(tmp_path):
    df = ler_csv(escrever_csv(tmp_path, [LINHA]))
    assert df.loc[0, "ano"] == 2024
    assert df.loc[0, "mes"] == 1


def test_valida_arquivo_ok(tmp_path):
    df = ler_csv(escrever_csv(tmp_path, [LINHA]))
    assert validar(df) == []


def test_valida_detecta_coluna_ausente(tmp_path):
    df = ler_csv(escrever_csv(tmp_path, [LINHA])).drop(columns=["Valor Pago (R$)"])
    assert any("ausentes" in p for p in validar(df))


def test_valida_detecta_arquivo_vazio(tmp_path):
    df = ler_csv(escrever_csv(tmp_path, [LINHA])).iloc[0:0]
    assert validar(df) == ["arquivo sem linhas"]
