import MenuDeLinks from "../pecas/MenuDeLinks.tsx";

export default function MiniaturaDaPaginaComLinks() {
  return (
    <>
      <MenuDeLinks tamanho="pequeno" />
      <line className="animacao-do-modo__traco animacao-do-modo__traco--suave" x1="8" y1="34" x2="60" y2="34" />
      <line className="animacao-do-modo__traco animacao-do-modo__traco--suave" x1="8" y1="42" x2="48" y2="42" />
    </>
  );
}
