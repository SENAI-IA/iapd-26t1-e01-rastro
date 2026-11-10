export interface Retangulo {
  topo: number;
  esquerda: number;
  largura: number;
  altura: number;
}

export interface Tamanho {
  largura: number;
  altura: number;
}

export interface Ponto {
  topo: number;
  esquerda: number;
}

const FOLGA_DO_DESTAQUE = 6;
const DISTANCIA_DO_BALAO = 14;
const MARGEM_DA_TELA = 12;

export function retanguloDoDestaque(alvo: Retangulo, tela: Tamanho, alturaDoTopo: number): Retangulo {
  const topo = Math.max(alvo.topo - FOLGA_DO_DESTAQUE, alturaDoTopo);
  const fim = Math.min(alvo.topo + alvo.altura + FOLGA_DO_DESTAQUE, tela.altura);
  return {
    topo,
    esquerda: alvo.esquerda - FOLGA_DO_DESTAQUE,
    largura: alvo.largura + FOLGA_DO_DESTAQUE * 2,
    altura: Math.max(fim - topo, 0),
  };
}

export function posicaoDoBalao(destaque: Retangulo, balao: Tamanho, tela: Tamanho, alturaDoTopo: number): Ponto {
  const ponto = primeiroLugarQueCabe(destaque, balao, tela, alturaDoTopo);
  const esquerdaMaxima = tela.largura - balao.largura - MARGEM_DA_TELA;
  return {
    topo: ponto.topo,
    esquerda: Math.max(MARGEM_DA_TELA, Math.min(ponto.esquerda, esquerdaMaxima)),
  };
}

function primeiroLugarQueCabe(destaque: Retangulo, balao: Tamanho, tela: Tamanho, alturaDoTopo: number): Ponto {
  const topoMinimo = alturaDoTopo + MARGEM_DA_TELA;
  const baixo = destaque.topo + destaque.altura + DISTANCIA_DO_BALAO;
  if (baixo + balao.altura <= tela.altura - MARGEM_DA_TELA) {
    return { topo: baixo, esquerda: destaque.esquerda };
  }
  const cima = destaque.topo - DISTANCIA_DO_BALAO - balao.altura;
  if (cima >= topoMinimo) {
    return { topo: cima, esquerda: destaque.esquerda };
  }
  const topoAoLado = Math.max(topoMinimo, Math.min(destaque.topo, tela.altura - balao.altura - MARGEM_DA_TELA));
  const direita = destaque.esquerda + destaque.largura + DISTANCIA_DO_BALAO;
  if (direita + balao.largura <= tela.largura - MARGEM_DA_TELA) {
    return { topo: topoAoLado, esquerda: direita };
  }
  const esquerda = destaque.esquerda - DISTANCIA_DO_BALAO - balao.largura;
  if (esquerda >= MARGEM_DA_TELA) {
    return { topo: topoAoLado, esquerda };
  }
  return { topo: tela.altura - balao.altura - MARGEM_DA_TELA, esquerda: tela.largura - balao.largura };
}

export function rolagemParaMostrar(alvo: Retangulo, rolagemAtual: number, tela: Tamanho, alturaDoTopo: number): number {
  const espacoLivre = tela.altura - alturaDoTopo;
  const acimaDoAlvo = alvo.altura < espacoLivre ? (espacoLivre - alvo.altura) / 3 : MARGEM_DA_TELA * 2;
  return Math.max(0, rolagemAtual + alvo.topo - alturaDoTopo - acimaDoAlvo);
}
