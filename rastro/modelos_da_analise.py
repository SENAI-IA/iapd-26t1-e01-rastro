from dataclasses import dataclass
from datetime import datetime

from rastro.acao.modelos import Acao
from rastro.configuracao.modelos import Checagem
from rastro.explicacao.modelos import Explicacao
from rastro.fontes.modelos import FonteSemResposta
from rastro.har.visita import PassoDaVisita
from rastro.ia.cliente import ChamadaDaIA
from rastro.identificacao.modelos import Biblioteca
from rastro.risco.modelos import Achado
from rastro.travas.modelos import TravaAcionada


@dataclass(frozen=True)
class Analise:
    har: str
    site: str | None
    inicio: datetime
    duracao_s: float
    provedor_de_ia: str | None
    tem_javascript: bool
    bibliotecas: list[Biblioteca]
    a_confirmar: list[Biblioteca]
    nao_consultadas: dict[str, str]
    fontes_sem_resposta: list[FonteSemResposta]
    achados: list[Achado]
    explicacoes: dict[str, Explicacao]
    checagens: list[Checagem]
    plano_de_acao: list[Acao]
    travas_acionadas: list[TravaAcionada]
    chamadas_de_ia: list[ChamadaDaIA]
    visita: list[PassoDaVisita]
