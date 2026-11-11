# Tecnologia

## Stack

- **Núcleo e CLI:** Python 3.10 ou mais novo, biblioteca padrão primeiro (`argparse`, `json`, `pathlib`, `dataclasses`, `urllib.request`, `subprocess`).
- **Relatório:** React + TypeScript (template padrão do Vite) + `vite-plugin-singlefile`, gerando um único HTML. O Python embute o JSON da análise nesse HTML.
- **IA:** Kiro (padrão), Claude ou Codex, chamados pela CLI já instalada e autenticada na máquina. Escolha por `--ia` ou `RASTRO_IA`.
- **Dados:** GitHub Advisory; OSV e NVD como extensão opcional. Registro do npm só com leitura, para as travas.
- **Qualidade:** pytest, pytest-cov, ruff, mypy.
- **Entrega:** instalação local, só com Python (o HTML do relatório vai pronto no repo). Opcional: o comando `rastro`, criado pela pessoa com `python -m rastro instalar`. Sem Docker e sem CI; o demo gravado cumpre o requisito "Docker ou vídeo".

## Dependências

- **Python em produção:** nenhuma. Nada de SDK de IA nem chave de API no projeto.
- **Python em desenvolvimento:** `pytest`, `pytest-cov`, `ruff`, `mypy` e `setuptools` (monta o pacote no teste de instalação, sem rede), com versão fixa em `requirements-dev.txt`, instalados num `.venv` na raiz do projeto.
- **Configuração:** `ruff`, `mypy` (modo `strict`), `pytest`, cobertura e o empacotamento (setuptools, comando `rastro` e arquivos de dados do pacote) no `pyproject.toml`. Arquivo novo que não seja `.py` dentro de `rastro/` entra em `[tool.setuptools.package-data]`.
- **Frontend:** `react`, `react-dom`; em desenvolvimento, `vite`, `typescript`, `vite-plugin-singlefile` e o que o template `react-ts` do Vite já traz (`@vitejs/plugin-react` e os pacotes `@types/*`). O linter do template (`oxlint`) fica de fora: o `tsc` do build já confere os tipos. Sem biblioteca de componentes, de estado ou de gráficos. `package-lock.json` versionado.
- Qualquer dependência nova precisa resolver algo que o padrão não resolve. Justifique antes de adicionar.

## Comandos

Só comandos padrão: `python -m venv`, `pip install -r requirements.txt`, `python -m rastro` (com `instalar` e `desinstalar` para o comando `rastro`), `pytest`, `npm install`, `npm run build`. Nada de `Makefile` nem script `.sh`.

## Windows e Linux

Tudo precisa funcionar nos dois.

- Caminhos sempre com `pathlib`.
- Arquivos sempre com `encoding="utf-8"` explícito.
- Executável das CLIs de IA localizado com `shutil.which` (no Windows pode ser `.cmd`).
- **Prompt para a IA sempre pela entrada padrão, nunca como argumento.**
- Saída do terminal em texto simples, sem depender de cor ou emoji.
- Sem CI: `ruff`, `mypy` e `pytest` rodados na máquina local, no Windows e no Linux, antes de cada entrega.
- README com os comandos dos dois sistemas lado a lado.

## Nada destrutivo

- O Rastro só lê o HAR e nunca o altera.
- O relatório é gravado numa pasta nova, `~/Rastro/relatorios/<site>/<AAAA-MM-DD_HH-MM-SS>/` (`--saida` troca a raiz), com arquivos abertos no modo `"x"`; se a pasta já existir, para com mensagem clara. Nome de pasta sem `:` e sem caracteres que o Windows não aceita.
- Nada instalado no sistema, sem `sudo`, e o Rastro não instala nem apaga nada por conta própria. O comando `rastro` só é criado ou removido quando a pessoa pede (`instalar` e `desinstalar`), na pasta do usuário, e só o que tem a marca do Rastro é tocado.
- Vale também para os comandos que o agente roda durante o desenvolvimento.

## Rede

- Só GitHub Advisory, registro do npm (leitura) e, se a extensão for feita, OSV e NVD. Nunca o site analisado.
- O pacote baixado do npm é lido em memória: nada extraído em disco, nada executado.

## Testes

- Cobertura mínima de 60% nas regras de negócio (meta 80%), medida com `pytest-cov`. Relatório versionado em `docs/cobertura/`.
- Verificação: `ruff check`, `mypy rastro` e `pytest --cov=rastro --cov-report=term`, com o `.venv` ativo (comandos na seção "Verificação" do README). O resultado de cada sistema fica em `docs/cobertura/linux.md` e `docs/cobertura/windows.md`. O HTML da cobertura nunca vai direto para `docs/cobertura/`: o `pytest-cov` cria ali um `.gitignore` com `*`. Ele fica em `docs/cobertura/html/` (`--cov-report=html:docs/cobertura/html`), que tem um `.gitignore` versionado que não ignora nada; com a pasta não vazia, o `pytest-cov` não cria o dele. O número das regras de negócio vai para o README a cada atualização.
- Fonte de dados, registro do npm e IA trocados por dublês: testes não acessam rede (um `conftest.py` bloqueia).
- Testes de frontend não são obrigatórios.
