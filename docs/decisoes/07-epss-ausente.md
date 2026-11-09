# Decisão 07: sem EPSS, a nota é igual ao CVSS

Requisitos: R05.3 e R05.4. Código: `rastro/risco/nota.py`.

## Contexto

A fórmula da nota ([decisão 01](01-formula-da-nota.md)) usa CVSS e EPSS. O EPSS só existe para falha com CVE. No spike T01, 12 de 136 avisos (8,8%) vieram sem EPSS, e **todos eram avisos sem CVE**, só com GHSA. Seis deles tinham CVSS; os outros seis não tinham nem CVSS (`docs/spike/github-advisory.md`).

## Decisão

| Situação | Nota | Prioridade | No relatório |
|---|---|---|---|
| CVSS e EPSS | a fórmula | pela faixa | `10 × (0,5 × 6,1/10 + 0,5 × 0,97) = 7,9` |
| Só CVSS | igual ao CVSS | pela faixa | selo "sem EPSS" e `sem EPSS: nota = CVSS = 6,1` |
| Sem CVSS | sem nota | "a avaliar" | `sem CVSS: sem nota`, no fim da lista, sem sumir |

- O CVSS está na mesma escala de 0 a 10 da nota. Usá-lo sozinho mantém a nota comparável com as outras e não inventa dado nenhum.
- O selo "sem EPSS" e a conta escrita mostram que ali a chance de exploração não entrou.
- Com a extensão do NVD (T50), o CVSS que faltava pode vir de lá. O EPSS vem só do GitHub.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| EPSS = 0 | Corta a nota pela metade: um CVSS 9,8 viraria 4,9 e "baixa". Rebaixa justo o aviso sem CVE, que não tem como ter EPSS. |
| EPSS médio da base | É um número que não veio de nenhuma fonte. Vai contra R21.8. |
| Descartar o aviso | Esconde uma falha real. R05.4 proíbe esconder achado. |
| Consultar o EPSS no FIRST pelo CVE | O aviso sem EPSS é o que não tem CVE: não há o que consultar. |
| A IA estima o EPSS | A IA nunca preenche CVSS nem EPSS (R21.8). |
