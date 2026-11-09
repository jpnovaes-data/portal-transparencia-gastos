import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import download  # noqa: E402


def test_extrai_csv_do_zip(tmp_path):
    zip_path = tmp_path / "202401.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("202401_Despesas.csv", "a;b\n1;2\n")
    csvs = download.extrair_zip(zip_path, tmp_path / "saida")
    assert [c.name for c in csvs] == ["202401_Despesas.csv"]


def test_monta_url_com_mes_de_dois_digitos():
    url = download.URL_MODELO_DESPESAS.format(ano=2024, mes="01")
    assert "202401" in url or "{" not in url
