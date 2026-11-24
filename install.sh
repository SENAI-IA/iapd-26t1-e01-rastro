#!/bin/sh
# Instala o Rastro na pasta do usuário, sem sudo e sem Git (R17.4):
#
#   curl -fsSL https://raw.githubusercontent.com/SENAI-IA/iapd-26t1-e01-rastro/main/install.sh | bash
#
# Baixa a main do GitHub para ~/.local/share/rastro e roda `rastro instalar`,
# que cria o comando `rastro`. Rodar de novo atualiza. Para remover: rastro desinstalar.
#
# RASTRO_PASTA troca a pasta de destino; RASTRO_ORIGEM troca o endereço do pacote
# (os testes usam um file:// para não acessar a rede).

set -eu

ORIGEM_PADRAO="https://codeload.github.com/SENAI-IA/iapd-26t1-e01-rastro/tar.gz/refs/heads/main"
MARCA_DO_INSTALADOR=".instalado-pelo-install-sh"
PYTHON_MINIMO="3.10"

erro() {
    printf 'rastro: erro: %s\n' "$1" >&2
    exit 1
}

aviso() {
    printf '%s\n' "$1"
}

exigir_comando() {
    command -v "$1" >/dev/null 2>&1 || erro "o comando $1 não foi encontrado. Instale o $1 e rode de novo."
}

python_serve() {
    "$1" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1
}

achar_python() {
    for candidato in python3 python; do
        if command -v "$candidato" >/dev/null 2>&1 && python_serve "$candidato"; then
            command -v "$candidato"
            return 0
        fi
    done
    erro "o Rastro precisa do Python $PYTHON_MINIMO ou mais novo, e ele não foi encontrado. Instale o Python e rode de novo."
}

conferir_pasta_de_destino() {
    if [ -e "$1" ] && [ ! -f "$1/$MARCA_DO_INSTALADOR" ]; then
        erro "a pasta $1 já existe e não foi criada por este instalador. Nada foi alterado."
    fi
}

baixar_e_extrair() {
    origem="$1"
    destino="$2"
    pacote="$destino.tar.gz"
    curl -fsSL "$origem" -o "$pacote" || erro "não foi possível baixar o Rastro de $origem. Confira a internet e rode de novo."
    mkdir "$destino"
    tar -xzf "$pacote" -C "$destino" --strip-components=1 || erro "o pacote baixado está corrompido. Rode de novo."
    rm -f "$pacote"
    [ -f "$destino/rastro/__main__.py" ] || erro "o pacote baixado não tem o Rastro. Nada foi alterado."
    : >"$destino/$MARCA_DO_INSTALADOR"
}

trocar_pasta() {
    nova="$1"
    pasta="$2"
    if [ -e "$pasta" ]; then
        antiga="$pasta.antiga.$$"
        mv "$pasta" "$antiga"
        mv "$nova" "$pasta"
        rm -rf "$antiga"
    else
        mv "$nova" "$pasta"
    fi
}

principal() {
    pasta="${RASTRO_PASTA:-${XDG_DATA_HOME:-$HOME/.local/share}/rastro}"
    origem="${RASTRO_ORIGEM:-$ORIGEM_PADRAO}"

    exigir_comando curl
    exigir_comando tar
    python="$(achar_python)"
    conferir_pasta_de_destino "$pasta"

    aviso "Baixando o Rastro para $pasta ..."
    mkdir -p "$(dirname "$pasta")"
    temporaria="$pasta.nova.$$"
    trap 'rm -rf "$temporaria" "$temporaria.tar.gz"' EXIT
    baixar_e_extrair "$origem" "$temporaria"
    trocar_pasta "$temporaria" "$pasta"

    (cd "$pasta" && "$python" -m rastro instalar)
    aviso "Os arquivos do Rastro ficam em $pasta. Para atualizar, rode este instalador de novo. Para remover: rastro desinstalar"
}

principal "$@"
