# Decisão 02: GitHub Advisory como fonte principal

Requisitos: R04 e R04A. Código: `rastro/fontes/`.

## Contexto

Para cada biblioteca (`pacote@versão`), o Rastro precisa dos avisos de falha com CVE, CVSS, EPSS, faixa de versões afetadas e versão corrigida. O prazo era de cinco semanas, e cada fonte a mais traz outro formato, outro limite de uso e outras falhas para tratar.

## Decisão

**O MVP foi desenhado com uma fonte só: o GitHub Advisory.**

- Consulta direta por pacote npm e versão (`affects=<pacote>@<versão>`). No spike T01, 20 pacotes trouxeram 136 avisos, e a versão consultada estava na faixa de todos eles (`docs/spike/github-advisory.md`).
- Traz tudo o que a nota precisa: CVSS v3 ou v4 e o **EPSS já embutido**, sem uma segunda consulta.
- Traz a faixa afetada e a primeira versão corrigida, que viram o plano de ação.
- Não exige chave: 60 consultas por hora sem token, uma por biblioteca, e uma análise cabe nesse limite. Com `GITHUB_TOKEN`, 5.000 por hora.

**OSV e NVD entraram depois, como extensão (T49 a T51)**, porque as fases 1 e 2 fecharam no prazo. O GitHub continua sendo a fonte principal:

- O **OSV** só acrescenta avisos que o GitHub não tem. Ele não traz a nota CVSS (só o vetor) nem o EPSS.
- O **NVD** só completa o CVSS de aviso com CVE que veio sem CVSS, uma vez por CVE.
- Quando as fontes discordam, vale uma ordem fixa: GitHub, OSV e NVD (R04A.4). O EPSS vem só do GitHub. O relatório mostra de qual fonte veio cada campo (R04A.5).
- Se o GitHub não responder, a biblioteca fica "não consultada" (R04.3), e o OSV nem é consultado. Falha do OSV ou do NVD não para nada: vira uma limitação no relatório (R04A.6).

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| OSV como fonte principal | Não traz a nota CVSS nem o EPSS. O Rastro teria que calcular a nota a partir do vetor e buscar o EPSS em outra fonte. |
| NVD como fonte principal | Organiza as falhas por produto (CPE), não por pacote npm. Sem chave, aceita poucas consultas por minuto. |
| Três fontes desde o início | Junção de avisos e ordem entre fontes antes de ter o núcleo pronto. Arriscava o prazo, então ficou como extensão. |
| Bases comerciais (Snyk e outras) | Exigem conta e chave, o que vai contra "sem chave no projeto", e a licença limita o uso. |
| Base do Retire.js | Feita para bibliotecas JavaScript, mas é mantida pela comunidade, sem EPSS, e não é fonte oficial de falhas (R04.5). |
| CISA KEV, Exploit-DB, Vulners | Fora do escopo do MVP. Estão nos planos futuros, como um conector a mais em `rastro/fontes/`. |
