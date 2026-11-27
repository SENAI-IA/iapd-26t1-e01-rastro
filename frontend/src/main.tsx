import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./estilos/fontes.css";
import "./estilos/tokens.css";
import "./estilos/base.css";
import App from "./App.tsx";
import { guardarPaginaOriginal } from "./exportacao/paginaOriginal.ts";
import { lerRelatorioSemValidar } from "./relatorio/lerRelatorioSemValidar.ts";

guardarPaginaOriginal(document);

const raiz = document.getElementById("raiz");
if (raiz === null) {
  throw new Error('A página não tem o elemento com id "raiz", onde o relatório é montado.');
}

createRoot(raiz).render(
  <StrictMode>
    <App relatorio={lerRelatorioSemValidar(document)} />
  </StrictMode>,
);
