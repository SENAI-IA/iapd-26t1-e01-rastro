import Janela from "../pecas/Janela.tsx";

export default function MiniaturaDoRelatorio() {
  return (
    <Janela tamanho="pequeno">
      <rect className="animacao-do-modo__traco animacao-do-modo__traco--destaque" x="8" y="17" width="16" height="10" rx="1.5" />
      <rect className="animacao-do-modo__traco" x="27" y="17" width="16" height="10" rx="1.5" />
      <rect className="animacao-do-modo__traco" x="46" y="17" width="16" height="10" rx="1.5" />
      <circle className="animacao-do-modo__traco" cx="20" cy="41" r="8" />
      <line className="animacao-do-modo__traco animacao-do-modo__traco--destaque animacao-do-modo__traco--grosso" x1="36" y1="36" x2="60" y2="36" />
      <line className="animacao-do-modo__traco animacao-do-modo__traco--destaque animacao-do-modo__traco--grosso" x1="36" y1="44" x2="52" y2="44" />
    </Janela>
  );
}
