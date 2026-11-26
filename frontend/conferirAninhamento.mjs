import path from "node:path";
import { fileURLToPath } from "node:url";
import { API } from "typescript/unstable/sync";
import { SyntaxKind } from "typescript/unstable/ast";

const LIMITE_DE_NIVEIS = 2;
const PASTA_DO_FRONTEND = path.dirname(fileURLToPath(import.meta.url));
const PASTA_DO_CODIGO = path.join(PASTA_DO_FRONTEND, "src") + path.sep;
const CONFIGURACAO_DO_PROJETO = path.join(PASTA_DO_FRONTEND, "tsconfig.app.json");

const BLOCOS_QUE_CONTAM_COMO_NIVEL = new Set([
  SyntaxKind.IfStatement,
  SyntaxKind.ForStatement,
  SyntaxKind.ForOfStatement,
  SyntaxKind.ForInStatement,
  SyntaxKind.WhileStatement,
  SyntaxKind.DoStatement,
  SyntaxKind.SwitchStatement,
  SyntaxKind.TryStatement,
]);

const FUNCOES = new Set([
  SyntaxKind.FunctionDeclaration,
  SyntaxKind.FunctionExpression,
  SyntaxKind.ArrowFunction,
  SyntaxKind.MethodDeclaration,
  SyntaxKind.GetAccessor,
  SyntaxKind.SetAccessor,
  SyntaxKind.Constructor,
]);

const METODOS_DE_LACO = new Set(["forEach", "map", "filter", "reduce", "some", "every", "find"]);

function nomeDoMetodoChamado(chamada) {
  const chamado = chamada.expression;
  if (chamado.kind !== SyntaxKind.PropertyAccessExpression) return undefined;
  return chamado.name.text;
}

function noECallbackDeLaco(funcao) {
  const chamada = funcao.parent;
  if (chamada.kind !== SyntaxKind.CallExpression) return false;
  if (!chamada.arguments.includes(funcao)) return false;
  return METODOS_DE_LACO.has(nomeDoMetodoChamado(chamada));
}

function noEElseIf(no) {
  const pai = no.parent;
  return no.kind === SyntaxKind.IfStatement && pai.kind === SyntaxKind.IfStatement && pai.elseStatement === no;
}

function somaUmNivel(no) {
  if (noEElseIf(no)) return false;
  if (BLOCOS_QUE_CONTAM_COMO_NIVEL.has(no.kind)) return true;
  return FUNCOES.has(no.kind) && noECallbackDeLaco(no);
}

function nomeDaFuncao(funcao) {
  if (funcao.name) return funcao.name.text;
  const pai = funcao.parent;
  if (pai.kind === SyntaxKind.VariableDeclaration || pai.kind === SyntaxKind.PropertyAssignment) return pai.name.text;
  if (pai.kind === SyntaxKind.CallExpression) return `callback de ${pai.expression.getText()}`;
  return "função sem nome";
}

function medirFuncao(funcao, arquivo, funcoesMedidas) {
  const medida = { funcao, arquivo, maiorNivel: 0 };
  funcoesMedidas.push(medida);
  funcao.forEachChild((filho) => percorrer(filho, 0, medida, arquivo, funcoesMedidas));
}

function percorrer(no, nivel, medida, arquivo, funcoesMedidas) {
  const comecaFuncaoNova = FUNCOES.has(no.kind) && !noECallbackDeLaco(no);
  if (comecaFuncaoNova) return medirFuncao(no, arquivo, funcoesMedidas);
  const nivelAqui = somaUmNivel(no) ? nivel + 1 : nivel;
  medida.maiorNivel = Math.max(medida.maiorNivel, nivelAqui);
  no.forEachChild((filho) => percorrer(filho, nivelAqui, medida, arquivo, funcoesMedidas));
}

function medirArquivo(arquivo) {
  const funcoesMedidas = [];
  const medidaDoTopo = { funcao: arquivo, arquivo, maiorNivel: 0 };
  arquivo.forEachChild((filho) => percorrer(filho, 0, medidaDoTopo, arquivo, funcoesMedidas));
  return funcoesMedidas;
}

function descreverExcesso({ funcao, arquivo, maiorNivel }) {
  const linha = arquivo.getLineAndCharacterOfPosition(funcao.getStart(arquivo)).line + 1;
  const caminho = path.relative(PASTA_DO_FRONTEND, arquivo.fileName);
  return `${caminho}:${linha} ${nomeDaFuncao(funcao)} (${maiorNivel} níveis)`;
}

function arquivosDoCodigo(projeto) {
  return projeto.rootFiles
    .filter((nome) => nome.startsWith(PASTA_DO_CODIGO))
    .filter((nome) => /\.tsx?$/.test(nome))
    .map((nome) => projeto.program.getSourceFile(nome));
}

function conferir() {
  const api = new API({ cwd: PASTA_DO_FRONTEND });
  const projeto = api.updateSnapshot({ openProjects: [CONFIGURACAO_DO_PROJETO] }).getProject(CONFIGURACAO_DO_PROJETO);
  const excessos = arquivosDoCodigo(projeto)
    .flatMap(medirArquivo)
    .filter((medida) => medida.maiorNivel > LIMITE_DE_NIVEIS)
    .map(descreverExcesso);
  api.close();
  if (excessos.length === 0) return 0;
  console.error(`Funções com mais de ${LIMITE_DE_NIVEIS} níveis de bloco aninhado:`);
  excessos.forEach((excesso) => console.error(`  ${excesso}`));
  return 1;
}

process.exitCode = conferir();
