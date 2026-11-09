# Decisão 04: IA pela CLI, sem SDK nem chave

Requisitos: R14, R16.3 e R20.3. Código: `rastro/ia/cliente.py` e `rastro/ia/provedores/`.

## Contexto

Quem usa o Rastro já tem, na própria máquina, a CLI de uma IA instalada e autenticada: Kiro, Claude Code ou Codex. Chave de API no projeto seria um segredo a guardar, a dividir no grupo e a não vazar no repositório. As regras do projeto pedem biblioteca padrão primeiro e nenhuma dependência de produção.

## Decisão

- O Rastro chama a CLI com `subprocess.run`, com o caminho que `shutil.which` achou. Não usa SDK nem chave, e não instala nem autentica nenhuma CLI (R20.3).
- **Três provedores, um arquivo cada**, em `rastro/ia/provedores/`. A escolha é feita por `--ia`, senão por `RASTRO_IA`, senão o Kiro (R14.1).
- **O prompt vai pela entrada padrão, nunca como argumento** (R14.4). Assim ele não aparece na lista de processos e não esbarra no limite de tamanho da linha de comando do Windows.
- **As opções desligam ferramentas e gravação:** a IA só responde, sem ler, rodar ou gravar nada na máquina (`docs/spike/clis-de-ia.md`).
- **Toda falha** (código de saída, tempo limite de 120 s, resposta com erro ou vazia) vira `FalhaDoProvedor`. A análise segue sem aquele dado, e a falha aparece no painel da IA.
- **Tokens só quando a CLI informa.** O Kiro não informa, e o relatório mostra "não informado", sem estimar (R11.2).
- O texto passa pela sanitização dentro do cliente, antes de chegar ao provedor (R16.3).

O que isso custa:

- O Rastro não escolhe o modelo: vale o padrão de cada CLI.
- Cada CLI soma o próprio prompt de sistema: de 12 mil a 27 mil tokens de entrada por chamada, no spike T02. A T46 mede o custo real.
- O comando de cada CLI pode mudar de uma versão para outra. As versões conferidas estão no spike T02.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| SDK oficial (Anthropic, OpenAI) | Exige chave de API e uma dependência de produção por provedor, e a cobrança vai para a conta da API, não para a assinatura que a pessoa já tem. |
| Chamada HTTP direta à API | Sem dependência, mas continua exigindo chave no projeto. |
| Modelo local (Ollama e outros) | Exige instalar e baixar um modelo grande na máquina do auditor, o que vai contra "não instala nada". Máquina comum, sem GPU, fica lenta. |
| Um provedor só | Prende o Rastro a quem tem aquela assinatura. Com uma interface pequena, os três custam pouco a mais. |
| Prompt como argumento da CLI | Fica visível na lista de processos e pode passar do limite da linha de comando no Windows. |
