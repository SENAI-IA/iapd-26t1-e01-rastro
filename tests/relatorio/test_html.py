import json
import re
from html.parser import HTMLParser
from typing import Any

import pytest

from rastro.relatorio.html import (
    TAG_DOS_DADOS_VAZIA,
    ModeloSemTagDosDados,
    ler_modelo,
    montar_html,
)

DADOS_MALICIOSOS = {
    "resumo": "</script><script>alert(1)</script>",
    "comentario": "<!--<script>",
    "maiusculas": "</SCRIPT >",
    "acento": "não procurado",
}
MODELO_MINIMO = f"<html><body>{TAG_DOS_DADOS_VAZIA}<div id='raiz'></div></body></html>"
ENDERECO_EMBUTIDO = "data:"


class LeitorDeTags(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.enderecos: list[str] = []
        self.scripts: list[dict[str, str | None]] = []
        self.conteudo_dos_dados: str | None = None
        self._dentro_dos_dados = False

    def handle_starttag(self, tag: str, atributos: list[tuple[str, str | None]]) -> None:
        mapa = dict(atributos)
        self.enderecos.extend(
            valor for nome, valor in atributos if nome in ("src", "href") and valor
        )
        if tag == "script":
            self.scripts.append(mapa)
            self._dentro_dos_dados = mapa.get("id") == "dados"

    def handle_endtag(self, tag: str) -> None:
        if tag == "script":
            self._dentro_dos_dados = False

    def handle_data(self, dados: str) -> None:
        if self._dentro_dos_dados:
            self.conteudo_dos_dados = (self.conteudo_dos_dados or "") + dados


def ler_tags(html: str) -> LeitorDeTags:
    leitor = LeitorDeTags()
    leitor.feed(html)
    leitor.close()
    return leitor


def test_r13_5_dados_entram_na_tag_dos_dados() -> None:
    html = montar_html(MODELO_MINIMO, {"versao_formato": 1, "site": "loja.exemplo.com"})

    conteudo = ler_tags(html).conteudo_dos_dados

    assert conteudo is not None
    assert json.loads(conteudo) == {"versao_formato": 1, "site": "loja.exemplo.com"}


def test_r13_5_fechamento_de_script_nos_dados_nao_quebra_a_pagina() -> None:
    html = montar_html(MODELO_MINIMO, DADOS_MALICIOSOS)

    tags = ler_tags(html)

    assert len(tags.scripts) == 1
    assert tags.conteudo_dos_dados is not None
    assert "<" not in tags.conteudo_dos_dados
    assert json.loads(tags.conteudo_dos_dados) == DADOS_MALICIOSOS


def test_r13_5_resto_do_modelo_fica_igual() -> None:
    html = montar_html(MODELO_MINIMO, {"a": 1})

    antes, depois = MODELO_MINIMO.split(TAG_DOS_DADOS_VAZIA)
    assert html.startswith(antes + '<script id="dados" type="application/json">')
    assert html.endswith("</script>" + depois)


def test_r13_5_modelo_sem_a_tag_dos_dados_e_recusado() -> None:
    with pytest.raises(ModeloSemTagDosDados, match="build do frontend"):
        montar_html("<html><body></body></html>", {})


def test_r13_5_modelo_com_a_tag_repetida_e_recusado() -> None:
    with pytest.raises(ModeloSemTagDosDados):
        montar_html(TAG_DOS_DADOS_VAZIA * 2, {})


def test_r13_5_modelo_do_pacote_traz_a_tag_dos_dados_vazia() -> None:
    assert ler_modelo().count(TAG_DOS_DADOS_VAZIA) == 1


def test_r13_5_modelo_do_pacote_nao_busca_nada_na_rede() -> None:
    modelo = ler_modelo()
    tags = ler_tags(modelo)

    enderecos_de_css = re.findall(r"url\(\s*['\"]?([^)'\"]*)", estilos_do_modelo(modelo))
    assert tags.enderecos
    assert all(e.startswith(ENDERECO_EMBUTIDO) for e in tags.enderecos + enderecos_de_css)
    assert all("src" not in script for script in tags.scripts)
    assert "@import" not in estilos_do_modelo(modelo)


def test_r13_5_relatorio_real_embutido_no_modelo_do_pacote() -> None:
    relatorio: dict[str, Any] = {"versao_formato": 1, "achados": [DADOS_MALICIOSOS]}

    tags = ler_tags(montar_html(ler_modelo(), relatorio))

    assert tags.conteudo_dos_dados is not None
    assert json.loads(tags.conteudo_dos_dados) == relatorio


def estilos_do_modelo(modelo: str) -> str:
    return "".join(re.findall(r"<style[^>]*>(.*?)</style>", modelo, flags=re.DOTALL))
