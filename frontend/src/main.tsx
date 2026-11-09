import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./fontes.css";
import "./tokens.css";
import "./base.css";
import App from "./App.tsx";
import { lerRelatorio } from "./dados.ts";

createRoot(document.getElementById("raiz")!).render(
  <StrictMode>
    <App relatorio={lerRelatorio(document)} />
  </StrictMode>,
);
