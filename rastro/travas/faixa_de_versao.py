from rastro.fontes.modelos import Aviso, AvisosDaBiblioteca
from rastro.travas.modelos import TravaAcionada
from rastro.versao_semver import FaixaIlegivel, versao_na_faixa

NOME_DA_TRAVA = "faixa conferida"


def conferir_faixas(
    avisos: list[AvisosDaBiblioteca],
) -> tuple[list[AvisosDaBiblioteca], list[TravaAcionada]]:
    mantidos: list[AvisosDaBiblioteca] = []
    travas_acionadas: list[TravaAcionada] = []
    for avisos_da_biblioteca in avisos:
        biblioteca = avisos_da_biblioteca.biblioteca
        na_faixa, travas_da_faixa = descartar_fora_da_faixa(
            biblioteca.pacote, biblioteca.versao, avisos_da_biblioteca.avisos
        )
        mantidos.append(AvisosDaBiblioteca(biblioteca, na_faixa))
        travas_acionadas.extend(travas_da_faixa)
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
    travas_acionadas = travas_dos_avisos_descartados(pacote, versao, mantidos, motivos_por_aviso)
    return mantidos, travas_acionadas


def travas_dos_avisos_descartados(
    pacote: str, versao: str, mantidos: list[Aviso], motivos_por_aviso: dict[str, list[str]]
) -> list[TravaAcionada]:
    avisos_mantidos = {aviso.ghsa for aviso in mantidos}
    travas_acionadas = []
    for ghsa, motivos in motivos_por_aviso.items():
        if ghsa not in avisos_mantidos:
            alvo = f"{ghsa} em {pacote}@{versao}"
            travas_acionadas.append(TravaAcionada(NOME_DA_TRAVA, alvo, "; ".join(motivos)))
    return travas_acionadas


def motivo_para_descartar(versao: str, faixa: str) -> str | None:
    try:
        if versao_na_faixa(versao, faixa):
            return None
    except FaixaIlegivel as erro:
        return f"não foi possível conferir a faixa `{faixa}`: {erro}"
    return f"a versão {versao} está fora da faixa afetada `{faixa}`"
