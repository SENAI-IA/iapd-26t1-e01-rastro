const FOLGA_ABAIXO_DO_CABECALHO_FIXO = 12;

export function rolarAteOElemento(elemento: Element, alturaDoCabecalhoFixo: number, comportamento?: ScrollBehavior) {
  const topoDoElementoNaPagina = elemento.getBoundingClientRect().top + window.scrollY;
  window.scrollTo({
    top: topoDoElementoNaPagina - alturaDoCabecalhoFixo - FOLGA_ABAIXO_DO_CABECALHO_FIXO,
    behavior: comportamento,
  });
}
