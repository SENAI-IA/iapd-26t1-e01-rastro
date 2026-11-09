# Decisão 10: o NVD ganha a interface `BuscaDeCvss`

Requisitos: R04A.2, R04A.6 e R19.2. Código: `rastro/fontes/nvd.py` e `rastro/fluxo.py`.

## Contexto

O `structure.md` limitava as interfaces a três pontos de troca real: `ConectorDeAvisos`, `RegistroDePacotes` e `ProvedorDeIA`. A extensão do NVD (T50) trouxe um quarto: o NVD é rede (borda), e os testes precisam trocá-lo por um dublê sem acessar a rede (R19.2). Ele não cabe no `ConectorDeAvisos`, porque não devolve avisos: só completa o CVSS de um CVE que já veio do GitHub ou do OSV.

## Decisão

- O NVD fica atrás de `BuscaDeCvss`, um `Protocol` com um único método: `buscar_cvss(cve) -> float | None`.
- O `fluxo.py` recebe a `BuscaDeCvss` como recebe as outras fontes. Nos testes, ela vira o `NvdFalso` de `tests/dubles.py`.
- O `structure.md` passa a listar as quatro interfaces.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Reaproveitar o `ConectorDeAvisos` | O contrato é `consultar(pacote, versão) -> list[Aviso]`. O NVD é consultado por CVE e devolve um número. Forçar o formato esconderia o que a fonte faz. |
| Passar uma função (`Callable[[str], float \| None]`) | Funciona, mas é a mesma interface com outro nome, e fica diferente das outras três fontes na hora de ler o `fluxo.py`. |
| Chamar o NVD direto no `fluxo.py` | Os testes do fluxo passariam a depender de rede ou de monkeypatch na borda, contra R19.2. |
