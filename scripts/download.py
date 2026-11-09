"""Download e descompactação do arquivo mensal, com retentativas."""
import logging
import time
import zipfile
from pathlib import Path

import requests

from config import ESPERAS_RETENTATIVA, MAX_TENTATIVAS, PASTA_RAW, TIMEOUT_SEGUNDOS, URL_MODELO_DESPESAS

log = logging.getLogger("download")


def montar_url(ano: int, mes: int) -> str:
    return URL_MODELO_DESPESAS.format(ano=ano, mes=f"{mes:02d}")


def baixar_zip(url: str, destino: Path, espera=time.sleep, sessao=None) -> Path:
    """Baixa o ZIP em streaming para não carregar o arquivo inteiro na memória."""
    sessao = sessao or requests.Session()
    destino.parent.mkdir(parents=True, exist_ok=True)
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            with sessao.get(url, stream=True, timeout=TIMEOUT_SEGUNDOS) as resp:
                resp.raise_for_status()
                with open(destino, "wb") as arq:
                    for bloco in resp.iter_content(chunk_size=1024 * 1024):
                        arq.write(bloco)
            return destino
        except requests.RequestException as erro:
            log.warning("tentativa %s de %s falhou: %s", tentativa, url, erro)
            if tentativa == MAX_TENTATIVAS:
                raise
            espera(ESPERAS_RETENTATIVA[min(tentativa - 1, len(ESPERAS_RETENTATIVA) - 1)])
    raise RuntimeError("inalcançável")


def extrair_zip(zip_path: Path, pasta: Path) -> list[Path]:
    """Extrai o ZIP e retorna os CSVs encontrados."""
    pasta.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(pasta)
    return sorted(pasta.glob("*.csv"))


def pasta_do_mes(ano: int, mes: int) -> Path:
    return PASTA_RAW / f"ano={ano}" / f"mes={mes:02d}"


def ingerir_mes(ano: int, mes: int, espera=time.sleep, sessao=None) -> list[Path]:
    """Baixa, descompacta e devolve os CSVs do mês. Reexecutar sobrescreve o mesmo mês."""
    pasta = pasta_do_mes(ano, mes)
    zip_path = baixar_zip(montar_url(ano, mes), pasta / f"{ano}{mes:02d}.zip", espera=espera, sessao=sessao)
    return extrair_zip(zip_path, pasta)
