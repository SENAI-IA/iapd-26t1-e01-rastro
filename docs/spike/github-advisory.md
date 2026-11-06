# Spike: GitHub Advisory e EPSS (T01)

Exploração de 06/11/2026, sem token, para responder as perguntas da seção 17 do design sobre a fonte. Afeta a seção 7 e a 9 do design e os critérios R04.4 e R05.3.

## Como foi feito

Um script com a biblioteca padrão (`urllib.request`), fora do repositório, consultou 20 pacotes npm em versões antigas, uma requisição por pacote:

```
GET https://api.github.com/advisories?ecosystem=npm&affects=<pacote>@<versao>&per_page=100
Accept: application/vnd.github+json
```

| Pacote | Versão | Avisos | Retirados | Sem EPSS | Sem CVSS |
|---|---|---|---|---|---|
| jquery | 3.4.1 | 3 | 1 | 0 | 0 |
| jquery-ui | 1.12.1 | 4 | 0 | 0 | 0 |
| bootstrap | 3.3.7 | 8 | 1 | 0 | 0 |
| lodash | 4.17.15 | 6 | 1 | 0 | 0 |
| moment | 2.29.1 | 2 | 0 | 0 | 0 |
| angular | 1.7.9 | 12 | 0 | 1 | 0 |
| handlebars | 4.0.11 | 21 | 1 | 6 | 3 |
| underscore | 1.12.0 | 2 | 0 | 0 | 0 |
| dompurify | 2.0.7 | 24 | 1 | 4 | 3 |
| vue | 2.6.10 | 1 | 0 | 0 | 0 |
| axios | 0.21.0 | 26 | 1 | 0 | 0 |
| minimist | 1.2.0 | 3 | 1 | 0 | 0 |
| marked | 0.3.6 | 8 | 3 | 0 | 0 |
| highlight.js | 9.18.1 | 2 | 0 | 1 | 1 |
| knockout | 3.4.2 | 2 | 1 | 0 | 0 |
| jquery-validation | 1.19.2 | 4 | 0 | 0 | 1 |
| chart.js | 2.9.3 | 1 | 0 | 0 | 0 |
| sanitize-html | 1.20.0 | 10 | 0 | 0 | 0 |
| socket.io-client | 2.3.0 | 0 | 0 | 0 | 0 |
| @angular/core | 11.0.0 | 8 | 0 | 0 | 0 |
| **Total** | | **147** | **11** | **12** | **8** |

"Sem EPSS" e "Sem CVSS" contam só os avisos não retirados (136).

## Respostas

### Limite sem token

- **60 requisições por hora** por IP (`X-RateLimit-Limit: 60`, recurso `core`). Cada consulta levou cerca de 0,4 s (a maior, 1,9 s).
- O Rastro faz uma requisição por biblioteca: os 20 pacotes deste spike gastaram 20. **Uma análise com até 60 bibliotecas cabe no limite sem token.** Várias análises na mesma hora dividem as 60; passou disso, as bibliotecas restantes ficam "não consultada" (R04.3).
- Com `GITHUB_TOKEN`, o limite sobe para 5.000 por hora. **R04.4 continua como está:** o token é opcional e só usado quando existe.
- Nenhuma resposta passou de 26 avisos, nem trouxe o cabeçalho `Link` de paginação. Com `per_page=100`, o Rastro não precisa paginar.

### Formato de `epss`

```json
"epss": { "percentage": 0.00049, "percentile": 0.21662 }
```

- É um objeto, não uma lista. O Rastro usa `percentile` (0 a 1), como o design previa.
- **Sem EPSS, a chave `epss` não vem na resposta** (não é `null`). A leitura precisa ser `aviso.get("epss")`.

### Formato de `cvss_severities`

```json
"cvss": { "vector_string": "CVSS:3.1/AV:N/...", "score": 6.1 },
"cvss_severities": {
  "cvss_v3": { "vector_string": "CVSS:3.1/AV:N/...", "score": 6.1 },
  "cvss_v4": { "vector_string": null, "score": 0.0 }
}
```

- **CVSS ausente vem como `score: 0.0` e `vector_string: null`**, não como `null`. A regra "se nulo, usa o próximo" do design não funcionava: pegaria o 0,0. Vale o CVSS **só quando `vector_string` está preenchido**.
- O campo `cvss` é o legado: igual ao `cvss_v3` quando existe e `null` quando não existe. Não acrescenta nada; o Rastro não o usa.
- **21 avisos (15%) só têm CVSS v4.** Sem ler o `cvss_v4`, eles ficariam sem nota.

### Com que frequência o EPSS vem vazio

- **12 de 136 avisos (8,8%) vêm sem EPSS**, em 4 dos 19 pacotes com avisos (angular, handlebars, dompurify, highlight.js).
- **Todos os 12 não têm CVE.** O EPSS só existe para CVE, então "sem EPSS" é previsível: aviso só com GHSA.
- Desses 12, 6 têm CVSS (nota igual ao CVSS, selo "sem EPSS") e 6 também não têm CVSS ("sem nota", "a avaliar").
- **8 de 136 (5,9%) vêm sem CVSS** (nem v3 nem v4). Dois deles têm EPSS, mas sem CVSS a fórmula não fecha: "a avaliar", como já diz R05.4.
- Conclusão: **R05.3 se mantém.** A taxa é baixa e a causa é explicável ("o aviso não tem CVE").

## O que mais apareceu

| Achado | Quantos | O que muda |
|---|---|---|
| Avisos **retirados** (`withdrawn_at` preenchido) vêm na resposta | 11 de 147 (7,5%) | O Rastro descarta aviso retirado (novo R04.6). Senão, conta duplicata como falha. |
| `vulnerabilities` traz outros ecossistemas (nuget, maven, rubygems) e outros pacotes npm | 21 e 15 avisos | Usar só os itens com `ecosystem == "npm"` e `name == pacote`. |
| O mesmo pacote com **mais de uma faixa** no mesmo aviso | 46 de 136 (34%) | Vale a faixa que contém a versão (trava 6); a versão corrigida sai dela. |
| `first_patched_version` nulo | 19 faixas | Caso "sem correção publicada" do plano de ação (R08). |
| Formatos de faixa | `<`, `<=`, `>=`, `>= x, < y`, `>= x, <= y` | Os que a seção 8 do design já previa. |
| Em todos os avisos, a versão consultada estava em uma das faixas | 136 de 136 | O filtro `affects` funciona. A trava 6 continua como defesa e para escolher a faixa. |
| Pacote com escopo | `@angular/core@11.0.0` | Funciona com `/` puro e com `%2F`. |
| Pacote inexistente ou versão sem falhas | `200` e lista vazia | Lista vazia não prova que o pacote existe; isso é da trava 4 (npm). |
| Aviso `unreviewed` | 1 (já retirado) | Nada a fazer no MVP. |

## O que foi ajustado na spec

- `design.md`, seção 7: tabela de campos com a regra do `vector_string`, a chave `epss` ausente, o filtro de `vulnerabilities` e o descarte dos retirados; o limite confirmado, sem `[spike]`.
- `design.md`, seção 9: "sem EPSS" confirmado, sem `[spike]`.
- `design.md`, seção 17: as duas perguntas da fonte marcadas como respondidas.
- `requirements.md`: R04.4 e R05.3 sem `[spike]`; R04.6 novo (aviso retirado é descartado).
- `tasks.md`: a T12 passa a cobrir R04.6.
