/**
 * A caixinha de +/- da ficha, recalculada contra o que o documento publica.
 *
 * O Apps Script nao roda fora do Google, entao o aplicaPasso_ do Codigo.gs
 * mora sozinho, sem tocar em planilha nenhuma, e este arquivo o carrega e o
 * roda no node. Nenhum numero esperado esta escrito aqui: o exemplo sai do
 * manual-temporario.md, o teto sai do capitulo 1 do manual.txt, e as regras
 * saem do decisoes-ficha.json.
 *
 * node regressao-delta.js
 */
'use strict';
const fs = require('fs');
const path = require('path');
const RAIZ = __dirname;

let ok = 0;
const falhas = [];
function checa(nome, obtido, esperado) {
  const a = JSON.stringify(obtido), b = JSON.stringify(esperado);
  if (a === b) { ok++; return; }
  falhas.push(`${nome}\n      obtido:   ${a}\n      esperado: ${b}`);
}

// --- carrega o aplicaPasso_ do Codigo.gs, so ele -------------------------
function extrai(fonte, nome) {
  const i = fonte.indexOf('function ' + nome + '(');
  if (i < 0) throw new Error(`${nome} nao existe no Codigo.gs`);
  let n = 0, j = fonte.indexOf('{', i);
  const ini = j;
  for (; j < fonte.length; j++) {
    if (fonte[j] === '{') n++;
    else if (fonte[j] === '}' && --n === 0) return fonte.slice(i, j + 1);
  }
  throw new Error(`${nome} nao fecha`);
}
const GS = fs.readFileSync(path.join(RAIZ, 'apps-script', 'Codigo.gs'), 'utf8');
const aplicaPasso_ = new Function(extrai(GS, 'aplicaPasso_') +
                                  '; return aplicaPasso_;')();

// --- o que os documentos dizem ------------------------------------------
const A2 = JSON.parse(fs.readFileSync(path.join(RAIZ, 'decisoes-ficha.json'),
                                      'utf8'))['A2_temporario'];
const MAN = fs.readFileSync(path.join(RAIZ, 'manual-temporario.md'), 'utf8');

// "Kaori tem 9 de vida temporaria ... Muralha ... que da 18 ... fica com 18,
//  nao com 27" / "toma 20 de dano ... os 2 que sobram descem na vida dela"
const mTemp = MAN.match(/fica com (\d+), não com (\d+)/);
const mDano = MAN.match(/toma (\d+) de dano.*?os (\d+) que sobram/s);
if (!mTemp || !mDano) throw new Error('o exemplo do manual-temporario.md mudou de forma');
const TEMP = Number(mTemp[1]);         // 18
const SOMA = Number(mTemp[2]);         // 27, a soma que a regra proibe
const DANO = Number(mDano[1]);         // 20
const SOBRA = Number(mDano[2]);        // 2, o que desce na vida

// --- 1. o exemplo publicado, ao pe da letra -----------------------------
const MAXV = 40;                       // qualquer teto acima do exemplo
const kaori = aplicaPasso_(MAXV, MAXV, TEMP, -DANO);
checa('exemplo do manual · a temporaria vai embora inteira',
      kaori.temp, 0);
checa(`exemplo do manual · so ${SOBRA} descem na vida`,
      MAXV - kaori.atual, SOBRA);
checa('exemplo do manual · a temporaria nao virou soma',
      kaori.atual !== MAXV - DANO + (SOMA - TEMP), true);

// --- 2. a temporaria absorve tudo quando da conta -----------------------
const meio = aplicaPasso_(MAXV, MAXV, TEMP, -(TEMP - 1));
checa('dano menor que a temporaria · a reserva nao e tocada',
      meio.atual, MAXV);
checa('dano menor que a temporaria · sobra temporaria',
      meio.temp, 1);
const exato = aplicaPasso_(MAXV, MAXV, TEMP, -TEMP);
checa('dano igual a temporaria · a reserva nao e tocada', exato.atual, MAXV);
checa('dano igual a temporaria · a temporaria zera', exato.temp, 0);

// --- 3. as duas reservas que a A2 manda gastar primeiro -----------------
checa('A2 diz que a vida temporaria gasta antes da vida',
      A2.vida.gasta_antes_da_vida_normal, true);
checa('A2 diz que a energia temporaria gasta antes do PE',
      A2.energia.gasta_antes_do_pe_normal, true);

// --- 4. sem temporaria, a caixinha e a de antes -------------------------
const seca = aplicaPasso_(19, 19, 0, -9);
checa('sem temporaria · desce direto na reserva', seca.atual, 10);
checa('sem temporaria · nada a descontar', seca.temp, 0);
const vazio = aplicaPasso_(19, 19, '', -9);
checa('campo TEMP vazio vale zero', vazio, { atual: 10, temp: 0 });

// --- 5. ganho nao devolve temporaria ------------------------------------
const cura = aplicaPasso_(10, 19, 5, 4);
checa('ganho nao mexe na temporaria', cura.temp, 5);
checa('ganho sobe a reserva', cura.atual, 14);
checa('ganho nao passa do maximo', aplicaPasso_(17, 19, 0, 9).atual, 19);

// --- 6. os limites -----------------------------------------------------
checa('perda nao passa de zero', aplicaPasso_(4, 19, 0, -30).atual, 0);
checa('perda alem de zero nao deixa temporaria para tras',
      aplicaPasso_(4, 19, 3, -30).temp, 0);
checa('temporaria negativa e lida como zero',
      aplicaPasso_(19, 19, -5, -2).atual, 17);
checa('sem maximo declarado o ganho nao e preso',
      aplicaPasso_(10, 0, 0, 40).atual, 50);
checa('passo zero nao move nada', aplicaPasso_(10, 19, 5, 0), { atual: 10, temp: 5 });

// --- 7. o teto do campo TEMP, o B19 -----------------------------------
const tetoTemp_ = new Function(extrai(GS, 'tetoTemp_') + '; return tetoTemp_;')();
const CAP1 = fs.readFileSync(path.join(RAIZ, 'manual.txt'), 'utf8').split(/\s+/).join(' ');
// "com 40 de vida máxima o seu teto é 20: um efeito que daria 27 te deixa em 20"
const mTeto = CAP1.match(/com (\d+) de vida máxima o seu teto é (\d+): um efeito que daria (\d+) te deixa em (\d+)/);
// "O que você ganha desce. E o que você ganha nunca fica abaixo de 1."
const mPiso = CAP1.match(/o que você ganha nunca fica abaixo de (\d+)/);
if (!mTeto || !mPiso) throw new Error('o exemplo do teto no capitulo 1 do manual.txt mudou de forma');
const [TMAX, TETO, EFEITO, FICA] = mTeto.slice(1).map(Number);
const PISO = Number(mPiso[1]);

checa(`exemplo do manual · ${EFEITO} com maximo ${TMAX} fica em ${FICA}`,
      tetoTemp_(EFEITO, TMAX), FICA);
checa('exemplo do manual · abaixo do teto nao e mexido', tetoTemp_(TETO - 1, TMAX), TETO - 1);
checa('exemplo do manual · o proprio teto passa', tetoTemp_(TETO, TMAX), TETO);
checa('A2 poe o teto da vida em metade do maximo', /^metade /.test(A2.vida.teto), true);
checa('A2 poe o teto da energia em metade do maximo', /^metade /.test(A2.energia.teto), true);
checa('o manual arredonda para baixo o que voce ganha', CAP1.includes('O que você ganha desce.'), true);

const outro = TMAX - 1;                // um maximo com a paridade trocada
const tOutro = tetoTemp_(outro, outro);
checa(`maximo ${outro} · o teto nao passa da metade`, 2 * tOutro <= outro, true);
checa(`maximo ${outro} · o teto e o maior inteiro que nao passa`, 2 * (tOutro + 1) > outro, true);
checa(`maximo 1 · o teto nao cai abaixo de ${PISO}`, tetoTemp_(TMAX, 1), PISO);
checa('campo TEMP vazio continua vazio', tetoTemp_('', TMAX), '');
checa('temporaria negativa digitada vira zero', tetoTemp_(-3, TMAX), 0);
checa('sem maximo declarado nao ha teto', tetoTemp_(EFEITO, 0), EFEITO);
checa('texto que nao e numero nao e mexido', tetoTemp_('x', TMAX), 'x');

// --- as perícias fixas do Caminho, 17/09/2026 ----------------------------
// A tabela sai do catálogo, que o conferir-catalogo.py confere contra o livro. O que se prova: o Caminho
// novo marca as fixas dele, o de antes desmarca as suas, e uma perícia que os dois fixam não é
// desmarcada.
const periciasDoCaminho_ = new Function(extrai(GS, 'periciasDoCaminho_') +
                                        '; return periciasDoCaminho_;')();
const CATA = JSON.parse(fs.readFileSync(path.join(RAIZ, 'catalogo-projeto-m.json'), 'utf8'));
const TAB = Object.entries(CATA.caminhos).map(([c, v]) => ({ caminho: c, pericias: v.pericias_fixas }));
const [c1, c2] = Object.keys(CATA.caminhos);
checa(`escolher ${c1} do zero marca as fixas dele`,
      periciasDoCaminho_(TAB, c1, undefined), { marcar: CATA.caminhos[c1].pericias_fixas, desmarcar: [] });
checa(`trocar ${c1} por ${c2} desmarca as de ${c1}`,
      periciasDoCaminho_(TAB, c2, c1), { marcar: CATA.caminhos[c2].pericias_fixas, desmarcar: CATA.caminhos[c1].pericias_fixas });
checa('apagar o Caminho so desmarca', periciasDoCaminho_(TAB, '', c1).marcar, []);
const TAB2 = [{ caminho: 'A', pericias: ['X', 'Y'] }, { caminho: 'B', pericias: ['Y', 'Z'] }];
checa('a perícia fixa nos dois Caminhos continua marcada', periciasDoCaminho_(TAB2, 'B', 'A'), { marcar: ['Y', 'Z'], desmarcar: ['X'] });
checa('um Caminho que não está na tabela não marca nada', periciasDoCaminho_(TAB, 'Nenhum', c1).marcar, []);

// --- a Trilha que não é do Caminho novo, 17/09/2026 ----------------------
// As Trilhas saem do catálogo, e o texto de escolha sai do ficha_automatica.py, que o põe na ficha.
const trilhaQueFica_ = new Function(extrai(GS, 'trilhaQueFica_') + '; return trilhaQueFica_;')();
const PY = fs.readFileSync(path.join(RAIZ, 'ficha-v01', 'ficha_automatica.py'), 'utf8');
const mVazio = PY.match(/^ESCOLHA_TRILHA = "([^"]+)"/m);
if (!mVazio) throw new Error('o ESCOLHA_TRILHA do ficha_automatica.py mudou de forma');
const VAZIO = mVazio[1];
const TRI = Object.entries(CATA.trilhas).map(([t, c]) => ({ trilha: t, caminho: c }));
const tDe = c => TRI.filter(l => l.caminho === c).map(l => l.trilha);
const [t1] = tDe(c1), [t2] = tDe(c2);
checa(`${t1} fica quando o Caminho é ${c1}`, trilhaQueFica_(TRI, c1, t1, VAZIO), t1);
checa(`${t1} volta para "${VAZIO}" quando o Caminho vira ${c2}`, trilhaQueFica_(TRI, c2, t1, VAZIO), VAZIO);
checa(`${t2} fica quando o Caminho vira ${c2}`, trilhaQueFica_(TRI, c2, t2, VAZIO), t2);
checa('apagar o Caminho devolve a Trilha para o texto de escolha', trilhaQueFica_(TRI, '', t1, VAZIO), VAZIO);
checa('a Trilha ainda não escolhida não é mexida', trilhaQueFica_(TRI, c2, VAZIO, VAZIO), VAZIO);
checa('a Trilha vazia não vira texto de escolha', trilhaQueFica_(TRI, c2, '', VAZIO), '');
checa('toda Trilha do catálogo fica no próprio Caminho',
      TRI.every(l => trilhaQueFica_(TRI, l.caminho, l.trilha, VAZIO) === l.trilha), true);

// --- onde a nota mora, 17/09/2026 ----------------------------------------
const tituloOuCaixa_ = new Function(extrai(GS, 'tituloOuCaixa_') + '; return tituloOuCaixa_;')();
checa('rótulo digitado em cima leva a nota', tituloOuCaixa_({ formula: '', valor: 'DEFESA' }), 'título');
checa('fórmula em cima deixa a nota na caixa', tituloOuCaixa_({ formula: '=IF(A1,"x","y")', valor: 'x' }), 'caixa');
checa('nada em cima deixa a nota na caixa', tituloOuCaixa_({ formula: '', valor: '' }), 'caixa');
checa('só espaço em cima deixa a nota na caixa', tituloOuCaixa_({ formula: '', valor: '  ' }), 'caixa');
checa('número em cima deixa a nota na caixa', tituloOuCaixa_({ formula: '', valor: 5 }), 'caixa');

// --- resultado ---------------------------------------------------------
const barra = '='.repeat(74);
console.log('');
console.log(barra);
if (falhas.length) {
  console.log(`>>> ${falhas.length} FALHA(S) de ${ok + falhas.length} checagens\n`);
  falhas.forEach(f => console.log('  · ' + f));
  console.log(barra);
  process.exit(1);
}
console.log(`>>> TUDO OK — as ${ok} checagens saem do exemplo do`);
console.log('    manual-temporario.md, do capitulo 1 do manual.txt e da A2 do decisoes-ficha.json.');
console.log(barra);
