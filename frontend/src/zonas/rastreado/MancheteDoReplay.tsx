import type { Chegada } from "../../calculosDeTela/chegadasDaVisita.ts";
import { formatarDuracao } from "../../formatacao/formato.ts";

interface Props {
  chegaram: number;
  total: number;
  falhas: Chegada[];
}

export default function MancheteDoReplay({ chegaram, total, falhas }: Props) {
  if (falhas.length === 0 && chegaram < total) {
    return <>Seguindo o rastro da visita…</>;
  }
  if (falhas.length === 0) {
    return <>Nenhuma das {total} requisições trouxe biblioteca com falha conhecida.</>;
  }
  const quando = formatarDuracao((falhas.at(-1)?.inicio_ms ?? 0) / 1000);
  const quantas = falhas.length === 1 ? "1 biblioteca com falha conhecida" : `${falhas.length} bibliotecas com falha conhecida`;
  return (
    <>
      Com <strong className="replay__numero">{quando}</strong> de visita,{" "}
      <strong className="replay__numero replay__numero--alerta">{quantas}</strong>{" "}
      {falhas.length === 1 ? "já estava" : "já estavam"} no navegador de quem acessou.
    </>
  );
}
