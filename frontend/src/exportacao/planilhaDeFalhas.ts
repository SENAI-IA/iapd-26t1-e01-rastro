import type { Achado, Biblioteca, Prioridade, Relatorio } from "../relatorio/tiposDoRelatorio.ts";

type Celula = string | number | null;

const SEPARADOR = ";";
const FIM_DE_LINHA = "\r\n";
const MARCA_DE_UTF8 = "﻿";
const COMECO_DE_FORMULA = /^[=+\-@\t\r]/;
const PRECISA_DE_ASPAS = /[";\r\n]/;
const NUMERO = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 5, useGrouping: false });

const CABECALHO = [
  "Pacote",
  "Versão",
  "GHSA",
  "CVE",
  "Resumo",
  "CVSS",
  "EPSS (percentil)",
  "Nota",
  "Prioridade",
  "Versões afetadas",
  "Versão corrigida",
  "Link",
];

const NOME_DA_PRIORIDADE: Record<Prioridade, string> = {
  alta: "alta",
  media: "média",
  baixa: "baixa",
  "a avaliar": "a avaliar",
};

function textoDaCelula(valor: Celula): string {
  if (valor === null) {
    return "";
  }
  if (typeof valor === "number") {
    return NUMERO.format(valor);
  }
  const semFormula = COMECO_DE_FORMULA.test(valor) ? `'${valor}` : valor;
  return PRECISA_DE_ASPAS.test(semFormula) ? `"${semFormula.replaceAll('"', '""')}"` : semFormula;
}

function linhaDaPlanilha(celulas: Celula[]): string {
  return celulas.map(textoDaCelula).join(SEPARADOR);
}

function celulasDoAchado(achado: Achado, bibliotecas: Biblioteca[]): Celula[] {
  const biblioteca = bibliotecas.find((candidata) => candidata.id === achado.biblioteca);
  const { aviso, nota } = achado;
  return [
    biblioteca?.pacote ?? achado.biblioteca,
    biblioteca?.versao ?? null,
    aviso.ghsa,
    aviso.cve,
    aviso.resumo,
    aviso.cvss,
    aviso.percentil_epss,
    nota.valor,
    NOME_DA_PRIORIDADE[nota.prioridade],
    aviso.versoes_afetadas,
    aviso.versao_corrigida,
    aviso.link,
  ];
}

export function montarPlanilhaDeFalhas(relatorio: Relatorio): string {
  const linhas = [
    linhaDaPlanilha(CABECALHO),
    ...relatorio.achados.map((achado) => linhaDaPlanilha(celulasDoAchado(achado, relatorio.bibliotecas))),
  ];
  return MARCA_DE_UTF8 + linhas.join(FIM_DE_LINHA) + FIM_DE_LINHA;
}
