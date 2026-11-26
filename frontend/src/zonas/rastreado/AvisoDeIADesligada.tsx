import Icone from "../../basicos/Icone.tsx";
import Termo from "../../basicos/Termo.tsx";

export default function AvisoDeIADesligada() {
  return (
    <p className="painel-da-ia__desligada">
      <Icone nome="informacao" />
      <span>
        <b>IA desligada nesta análise.</b> Nenhuma chamada foi feita. As travas que conferem o registro do{" "}
        <Termo nome="npm" /> e a faixa de versão afetada rodam também sem IA.
      </span>
    </p>
  );
}
