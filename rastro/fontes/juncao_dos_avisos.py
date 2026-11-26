from collections.abc import Iterable
from dataclasses import replace

from rastro.fontes.conector import Aviso

ORDEM_DAS_FONTES = ("GitHub Advisory", "OSV", "NVD")
CAMPOS_PELA_ORDEM_DAS_FONTES = ("cve", "resumo", "cvss", "percentil_epss")
CAMPOS_DA_FAIXA = ("versoes_afetadas", "versao_corrigida", "link")


def juntar_avisos(avisos: list[Aviso]) -> list[Aviso]:
    juntos = []
    for grupo in agrupar_avisos_iguais(avisos):
        juntos.extend(juntar_grupo(grupo))
    return juntos


def agrupar_avisos_iguais(avisos: list[Aviso]) -> list[list[Aviso]]:
    grupos: list[list[Aviso]] = []
    for aviso in avisos:
        grupo = grupo_do_aviso(aviso, grupos)
        if grupo is None:
            grupos.append([aviso])
        else:
            grupo.append(aviso)
    return grupos


def grupo_do_aviso(aviso: Aviso, grupos: list[list[Aviso]]) -> list[Aviso] | None:
    for grupo in grupos:
        if any(identificadores(aviso) & identificadores(outro) for outro in grupo):
            return grupo
    return None


def identificadores(aviso: Aviso) -> set[str]:
    return {aviso.ghsa, *aviso.apelidos}


def juntar_grupo(grupo: list[Aviso]) -> list[Aviso]:
    na_ordem = sorted(grupo, key=posicao_da_fonte)
    fonte_principal = na_ordem[0].fontes[0]
    faixas_da_fonte_principal = [aviso for aviso in na_ordem if aviso.fontes[0] == fonte_principal]
    return [completar_com_o_grupo(aviso, na_ordem) for aviso in faixas_da_fonte_principal]


def posicao_da_fonte(aviso: Aviso) -> int:
    return ORDEM_DAS_FONTES.index(aviso.fontes[0])


def completar_com_o_grupo(aviso_da_faixa: Aviso, na_ordem: list[Aviso]) -> Aviso:
    com_cve = primeiro_com_o_campo("cve", na_ordem)
    com_resumo = primeiro_com_o_campo("resumo", na_ordem) or aviso_da_faixa
    com_cvss = primeiro_com_o_campo("cvss", na_ordem)
    com_epss = primeiro_com_o_campo("percentil_epss", na_ordem)
    return replace(
        aviso_da_faixa,
        fontes=sem_repeticao(fonte for aviso in na_ordem for fonte in aviso.fontes),
        apelidos=apelidos_do_grupo(aviso_da_faixa.ghsa, na_ordem),
        cve=com_cve.cve if com_cve is not None else None,
        resumo=com_resumo.resumo,
        cvss=com_cvss.cvss if com_cvss is not None else None,
        percentil_epss=com_epss.percentil_epss if com_epss is not None else None,
        origem_dos_campos=origem_no_grupo(aviso_da_faixa, na_ordem),
    )


def origem_no_grupo(aviso_da_faixa: Aviso, na_ordem: list[Aviso]) -> dict[str, str]:
    origem = {}
    for campo in CAMPOS_PELA_ORDEM_DAS_FONTES:
        quem_traz = primeiro_com_o_campo(campo, na_ordem)
        if quem_traz is not None:
            origem[campo] = quem_traz.origem_dos_campos[campo]
    for campo in CAMPOS_DA_FAIXA:
        if campo in aviso_da_faixa.origem_dos_campos:
            origem[campo] = aviso_da_faixa.origem_dos_campos[campo]
    return origem


def primeiro_com_o_campo(campo: str, na_ordem: list[Aviso]) -> Aviso | None:
    for aviso in na_ordem:
        if campo in aviso.origem_dos_campos:
            return aviso
    return None


def apelidos_do_grupo(ghsa: str, na_ordem: list[Aviso]) -> list[str]:
    todos = sem_repeticao(
        identificador for aviso in na_ordem for identificador in [aviso.ghsa, *aviso.apelidos]
    )
    return [identificador for identificador in todos if identificador != ghsa]


def sem_repeticao(itens: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(itens))
