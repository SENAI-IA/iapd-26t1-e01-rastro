from rastro.fontes.completar_cvss import BuscaDeCvss, completar_cvss
from rastro.fontes.modelos import Aviso
from tests.dubles import NvdFalso


def aviso(ghsa: str, cve: str | None, cvss: float | None, fontes: list[str] | None = None) -> Aviso:
    return Aviso(
        fontes=fontes or ["GitHub Advisory"],
        apelidos=[cve] if cve else [],
        ghsa=ghsa,
        cve=cve,
        resumo="Aviso de exemplo",
        cvss=cvss,
        percentil_epss=None,
        versoes_afetadas="< 3.5.0",
        versao_corrigida="3.5.0",
        link=f"https://github.com/advisories/{ghsa}",
    )


def test_r04a_2_aviso_sem_cvss_ganha_o_do_nvd_com_a_fonte_registrada() -> None:
    sem_cvss = aviso("GHSA-gxr4-xjj5-5px2", "CVE-2020-11022", None)

    completado = completar_cvss([sem_cvss], NvdFalso({"CVE-2020-11022": 6.1}))

    assert completado.avisos[0].cvss == 6.1
    assert completado.avisos[0].fontes == ["GitHub Advisory", "NVD"]
    assert completado.nao_responderam == {}


def test_r04a_2_so_consulta_aviso_com_cve_e_sem_cvss() -> None:
    com_cvss = aviso("GHSA-aaaa-aaaa-aaaa", "CVE-2099-0001", 7.5)
    sem_cve = aviso("GHSA-bbbb-bbbb-bbbb", None, None)
    sem_cvss = aviso("GHSA-cccc-cccc-cccc", "CVE-2099-0003", None)
    nvd_falso = NvdFalso({"CVE-2099-0001": 1.0, "CVE-2099-0003": 5.0})

    completado = completar_cvss([com_cvss, sem_cve, sem_cvss], nvd_falso)

    assert nvd_falso.consultados == ["CVE-2099-0003"]
    assert completado.avisos[:2] == [com_cvss, sem_cve]
    assert completado.avisos[2].cvss == 5.0


def test_r04a_2_faz_uma_consulta_por_cve() -> None:
    do_github = aviso("GHSA-gxr4-xjj5-5px2", "CVE-2020-11022", None)
    do_osv = aviso("GHSA-gxr4-xjj5-5px2", "CVE-2020-11022", None, fontes=["OSV"])
    nvd_falso = NvdFalso({"CVE-2020-11022": 6.1})

    completado = completar_cvss([do_github, do_osv, do_github], nvd_falso)

    assert nvd_falso.consultados == ["CVE-2020-11022"]
    assert [completo.cvss for completo in completado.avisos] == [6.1, 6.1, 6.1]
    assert completado.avisos[1].fontes == ["OSV", "NVD"]


def test_r04a_2_sem_cvss_no_nvd_o_aviso_segue_igual() -> None:
    sem_cvss = aviso("GHSA-cccc-cccc-cccc", "CVE-2099-0003", None)

    completado = completar_cvss([sem_cvss], NvdFalso({"CVE-2099-0003": None}))

    assert completado.avisos == [sem_cvss]


def test_r04a_6_falha_do_nvd_mantem_o_aviso_e_registra_o_motivo() -> None:
    sem_cvss = aviso("GHSA-cccc-cccc-cccc", "CVE-2099-0003", None)
    outro = aviso("GHSA-dddd-dddd-dddd", "CVE-2099-0004", None)
    nvd_falso: BuscaDeCvss = NvdFalso(
        {"CVE-2099-0004": 8.1}, falhas={"CVE-2099-0003": "sem resposta do NVD: sem rede"}
    )

    completado = completar_cvss([sem_cvss, sem_cvss, outro], nvd_falso)

    assert completado.avisos[:2] == [sem_cvss, sem_cvss]
    assert completado.avisos[2].cvss == 8.1
    assert completado.nao_responderam == {"CVE-2099-0003": "sem resposta do NVD: sem rede"}
