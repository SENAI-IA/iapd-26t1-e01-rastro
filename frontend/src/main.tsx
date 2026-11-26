import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./estilos/fontes.css";
import "./estilos/tokens.css";
import "./estilos/base.css";
import App from "./App.tsx";
import { lerRelatorio } from "./relatorio/lerRelatorio.ts";

createRoot(document.getElementById("raiz")!).render(
  <StrictMode>
    <App relatorio={lerRelatorio(document)} />
  </StrictMode>,
);
