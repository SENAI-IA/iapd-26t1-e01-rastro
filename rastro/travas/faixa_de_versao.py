from rastro.fontes.conector import Aviso
from rastro.fontes.consulta import AvisosDaBiblioteca
from rastro.travas.modelos import TravaAcionada
from rastro.versao_semver import FaixaIlegivel, versao_na_faixa

NOME_DA_TRAVA = "faixa conferida"


def conferir_faixas(
    avisos: list[AvisosDaBiblioteca],
) -> tuple[list[AvisosDaBiblioteca], list[TravaAcionada]]:
    mantidos: list[AvisosDaBiblioteca] = []
    travas_acionadas: list[TravaAcionada] = []
    for biblioteca, avisos_da_biblioteca in avisos:
        na_faixa, barrados = descartar_fora_da_faixa(
            biblioteca.pacote, biblioteca.versao, avisos_da_biblioteca
        )
        mantidos.append((biblioteca, na_faixa))
        travas_acionadas.extend(barrados)
    return mantidos, travas_acionadas


def descartar_fora_da_faixa(
    pacote: str, versao: str, avisos: list[Aviso]
) -> tuple[list[Aviso], list[TravaAcionada]]:
    mantidos = []
    motivos_por_aviso: dict[str, list[str]] = {}
    for aviso in avisos:
        motivo = motivo_para_descartar(versao, aviso.versoes_afetadas)
        if motivo is None:
            mantidos.append(aviso)
        else:
            motivos_por_aviso.setdefault(aviso.ghsa, []).append(motivo)
    avisos_mantidos = {aviso.ghsa for aviso in mantidos}
    travas_acionadas = [
        TravaAcionada(NOME_DA_TRAVA, f"{ghsa} em {pacote}@{versao}", "; ".join(motivos))
        for ghsa, motivos in motivos_por_aviso.items()
        if ghsa not in avisos_mantidos
    ]
    return mantidos, travas_acionadas


def motivo_para_descartar(versao: str, faixa: str) -> str | None:
    try:
        if versao_na_faixa(versao, faixa):
            return None
    except FaixaIlegivel as erro:
        return f"não foi possível conferir a faixa `{faixa}`: {erro}"
    return f"a versão {versao} está fora da faixa afetada `{faixa}`"
