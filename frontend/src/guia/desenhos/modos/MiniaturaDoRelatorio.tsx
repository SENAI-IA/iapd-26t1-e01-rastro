import Janela from "../pecas/Janela.tsx";

export default function MiniaturaDoRelatorio() {
  return (
    <Janela tamanho="pequeno">
      <rect className="modo-anim__traco modo-anim__traco--destaque" x="8" y="17" width="16" height="10" rx="1.5" />
      <rect className="modo-anim__traco" x="27" y="17" width="16" height="10" rx="1.5" />
      <rect className="modo-anim__traco" x="46" y="17" width="16" height="10" rx="1.5" />
      <circle className="modo-anim__traco" cx="20" cy="41" r="8" />
      <line className="modo-anim__traco modo-anim__traco--destaque modo-anim__traco--grosso" x1="36" y1="36" x2="60" y2="36" />
      <line className="modo-anim__traco modo-anim__traco--destaque modo-anim__traco--grosso" x1="36" y1="44" x2="52" y2="44" />
    </Janela>
  );
}
