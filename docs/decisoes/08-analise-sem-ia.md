# Decisão 08: análise sem IA permitida, mas sempre marcada como incompleta

Requisitos: R14.3, R14.5 a R14.7. Código: `rastro/cli.py` e `rastro/relatorio/json.py`; no frontend, `AvisoSemIA`.

## Contexto

Nem todo auditor tem a CLI de uma IA instalada e autenticada. Num ambiente sem IA, ou mais tarde na esteira com Playwright, a análise ainda precisa rodar. A maior parte do Rastro já é regra determinística: leitura do HAR, assinaturas, fontes, travas 4 e 6, nota, checagens e plano de ação.

O risco é a falsa segurança. Sem IA, as bibliotecas escondidas em bundles não são procuradas, e um relatório com "0 encontradas" pode ser lido como "não há nada".

## Decisão

- **`--sem-ia` existe, mas nunca em silêncio.** O aviso aparece:
  - no terminal, no começo e no fim da análise;
  - no topo do relatório, numa faixa sempre visível, com o que falta: bundles não procurados e achados sem explicação simples nem teste de verificação;
  - no indicador "encontradas só pela IA", que mostra "não procurado", e não zero (R14.6);
  - no `--help`, na mesma linha da opção (R14.7).
- O relatório também diz **o que continua igual:** a nota, a prioridade, as checagens e o plano de ação são os mesmos de uma análise com IA.
- **O padrão é com IA** (Kiro). Se a CLI escolhida não for encontrada, o Rastro encerra com código 1 antes de ler o HAR, diz qual CLI faltou e sugere `--sem-ia`, com o que se perde (R14.3). Não troca sozinho para a análise sem IA.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| IA obrigatória | Barra quem não tem CLI e a execução na esteira, mesmo com a maior parte da análise sem depender de IA. |
| Sem IA automático quando a CLI falta | O auditor acharia que teve a análise completa. A troca precisa ser uma escolha dele. |
| Sem IA como padrão | O padrão seria a análise incompleta, e a IA é o que acha as bibliotecas em bundles. |
| Aviso só no terminal | O relatório é encaminhado para quem nunca viu o terminal. O aviso precisa estar no arquivo. |
