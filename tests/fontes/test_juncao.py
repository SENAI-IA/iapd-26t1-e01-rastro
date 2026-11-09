from dataclasses import replace

from rastro.fontes.conector import Aviso, marcar_origem
from rastro.fontes.juncao import juntar_avisos
from rastro.fontes.nvd import completar_cvss
from tests.dubles import NvdFalso, avisos_gravados_do_jquery, avisos_gravados_do_jquery_no_osv

GHSA_DO_CVE_11022 = "GHSA-gxr4-xjj5-5px2"
GHSA_DO_CVE_11023 = "GHSA-jpcq-cgw6-v4j6"


def aviso_do_github(ghsa: str) -> Aviso:
    return next(aviso for aviso in avisos_gravados_do_jquery() if aviso.ghsa == ghsa)


def aviso_do_osv(ghsa: str) -> Aviso:
    return next(aviso for aviso in avisos_gravados_do_jquery_no_osv() if aviso.ghsa == ghsa)


def aviso_so_do_osv() -> Aviso:
    aviso = Aviso(
        fontes=["OSV"],
        apelidos=[],
        ghsa="MAL-2099-0001",
        cve=None,
        resumo="Código malicioso publicado no pacote",
        cvss=None,
        percentil_epss=None,
        versoes_afetadas=">= 0",
        versao_corrigida=None,
        link="https://osv.dev/vulnerability/MAL-2099-0001",
    )
    return marcar_origem(aviso, "OSV")


def juntar_github_e_osv() -> list[Aviso]:
    return juntar_avisos(avisos_gravados_do_jquery() + avisos_gravados_do_jquery_no_osv())


def test_r04a_3_mesmo_aviso_no_github_e_no_osv_aparece_uma_vez_com_as_duas_fontes() -> None:
    juntos = juntar_avisos([aviso_do_github(GHSA_DO_CVE_11022), aviso_do_osv(GHSA_DO_CVE_11022)])

    assert len(juntos) == 1
    assert juntos[0].ghsa == GHSA_DO_CVE_11022
    assert juntos[0].fontes == ["GitHub Advisory", "OSV"]
    assert juntos[0].apelidos == ["CVE-2020-11022", "BIT-drupal-2020-11022"]


def test_r04a_3_resposta_gravada_das_duas_fontes_mantem_um_aviso_por_faixa_do_github() -> None:
    juntos = juntar_github_e_osv()

    assert [(aviso.ghsa, aviso.versoes_afetadas) for aviso in juntos] == [
        (GHSA_DO_CVE_11022, ">= 1.2, < 3.5.0"),
        (GHSA_DO_CVE_11023, ">= 1.0.3, < 3.5.0"),
        (GHSA_DO_CVE_11023, "< 1.0.3"),
    ]
    assert all(aviso.fontes == ["GitHub Advisory", "OSV"] for aviso in juntos)


def test_r04a_3_junta_pelo_apelido_quando_o_id_e_diferente() -> None:
    do_osv = replace(
        aviso_do_osv(GHSA_DO_CVE_11022), ghsa="BIT-drupal-2020-11022", apelidos=["CVE-2020-11022"]
    )

    juntos = juntar_avisos([aviso_do_github(GHSA_DO_CVE_11022), do_osv])

    assert len(juntos) == 1
    assert juntos[0].ghsa == GHSA_DO_CVE_11022
    assert juntos[0].apelidos == ["CVE-2020-11022", "BIT-drupal-2020-11022"]


def test_r04a_3_aviso_so_do_osv_entra_como_veio() -> None:
    so_do_osv = aviso_so_do_osv()

    juntos = juntar_avisos([aviso_do_github(GHSA_DO_CVE_11022), so_do_osv])

    assert juntos == [aviso_do_github(GHSA_DO_CVE_11022), so_do_osv]


def test_r04a_3_avisos_de_uma_fonte_so_nao_mudam() -> None:
    avisos = avisos_gravados_do_jquery()

    assert juntar_avisos(avisos) == avisos


def test_r04a_4_faixa_versao_corrigida_e_link_seguem_o_github_mesmo_se_o_osv_vem_antes() -> None:
    juntos = juntar_avisos([aviso_do_osv(GHSA_DO_CVE_11022), aviso_do_github(GHSA_DO_CVE_11022)])

    assert juntos[0].versoes_afetadas == ">= 1.2, < 3.5.0"
    assert juntos[0].versao_corrigida == "3.5.0"
    assert juntos[0].link == "https://github.com/advisories/GHSA-gxr4-xjj5-5px2"
    assert juntos[0].fontes == ["GitHub Advisory", "OSV"]


def test_r04a_4_resumo_e_cve_seguem_o_github() -> None:
    do_osv = replace(aviso_do_osv(GHSA_DO_CVE_11022), resumo="Resumo diferente no OSV")

    juntos = juntar_avisos([aviso_do_github(GHSA_DO_CVE_11022), do_osv])

    assert juntos[0].resumo == "Potential XSS vulnerability in jQuery"
    assert juntos[0].cve == "CVE-2020-11022"


def test_r04a_4_campo_vazio_no_github_vem_da_proxima_fonte() -> None:
    sem_cve = marcar_origem(
        replace(aviso_do_github(GHSA_DO_CVE_11022), cve=None, apelidos=[]), "GitHub Advisory"
    )

    juntos = juntar_avisos([sem_cve, aviso_do_osv(GHSA_DO_CVE_11022)])

    assert juntos[0].cve == "CVE-2020-11022"
    assert juntos[0].origem_dos_campos["cve"] == "OSV"


def test_r04a_4_cvss_e_epss_vem_so_do_github() -> None:
    juntos = juntar_github_e_osv()

    assert juntos[0].cvss == 6.9
    assert juntos[0].percentil_epss == 0.95


def test_r04a_4_sem_cvss_no_github_o_do_nvd_completa_o_aviso_junto() -> None:
    sem_cvss = marcar_origem(
        replace(aviso_do_github(GHSA_DO_CVE_11022), cvss=None), "GitHub Advisory"
    )
    juntos = juntar_avisos([sem_cvss, aviso_do_osv(GHSA_DO_CVE_11022)])

    completado = completar_cvss(juntos, NvdFalso({"CVE-2020-11022": 6.1}))

    assert completado.avisos[0].cvss == 6.1
    assert completado.avisos[0].fontes == ["GitHub Advisory", "OSV", "NVD"]
    assert completado.avisos[0].origem_dos_campos["cvss"] == "NVD"


def test_r04a_5_origem_mostra_a_fonte_de_cada_campo() -> None:
    juntos = juntar_avisos([aviso_do_osv(GHSA_DO_CVE_11022), aviso_do_github(GHSA_DO_CVE_11022)])

    assert juntos[0].origem_dos_campos == {
        "cve": "GitHub Advisory",
        "resumo": "GitHub Advisory",
        "cvss": "GitHub Advisory",
        "percentil_epss": "GitHub Advisory",
        "versoes_afetadas": "GitHub Advisory",
        "versao_corrigida": "GitHub Advisory",
        "link": "GitHub Advisory",
    }


def test_r04a_5_aviso_so_do_osv_tem_a_origem_do_osv_e_sem_cvss_nem_epss() -> None:
    juntos = juntar_avisos([aviso_so_do_osv()])

    assert juntos[0].origem_dos_campos == {
        "resumo": "OSV",
        "versoes_afetadas": "OSV",
        "link": "OSV",
    }
