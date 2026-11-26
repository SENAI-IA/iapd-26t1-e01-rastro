import type { OrigemDoDado } from "../telas/tiposDaTela.ts";
import EtapaDaIdentificacao from "./EtapaDaIdentificacao.tsx";
import EtapaDaNota from "./EtapaDaNota.tsx";
import EtapaDoAviso from "./EtapaDoAviso.tsx";
import EtapaNoHar from "./EtapaNoHar.tsx";
import Icone from "../basicos/Icone.tsx";
import { usarJanelaModal } from "../hooks/usarJanelaModal.ts";
import "./PainelOrigemDoDado.css";

interface Props {
  origem: OrigemDoDado;
  aoFechar: () => void;
}

function tituloDaOrigem({ biblioteca, achados }: OrigemDoDado): string {
  const nome = `${biblioteca.pacote} ${biblioteca.versao}`;
  return achados.length === 1 ? `${nome} · ${achados[0].aviso.ghsa}` : nome;
}

export default function PainelOrigemDoDado({ origem, aoFechar }: Props) {
  const { janela, fechar, fecharAoClicarFora } = usarJanelaModal();
  return (
    <dialog
      ref={janela}
      className="painel-origem-do-dado"
      aria-labelledby="painel-origem-do-dado-titulo"
      onClose={aoFechar}
      onClick={fecharAoClicarFora}
    >
      <div className="painel-origem-do-dado__conteudo">
        <header className="painel-origem-do-dado__cabecalho">
          <div>
            <span className="painel-origem-do-dado__rotulo">Origem do dado</span>
            <h2 id="painel-origem-do-dado-titulo">{tituloDaOrigem(origem)}</h2>
          </div>
          <button type="button" className="painel-origem-do-dado__fechar" onClick={fechar} aria-label="Fechar a origem do dado">
            <Icone nome="fechar" tamanho={16} />
          </button>
        </header>
        <div className="painel-origem-do-dado__corpo">
          <EtapaNoHar biblioteca={origem.biblioteca} />
          <EtapaDaIdentificacao biblioteca={origem.biblioteca} />
          <EtapaDoAviso origem={origem} />
          <EtapaDaNota origem={origem} />
        </div>
      </div>
    </dialog>
  );
}
