import base64
import hashlib
import io
import json
import tarfile
from email.message import Message
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request

import pytest

from rastro.fontes import registro_npm
from rastro.fontes.conector import ConsultaNaoRealizada
from rastro.fontes.registro_npm import RegistroDePacotes, RegistroNpm, ler_arquivos_de_codigo


class RespostaFalsa(io.BytesIO):
    def __init__(self, status: int, corpo: bytes = b"{}") -> None:
        super().__init__(corpo)
        self.status = status


class UrlopenFalso:
    def __init__(self, status: int = 200, erro: Exception | None = None) -> None:
        self.status = status
        self.erro = erro
        self.requisicoes: list[Request] = []
        self.tempos_limite: list[float] = []

    def __call__(self, requisicao: Request, timeout: float) -> RespostaFalsa:
        self.requisicoes.append(requisicao)
        self.tempos_limite.append(timeout)
        if self.erro is not None:
            raise self.erro
        return RespostaFalsa(self.status)


def erro_http(codigo: int) -> HTTPError:
    return HTTPError(registro_npm.ENDERECO_DO_REGISTRO, codigo, "erro", Message(), None)


def consultar(
    monkeypatch: pytest.MonkeyPatch, urlopen_falso: UrlopenFalso, pacote: str, versao: str
) -> bool:
    monkeypatch.setattr(registro_npm, "urlopen", urlopen_falso)
    return RegistroNpm().existe(pacote, versao)


def test_r21_4_registro_npm_cumpre_a_interface() -> None:
    registro: RegistroDePacotes = RegistroNpm()

    assert callable(registro.existe)


def test_r21_4_http_200_confirma_que_foi_publicado(monkeypatch: pytest.MonkeyPatch) -> None:
    assert consultar(monkeypatch, UrlopenFalso(200), "jquery", "3.4.1")


def test_r21_4_http_404_diz_que_nao_foi_publicado(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso(erro=erro_http(404))

    assert not consultar(monkeypatch, urlopen_falso, "jquery", "9.9.9")


def test_r21_4_consulta_o_pacote_e_a_versao_no_registro(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()

    consultar(monkeypatch, urlopen_falso, "jquery", "3.4.1")

    requisicao = urlopen_falso.requisicoes[0]
    assert requisicao.full_url == "https://registry.npmjs.org/jquery/3.4.1"
    assert urlopen_falso.tempos_limite == [15]


def test_r21_4_pacote_com_escopo_usa_a_barra_codificada(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()

    consultar(monkeypatch, urlopen_falso, "@angular/core", "11.0.0")

    assert urlopen_falso.requisicoes[0].full_url == (
        "https://registry.npmjs.org/@angular%2Fcore/11.0.0"
    )


def test_r16_2_so_le_o_registro_do_npm(monkeypatch: pytest.MonkeyPatch) -> None:
    urlopen_falso = UrlopenFalso()

    consultar(monkeypatch, urlopen_falso, "jquery", "3.4.1")

    requisicao = urlopen_falso.requisicoes[0]
    assert requisicao.host == "registry.npmjs.org"
    assert requisicao.get_method() == "GET"
    assert requisicao.data is None


@pytest.mark.parametrize(
    ("erro", "motivo"),
    [
        (URLError("sem rede"), "sem resposta do registro do npm: sem rede"),
        (TimeoutError(), "sem resposta do registro do npm: tempo esgotado"),
        (erro_http(429), "limite de consultas do registro do npm atingido (HTTP 429)"),
        (erro_http(503), "erro no servidor do registro do npm (HTTP 503)"),
        (erro_http(401), "resposta inesperada do registro do npm (HTTP 401)"),
    ],
)
def test_r21_9_sem_resposta_do_registro_vira_consulta_nao_realizada(
    monkeypatch: pytest.MonkeyPatch, erro: Exception, motivo: str
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar(monkeypatch, UrlopenFalso(erro=erro), "jquery", "3.4.1")

    assert falha.value.motivo == motivo


def test_r21_9_codigo_de_sucesso_diferente_de_200_nao_confirma(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        consultar(monkeypatch, UrlopenFalso(204), "jquery", "3.4.1")

    assert falha.value.motivo == "resposta inesperada do registro do npm (HTTP 204)"


ENDERECO_DO_PACOTE = "https://registry.npmjs.org/@angular/core/-/core-22.2.2.tgz"
CODIGO_DO_ANGULAR = "const NG_VERSION_ATTR_NAME = 'ng-version';\nnew Version('22.2.2');"
ARQUIVOS_DO_PACOTE = {
    "package/fesm2022/core.mjs": CODIGO_DO_ANGULAR,
    "package/index.js": "module.exports = 'index';",
    "package/runtime.cjs": "exports.x = 'cjs';",
    "package/package.json": '{"name": "@angular/core"}',
    "package/README.md": "# Angular",
    "package/index.d.ts": "export declare const VERSION: string;",
}


def montar_tgz(arquivos: dict[str, str]) -> bytes:
    memoria = io.BytesIO()
    with tarfile.open(fileobj=memoria, mode="w:gz") as pacote:
        pasta = tarfile.TarInfo("package/pasta.js")
        pasta.type = tarfile.DIRTYPE
        pacote.addfile(pasta)
        for nome, conteudo in arquivos.items():
            dados = conteudo.encode("utf-8")
            membro = tarfile.TarInfo(nome)
            membro.size = len(dados)
            pacote.addfile(membro, io.BytesIO(dados))
        atalho = tarfile.TarInfo("package/atalho.js")
        atalho.type = tarfile.SYMTYPE
        atalho.linkname = "/etc/passwd"
        pacote.addfile(atalho)
    return memoria.getvalue()


def integridade_de(dados: bytes) -> str:
    return "sha512-" + base64.b64encode(hashlib.sha512(dados).digest()).decode("ascii")


def metadados(endereco: str = ENDERECO_DO_PACOTE, integridade: str | None = None) -> bytes:
    distribuicao = {"tarball": endereco, "shasum": "abc"}
    if integridade is not None:
        distribuicao["integrity"] = integridade
    return json.dumps({"name": "@angular/core", "version": "22.2.2", "dist": distribuicao}).encode()


class UrlopenDoPacote:
    def __init__(self, respostas: dict[str, bytes | Exception]) -> None:
        self.respostas = respostas
        self.requisicoes: list[Request] = []

    def __call__(self, requisicao: Request, timeout: float) -> RespostaFalsa:
        self.requisicoes.append(requisicao)
        resposta = self.respostas[requisicao.full_url]
        if isinstance(resposta, Exception):
            raise resposta
        return RespostaFalsa(200, resposta)


def registro_com_pacote(tgz: bytes, metadados_do_pacote: bytes | None = None) -> UrlopenDoPacote:
    return UrlopenDoPacote(
        {
            "https://registry.npmjs.org/@angular%2Fcore/22.2.2": (
                metadados_do_pacote or metadados(integridade=integridade_de(tgz))
            ),
            ENDERECO_DO_PACOTE: tgz,
        }
    )


def ler_codigo(monkeypatch: pytest.MonkeyPatch, urlopen_falso: UrlopenDoPacote) -> list[str]:
    monkeypatch.setattr(registro_npm, "urlopen", urlopen_falso)
    return RegistroNpm().ler_codigo("@angular/core", "22.2.2")


def test_r21_5_le_so_os_arquivos_de_codigo_do_pacote(monkeypatch: pytest.MonkeyPatch) -> None:
    codigos = ler_codigo(monkeypatch, registro_com_pacote(montar_tgz(ARQUIVOS_DO_PACOTE)))

    assert codigos == [CODIGO_DO_ANGULAR, "module.exports = 'index';", "exports.x = 'cjs';"]


def test_r21_5_baixa_os_metadados_e_o_pacote_so_com_leitura(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    urlopen_falso = registro_com_pacote(montar_tgz(ARQUIVOS_DO_PACOTE))

    ler_codigo(monkeypatch, urlopen_falso)

    assert [requisicao.full_url for requisicao in urlopen_falso.requisicoes] == [
        "https://registry.npmjs.org/@angular%2Fcore/22.2.2",
        ENDERECO_DO_PACOTE,
    ]
    assert all(requisicao.get_method() == "GET" for requisicao in urlopen_falso.requisicoes)
    assert all(requisicao.data is None for requisicao in urlopen_falso.requisicoes)


def test_r21_5_nada_e_extraido_em_disco_nem_executado(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def recusar(*_argumentos: object, **_opcoes: object) -> None:
        raise AssertionError("o pacote não pode ser extraído em disco")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(tarfile.TarFile, "extract", recusar)
    monkeypatch.setattr(tarfile.TarFile, "extractall", recusar)

    codigos = ler_codigo(monkeypatch, registro_com_pacote(montar_tgz(ARQUIVOS_DO_PACOTE)))

    assert CODIGO_DO_ANGULAR in codigos
    assert list(tmp_path.iterdir()) == []


def test_r21_5_integridade_diferente_nao_le_o_pacote(monkeypatch: pytest.MonkeyPatch) -> None:
    tgz = montar_tgz(ARQUIVOS_DO_PACOTE)
    adulterado = montar_tgz({"package/index.js": "'inventado'"})
    urlopen_falso = registro_com_pacote(adulterado, metadados(integridade=integridade_de(tgz)))

    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_codigo(monkeypatch, urlopen_falso)

    assert falha.value.motivo == "a integridade do pacote baixado não confere (sha512)"


@pytest.mark.parametrize(
    ("integridade", "motivo"),
    [
        (None, "resposta do registro do npm fora do formato esperado"),
        ("sha1-abc", "pacote sem integridade sha512 no registro do npm"),
    ],
)
def test_r21_5_pacote_sem_sha512_nao_e_lido(
    monkeypatch: pytest.MonkeyPatch, integridade: str | None, motivo: str
) -> None:
    tgz = montar_tgz(ARQUIVOS_DO_PACOTE)
    urlopen_falso = registro_com_pacote(tgz, metadados(integridade=integridade))

    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_codigo(monkeypatch, urlopen_falso)

    assert falha.value.motivo == motivo


def test_r21_5_aceita_integridade_com_mais_de_um_hash(monkeypatch: pytest.MonkeyPatch) -> None:
    tgz = montar_tgz(ARQUIVOS_DO_PACOTE)
    integridade = f"sha1-abc {integridade_de(tgz)}"

    codigos = ler_codigo(monkeypatch, registro_com_pacote(tgz, metadados(integridade=integridade)))

    assert CODIGO_DO_ANGULAR in codigos


def test_r21_5_pacote_acima_de_10_mb_nao_e_lido(monkeypatch: pytest.MonkeyPatch) -> None:
    grande = b"\0" * (10 * 1024 * 1024 + 1)

    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_codigo(monkeypatch, registro_com_pacote(grande, metadados(integridade="sha512-x")))

    assert falha.value.motivo == "pacote acima de 10 MB"


def test_r21_5_codigo_desempacotado_acima_do_limite_nao_e_lido(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(registro_npm, "LIMITE_DO_CODIGO_DESEMPACOTADO_EM_MB", 0)

    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_codigo(monkeypatch, registro_com_pacote(montar_tgz(ARQUIVOS_DO_PACOTE)))

    assert falha.value.motivo == "código do pacote acima de 0 MB desempacotado"


def test_r21_5_pacote_fora_do_registro_nao_e_baixado(monkeypatch: pytest.MonkeyPatch) -> None:
    fora = "https://exemplo.com/core-22.2.2.tgz"
    urlopen_falso = registro_com_pacote(b"", metadados(fora, "sha512-x"))

    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_codigo(monkeypatch, urlopen_falso)

    assert falha.value.motivo == f"pacote fora do registro do npm: {fora}"
    assert len(urlopen_falso.requisicoes) == 1


@pytest.mark.parametrize(
    "resposta", [b"nao e json", b"[]", b'{"dist": {"tarball": 1, "integrity": 2}}']
)
def test_r21_5_metadados_fora_do_formato_viram_consulta_nao_realizada(
    monkeypatch: pytest.MonkeyPatch, resposta: bytes
) -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_codigo(monkeypatch, registro_com_pacote(b"", resposta))

    assert falha.value.motivo == "resposta do registro do npm fora do formato esperado"


def test_r21_5_pacote_corrompido_vira_consulta_nao_realizada() -> None:
    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_arquivos_de_codigo(b"nao e um tgz")

    assert falha.value.motivo.startswith("pacote ilegível: ")


@pytest.mark.parametrize(
    ("erro", "motivo"),
    [
        (URLError("sem rede"), "sem resposta do registro do npm: sem rede"),
        (TimeoutError(), "sem resposta do registro do npm: tempo esgotado"),
        (erro_http(404), "resposta inesperada do registro do npm (HTTP 404)"),
        (erro_http(503), "erro no servidor do registro do npm (HTTP 503)"),
    ],
)
def test_r21_9_falha_ao_baixar_o_pacote_vira_consulta_nao_realizada(
    monkeypatch: pytest.MonkeyPatch, erro: Exception, motivo: str
) -> None:
    tgz = montar_tgz(ARQUIVOS_DO_PACOTE)
    urlopen_falso = registro_com_pacote(tgz)
    urlopen_falso.respostas[ENDERECO_DO_PACOTE] = erro

    with pytest.raises(ConsultaNaoRealizada) as falha:
        ler_codigo(monkeypatch, urlopen_falso)

    assert falha.value.motivo == motivo


def test_r21_9_codigo_diferente_de_200_ao_baixar_nao_le_o_pacote(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(registro_npm, "urlopen", UrlopenFalso(204))

    with pytest.raises(ConsultaNaoRealizada) as falha:
        RegistroNpm().ler_codigo("jquery", "3.4.1")

    assert falha.value.motivo == "resposta inesperada do registro do npm (HTTP 204)"
