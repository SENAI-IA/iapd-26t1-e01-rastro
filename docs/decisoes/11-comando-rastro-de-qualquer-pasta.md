# Decisão 11: comando `rastro` de qualquer pasta

Requisitos: R17.2, R17.3, R18.1, R20.1 e R20.2. Código: `rastro/instalacao/`, `rastro/comandos/comando_instalar.py`, `rastro/comandos/comando_desinstalar.py`, `rastro/__main__.py` e `pyproject.toml`.

## Contexto

O Rastro só rodava **na raiz do projeto**: `python3 -m rastro analisar site.har` precisa que o Python ache o pacote `rastro/` na pasta atual. O HAR pode estar em qualquer lugar, mas quem usa precisava abrir o terminal, entrar na pasta do Rastro e digitar o caminho completo do HAR (ex.: `~/Downloads/site.har`). Entrar na pasta do Rastro é o passo que mais atrapalha quem não é dev.

A regra do projeto (R17.2, `tech.md` e README) é que o Rastro não instala nada no sistema nem pede `sudo`.

A primeira versão desta decisão usava o pipx: quatro comandos (instalar o pipx, pôr no PATH, instalar o Rastro, conferir), internet e erros que quem não é dev não sabe resolver. Ao seguir o README com o `.venv` do projeto ativo, o passo 1 falhou (`Can not perform a '--user' install`) e, com ele, o resto. No Ubuntu 24.04 o passo 1 é recusado (`externally-managed-environment`) e pede `sudo apt install pipx`.

## Decisão

- A pessoa cria o comando `rastro` com o próprio Rastro, **uma vez, na raiz do projeto**, e remove quando quiser:

  | | Linux | Windows (PowerShell) — a conferir (T42) |
  |---|---|---|
  | Criar o comando | `python3 -m rastro instalar` | `py -m rastro instalar` |
  | Conferir, num terminal novo e em outra pasta | `rastro --help` | `rastro --help` |
  | Remover | `rastro desinstalar` | `rastro desinstalar` |

- Com ele, o uso fica:

  ```
  cd ~/Downloads
  rastro analisar site.har
  rastro como-usar
  ```

- **Quem instala e quem apaga é a pessoa, não o Rastro** (R17.2 e R17.3). O Rastro nunca cria nem remove o comando por conta própria; `instalar` e `desinstalar` só rodam quando a pessoa digita, e mexem só na pasta do usuário. O caminho garantido continua sendo `python -m rastro` na raiz do projeto, sem instalar nada.
- O que o `instalar` faz (`rastro/instalacao/`):
  - Grava um atalho com uma linha de marca (“Criado por `rastro instalar`”): no Linux, `~/.local/bin/rastro`, um script `sh` que roda `python -m rastro` com a raiz do projeto no `PYTHONPATH`; no Windows, `%LOCALAPPDATA%\Rastro\bin\rastro.cmd`, que faz o mesmo.
  - Se a pasta do atalho não estiver no PATH, acrescenta um bloco marcado no `.zshrc`, `.bashrc` ou `.profile`, conforme o `$SHELL`. No Windows, acrescenta a pasta ao PATH do usuário (`HKCU\Environment`, sem administrador) e avisa o sistema para os terminais novos já verem.
  - Usa o Python do sistema, mesmo rodado com o `.venv` ativo, para o atalho não quebrar se o `.venv` for apagado.
  - Rodar de novo atualiza o atalho (por exemplo, depois de mover a pasta do projeto) e não repete o bloco do PATH.
- O que o `desinstalar` faz: apaga só o atalho que tem a marca e tira só o bloco marcado do PATH. Não mexe no projeto nem nos relatórios.
- Um `rastro` sem a marca (do pipx, por exemplo) não é sobrescrito nem apagado: os dois comandos param com código 1 e dizem o que fazer.
- Sem pip, sem internet e sem dependência em produção. Como o atalho aponta para a pasta do projeto, um `git pull` já vale, sem reinstalar.
- O `pyproject.toml` continua com o `[build-system]`, o `[project.scripts]` (`rastro = "rastro.cli:principal"`) e os arquivos de dados do pacote (`modelo.html` e prompts). Quem preferir pode usar `pipx install .`; não é o caminho do README de usuário.
- Teste: `tests/instalacao/` instala e desinstala numa pasta de usuário falsa (`tmp_path`), sem tocar na máquina de quem roda, roda o atalho gravado de outra pasta e confere que um `rastro` de outro não é tocado. O registro do Windows fica para a verificação manual (T42). O `tests/test_instalacao.py` continua montando o pacote (wheel) sem rede para o caminho do pipx.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| `pip install --user .` | No Ubuntu e no Debian recentes é bloqueado (`externally-managed-environment`, PEP 668). No Windows, a pasta `Scripts` do usuário muitas vezes não está no PATH. |
| `sudo pip install .` | Instala no Python do sistema e pede administrador: contra o R17.2. |
| venv do projeto + `pip install -e .` | Só funciona com o venv ativado, então não resolve "de qualquer pasta". Continua sendo o caminho de quem desenvolve. |
| pipx como caminho principal (primeira versão desta decisão) | Quatro comandos, internet, falha com o `.venv` ativo e, no Ubuntu 24.04, pede `sudo apt install pipx`. Continua possível, pelo `pyproject.toml`. |
| Variável `PYTHONPATH` configurada à mão | Configuração manual diferente no Linux e no Windows, fácil de errar e difícil de explicar no README. O `instalar` faz a mesma coisa dentro do atalho, sem a pessoa configurar nada. |
| Script `instalar.sh` e `instalar.ps1` | Dois scripts, um por sistema, fora dos testes em Python; o steering pede nada de script `.sh`. O subcomando fica no mesmo código, testado. |
| Executável único (PyInstaller e parecidos) | Um binário por sistema, gerado e conferido a cada versão; precisa de ferramenta de build que o projeto não tem. Grande demais para o prazo. |
| Servidor local com envio do HAR pelo navegador (`rastro abrir`) | Resolve outra dor (digitar o caminho do HAR), mas muda o escopo (PRD, pitch e PDFs) e exige token contra requisições de outros sites. Fica como plano futuro, mais fácil com esta decisão: `rastro abrir` de qualquer pasta. |
| Testar instalando num venv temporário com `--system-site-packages` | Depende do setuptools do sistema, que no Ubuntu 22.04 (59.6) é antigo demais para ler o `[project]`, e é mais lento. Montar o wheel confere o que pode quebrar (o comando e os arquivos de dados) sem instalar nada. |
