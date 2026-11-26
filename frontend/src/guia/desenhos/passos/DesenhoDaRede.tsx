import Janela from "../pecas/Janela.tsx";

export default function DesenhoDaRede() {
  return (
    <Janela tamanho="grande">
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="52" x2="180" y2="52" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="66" x2="140" y2="66" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="24" y1="80" x2="160" y2="80" />
      <line className="ilustracao-do-guia__traco" x1="8" y1="98" x2="312" y2="98" />
      <text className="ilustracao-do-guia__texto" x="20" y="116">
        Elementos
      </text>
      <text className="ilustracao-do-guia__texto" x="84" y="116">
        Console
      </text>
      <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--destaque ilustracao-do-guia__texto--forte" x="140" y="116">
        Rede
      </text>
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" x1="138" y1="122" x2="166" y2="122" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="20" y1="140" x2="290" y2="140" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="20" y1="154" x2="250" y2="154" />
      <line className="ilustracao-do-guia__traco ilustracao-do-guia__traco--suave" x1="20" y1="168" x2="270" y2="168" />
      <g className="ilustracao-do-guia__tecla">
        <rect className="ilustracao-do-guia__traco ilustracao-do-guia__traco--destaque" x="246" y="46" width="50" height="28" rx="3" />
        <text className="ilustracao-do-guia__texto ilustracao-do-guia__texto--destaque ilustracao-do-guia__texto--forte" x="260" y="64.5">
          F12
        </text>
      </g>
    </Janela>
  );
}
