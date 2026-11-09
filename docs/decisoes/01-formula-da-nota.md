# Decisão 01: fórmula da nota e pesos 0,5 / 0,5

Requisito: R05. Código: `rastro/risco/nota.py` e `rastro/risco/prioridade.py`.

## Contexto

O auditor recebe vários avisos e precisa saber o que corrigir primeiro. Duas medidas públicas ajudam:

- **CVSS** (0 a 10): o tamanho do estrago se a falha for explorada. Não diz se alguém explora a falha de verdade.
- **EPSS**: a chance de a falha ser explorada nos próximos 30 dias, calculada pelo FIRST. O GitHub Advisory traz a probabilidade e o percentil (de 0 a 1, a posição da falha entre todas as outras).

A nota precisa ser explicável e refeita à mão na frente do time, e a IA não pode mexer nela (R05.7).

## Decisão

```
nota = 10 × (0,5 × CVSS/10 + 0,5 × percentil EPSS)
```

- **Pesos iguais.** O grupo não tem dado próprio de exploração para calibrar os pesos. Sem esse dado, dar mais peso a um dos lados seria um palpite. Metade e metade se explica numa frase: gravidade e chance de ataque valem o mesmo.
- **Percentil, não probabilidade.** A probabilidade fica quase sempre perto de zero e apagaria o EPSS da soma. No spike T01, o mesmo aviso trouxe probabilidade 0,00049 e percentil 0,21662 (`docs/spike/github-advisory.md`).
- **Escala de 0 a 10**, a mesma do CVSS, para comparar a nota com o CVSS e com a nota sem EPSS ([decisão 07](07-epss-ausente.md)).
- **Uma casa decimal, meio para cima**, com `Decimal`: CVSS 6,1 e percentil 0 dão 3,1, como na conta feita à mão. Com `float` daria 3,0.
- **Faixas:** alta ≥ 7,5; média ≥ 6,5; baixa no resto (R05.2). A nota da biblioteca é a maior nota dos seus achados.
- **A conta vai escrita no relatório:** `10 × (0,5 × 6,1/10 + 0,5 × 0,97) = 7,9`. Qualquer pessoa confere.

Efeito na ordem: uma falha com CVSS 6,1 e percentil 0,97 fica com 7,9 (alta). Uma com CVSS 9,8 e percentil 0,10 fica com 5,4 (baixa). O CVSS continua visível ao lado da nota, e no empate de nota vale o CVSS maior (R05.6).

**Em aberto:** os pesos e as faixas serão conferidos com os dados reais da avaliação na T46. Se mudarem, a mudança passa pela spec e por esta decisão.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Só o CVSS | É o que a maioria das ferramentas faz. Ignora se a falha é explorada de fato, e muitos avisos médios e altos empatam. |
| Só o EPSS | Falha recente ainda tem EPSS baixo, e aviso sem CVE nem tem EPSS. Uma falha grave e nova ficaria no fim da lista. |
| Multiplicar CVSS × EPSS | Um percentil baixo zera uma falha grave, e o produto é difícil de explicar para quem não é de segurança. |
| Pesos calibrados com dados | Seria o melhor, mas não há base de exploração real para as bibliotecas da avaliação. Fica para depois da T46. |
| Árvore de decisão (SSVC) ou lista de falhas exploradas (CISA KEV) | Precisa de fontes que estão fora do escopo do MVP (KEV está nos planos futuros). |
| A IA dá a nota | Resultado muda a cada chamada e não se explica. Proibido por R05.7. |
