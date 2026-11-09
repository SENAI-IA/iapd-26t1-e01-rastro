import { readFileSync } from "node:fs";
import react from "@vitejs/plugin-react";
import { defineConfig, type Plugin } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

function svgComoDataUrl(caminho: string): string {
  const svg = readFileSync(new URL(caminho, import.meta.url), "utf-8");
  return `data:image/svg+xml,${encodeURIComponent(svg.trim())}`;
}

function embutirFavicon(): Plugin {
  return {
    name: "rastro-embutir-favicon",
    transformIndexHtml: {
      order: "pre",
      handler: (html) =>
        html
          .replace("/src/assets/logo-claro.svg", svgComoDataUrl("./src/assets/logo-claro.svg"))
          .replace("/src/assets/logo-escuro.svg", svgComoDataUrl("./src/assets/logo-escuro.svg")),
    },
  };
}

export default defineConfig({
  plugins: [react(), viteSingleFile(), embutirFavicon()],
});
