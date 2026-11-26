export function depoisDeDesenhar(acao: () => void) {
  requestAnimationFrame(acao);
}
