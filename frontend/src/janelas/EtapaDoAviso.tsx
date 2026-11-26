import type { OrigemDoDado } from "../telas/tiposDaTela.ts";
import AvisosNasFontes from "./AvisosNasFontes.tsx";
import EtapaDaOrigem from "./EtapaDaOrigem.tsx";

interface Props {
  origem: OrigemDoDado;
}

export default function EtapaDoAviso({ origem }: Props) {
  return (
    <EtapaDaOrigem numero={3} titulo="Aviso nas fontes">
      <AvisosNasFontes origem={origem} />
    </EtapaDaOrigem>
  );
}
