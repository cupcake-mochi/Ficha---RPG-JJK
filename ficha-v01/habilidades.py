# -*- coding: utf-8 -*-
"""As Habilidades: a seção 7 da FICHA deixa de ser "Anotações" e vira cartas, uma por degrau de Caminho e uma por
entrega de Trilha. É a limpeza 27 (B34).

O desenho foi fechado com o Mizuki por estudo em 02/10/2026 (mockup/habilidades-estudo.html):
  · a forma C, as cartas, na linguagem do menu rápido ("Vai a C mesmo"): um bloco para o Caminho (cinco cartas e uma de
    anotação) e um para a Trilha (quatro cartas, as escolhas da Trilha e uma de anotação), três por fileira;
  · escrita à mão por enquanto ("nem precisa de automação AINDA (deixar preparado é o ideal), ja q o livro está sendo
    reescrito"): o jogador escreve o nome e o resumo de cada habilidade, e a forma já é a do livro, com o nível de cada
    carta fixo, para que o nome e o texto possam vir de lá depois sem refazer a seção;
  · a carta acima do nível do personagem avisa quando abre, e o que estiver escrito nela fica riscado até lá ("A e o
    texto fica 'riscado' (esqueci o nome), até desbloquear"). O aviso fica na etiqueta do nível, porque o nome é onde o
    jogador escreve: "Nível 15" quando já abriu, "Abre no 15" quando não. O riscado é regra de cor da FICHA (o
    corDeEstado_ do Codigo.gs lê a lista `condicional_gs` que este módulo declara), e só risca: não muda cor, para não
    brigar com a troca de paleta.

Os níveis vêm da tabela "Entregas por nível" do capítulo 35 (cinco degraus de Caminho nos níveis 2, 7, 15, 23 e 30;
quatro entregas de Trilha nos níveis 2, 11, 19 e 27), e são os mesmos para todos os Caminhos.

05/10/2026, a opção B do estudo de medida (o texto inteiro não cabe: 4 das 109 cartas): a carta traz o nome e o resumo
do livro, e o texto inteiro fica na nota da caixa do texto ("B - mas dando permissão para o jogador apagar o texto e
colocar oq preferir"). Quem escreve é o Codigo.gs (habilidadesDaFicha_), quando o Caminho ou a Trilha mudam: valor
solto, não fórmula, para o jogador poder apagar e escrever por cima, e a carta que o jogador mudou fica como está. Este
módulo publica na DADOS_AM o endereço do nome e do texto de cada carta (ADDRESS, que anda com a planilha), e escreve o
apps-script/Habilidades.gs, com o texto do livro (habilidades-do-livro.json, do extrair_habilidades.py). O texto mora
num arquivo de script próprio, e não na DADOS_AM, porque são 200 KB: o Ficha.gs passaria do teto de 900 KB que o
conferir-ficha-xlsx guarda (o Apps Script engasga perto de 1 MB por arquivo), e a montagem, que já beira os seis
minutos, escreveria 111 células de texto longo a mais. O nome ganha duas linhas (42 px),
pedido dele no mesmo dia; a rota do Batedor se escolhe no menu de Trilha (ficha_automatica.trilhas_do_menu), e a Rajada
Marcial do Pugilista vai na carta do nível 7 do Caminho ("o nv7 seria do caminho mesmo").

A seção cresce, e o menu rápido (limpeza 26) começa onde ela termina: o monta.py passa ao menu_rapido.trocas a linha
nova e as células desta seção, para ele não apagar nenhuma. A arte de respingos que morava no canto direito da seção
(ficha-2.png) muda para o lado direito do título, onde as cartas não chegam.
"""
import json, os, re
import indice_ficha as ix
import ficha_amaldicoada as fa
import menu_rapido as mr
import extrair_habilidades as xh

NOME = "FICHA"
DA = fa.DA
NIV_CAMINHO, NIV_TRILHA = (2, 7, 15, 23, 30), (2, 11, 19, 27)
POR, W, X = mr.POR, mr.W, mr.X                # as cartas do menu rápido: três por fileira, 13 colunas
C1, CN = mr.C1, mr.CN
TAG, TX = 3, 6                                # a etiqueta do nível tem 3 colunas ("Abre no 15"); o texto, 6 linhas
ARTE = "ficha-2.png"
ALT_NOME = 31.5                               # a linha do nome: duas linhas de 15,75 pt (42 px), para o nome do livro caber
ESTILOS = {**mr.ESTILOS,
           "tag": [["Oswald", 10.0, mr.fp.OSSO, False, False], mr.fp.ACENTO, mr.fp._CAIXA, ["center", "center", False, 0], None],
           "nm2": [["Castoro", 11.0, mr.fp.OSSO, False, False], mr.fp.ACENTO, mr.fp._CAIXA, ["left", "center", True, 0], None]}
FONTE_CAMINHO, FONTE_TRILHA, FONTE_JUNTO = "Caminho", "Trilha", "Caminho com a Trilha"


def livro():
    """o habilidades-do-livro.json, que o extrair_habilidades.py lê do manual.txt"""
    return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "habilidades-do-livro.json"), encoding="utf-8"))


def linhas_do_livro(HAB=None, CAT=None):
    """a tabela que o Codigo.gs lê para escrever as cartas: [dono, fonte, nível, nome na carta, resumo, texto]. A entrega
    de Trilha que mora na carta do Caminho (o nível 7 do Pugilista) entra como "Caminho com a Trilha", já junta com a
    habilidade do Caminho daquele nível: o nome dos dois, o resumo do Caminho e a primeira frase da Trilha, e os dois
    textos inteiros na nota"""
    HAB = HAB or livro()
    if CAT is None:
        CAT = json.load(open(os.path.join(fa.RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    out = [[d, FONTE_CAMINHO, int(n), h["nome_na_carta"], h["resumo"], h["texto"]]
           for d, por in HAB["caminhos"].items() for n, h in por.items()]
    out += [[d, FONTE_TRILHA, int(n), h["nome_na_carta"], h["resumo"], h["texto"]]
            for d, por in HAB["trilhas"].items() for n, h in por.items()]
    for t, por in HAB["no_caminho"].items():
        cam = CAT["trilhas"][t.split(" · ")[0]]
        for n, h in por.items():
            base, curto = HAB["caminhos"][cam][n], re.split(r", | e ", h["nome"])[0]
            frase = re.match(r".+?[.:](?= |\n|$)", h["resumo"], re.S).group(0)
            out.append([t, FONTE_JUNTO, int(n), xh.nome_na_carta(f"{base['nome']} · {curto}"),
                        f"{base['resumo']}\n{curto}: {frase}",
                        f"{base['texto']}\n\n{t.upper()} · {h['nome']}\n{h['texto']}"])
    return out


class _Folha(mr._Folha):
    def estilo(self, nome):
        import json
        if nome not in self._e:
            novo = json.loads(json.dumps(ESTILOS[nome]))
            chave = json.dumps(novo, ensure_ascii=False, sort_keys=True)
            achou = next((i for i, e in enumerate(self.layout["estilos"]) if json.dumps(e, ensure_ascii=False, sort_keys=True) == chave), None)
            if achou is None:
                self.layout["estilos"].append(novo)
                achou = len(self.layout["estilos"]) - 1
            self._e[nome] = achou
        return self._e[nome]


def arte_no_titulo(im, r7):
    """a arte de respingos ao lado do título da seção: três colunas (AQ a AS), nas três primeiras linhas da seção"""
    return dict(im, col=CN - 3, lin=r7, larg=3 * 28, alt=27 + 2 * 21, desloc_x=0, desloc_y=0)


def linha_do_titulo(ficha, n):
    """a linha do número de uma seção da FICHA (o 7 ou o 8, na coluna D)"""
    return next(ix._lc(r[0])[0] for r in ficha["celulas"] if ix._lc(r[0])[1] == C1 and r[1] in (n, float(n), str(n)))


def cartas():
    """as nove cartas de habilidade, na ordem do bloco: [(fonte, nível)]"""
    return [("Caminho", n) for n in NIV_CAMINHO] + [("Trilha", n) for n in NIV_TRILHA]


def escreve_gs(destino, linhas=None):
    """o apps-script/Habilidades.gs: a lista do livro que o habilidadesDaFicha_ do Codigo.gs lê. Gerado; não se edita"""
    linhas = linhas if linhas is not None else linhas_do_livro()
    chaves = ("dono", "fonte", "nivel", "nome", "resumo", "texto")
    corpo = ",\n".join("  " + json.dumps(dict(zip(chaves, l)), ensure_ascii=False) for l in linhas)
    txt = ("/**\n * GERADO pelo ficha-v01/monta.py (habilidades.escreve_gs), do ficha-v01/habilidades-do-livro.json, que o\n"
           " * extrair_habilidades.py lê do manual.txt. Não edite à mão: rode o monta.py.\n *\n"
           " * As habilidades de cada Caminho e de cada Trilha, para as cartas da seção 7 da FICHA. O habilidadesDaFicha_,\n"
           " * no Codigo.gs, escreve o nome e o resumo na carta e o texto na nota. Fonte \"Caminho com a Trilha\" é a entrega\n"
           " * de Trilha que mora na carta do Caminho (o nível 7 do Pugilista).\n */\n"
           f"var HABILIDADES_DO_LIVRO_ = [\n{corpo}\n];\n")
    open(destino, "w", encoding="utf-8").write(txt)
    return len(linhas), len(txt)


def trocas(layout, tr):
    """o que a limpeza muda na FICHA e na DADOS_AM. Lê a FICHA depois das limpezas de cima, e a DADOS_AM das trocas
    da Ficha Amaldiçoada (tr), que ainda não entrou no layout"""
    ficha = ix._aba(layout, NOME)
    fcel = {r[0]: r for r in ficha["celulas"]}
    r7, r8 = linha_do_titulo(ficha, 7), linha_do_titulo(ficha, 8)
    num_est, tit_est, fundo = fcel[f"D{r7}"][2], fcel[f"G{r7}"][2], fcel[f"C{r7 + 2}"][2]
    tit_fim = next(ix._lc(m.split(":")[1])[1] for m in ficha["mescladas"] if m.split(":")[0] == f"G{r7}")
    idx = ix.indice(layout)
    D, H = tr["D"], tr["H"]
    NIV = H["nível"].replace(DA, "")
    F_ = lambda k: fa._A(idx[k], "FICHA!")

    # --- a DADOS_AM: a etiqueta de cada carta pelo nível da FICHA, e o título de cada bloco pelo Caminho e pela Trilha
    lista = cartas()
    cH = D.tabela("habilidades", ["habilidade: carta", "nível da carta", "etiqueta da carta", "célula do nome", "célula do texto"],
                  [[f"{fonte} {n}", n, f'=IF({NIV}>={n},"Nível {n}","Abre no {n}")', None, None] for fonte, n in lista])
    escolha = lambda k: f'IF(OR({F_(k)}="",LEFT({F_(k)},7)="Escolha"),"","  ·  "&UPPER({F_(k)}))'
    cT = D.tabela("habilidades_titulos", ["habilidades: título", "texto do título"],
                  [["Caminho", f'="CAMINHO"&{escolha("caminho")}&"  ·  CINCO DEGRAUS"'],
                   ["Trilha", f'="TRILHA"&{escolha("trilha")}&"  ·  QUATRO ENTREGAS"']])
    etiqueta = lambda i: f"={DA}${fa.L(cH + 2)}${2 + i}"
    titulo = lambda i: f"={DA}${fa.L(cT + 1)}${2 + i}"

    # --- a seção na FICHA
    f = _Folha(layout)
    grupos, riscar, pos, alt_nome = [], [], {}, set()
    f.cel[f"D{r7}"] = (7, num_est)
    f.mesclas.append(f"D{r7}:F{r7 + 1}")
    f.cel[f"G{r7}"] = ("HABILIDADES", tit_est)
    f.mesclas.append(f"G{r7}:{fa.L(tit_fim)}{r7}")
    r = r7 + 3
    a_secao = r

    def carta(r, x, i):
        """a carta de uma habilidade: a etiqueta do nível, o nome e o texto, que o Codigo.gs escreve do livro e o
        jogador pode trocar"""
        tag = f.add("tag", x, r, x + TAG - 1, r, etiqueta(i))
        nome = f.add("nm2", x + TAG, r, x + W - 1, r, None)
        texto = f.add("desc", x, r + 1, x + W - 1, r + TX, None)
        pos[i] = (nome, texto)
        alt_nome.add(r)
        riscar.append({"faixas": [f"{nome}:{fa._a1(x + W - 1, r)}", f"{texto}:{fa._a1(x + W - 1, r + TX)}"],
                       "formula": f'=LEFT(${fa.L(x)}${r},4)="Abre"', "riscado": True})

    def livre(r, x, rotulo):
        f.add("cab", x, r, x + W - 1, r, rotulo)
        f.add("desc", x, r + 1, x + W - 1, r + TX, None)

    cheias = []
    def bloco(id_, i_titulo, itens):
        nonlocal r
        cab = r
        f.add("cab", C1, cab, CN, cab, titulo(i_titulo))
        r = cab + 1
        fil = -(-len(itens) // POR)
        for fi in range(fil):
            fileira = itens[fi * POR:(fi + 1) * POR]
            for j, it in enumerate(fileira):
                if isinstance(it, int):
                    carta(r, X[j], it)
                else:
                    livre(r, X[j], it)
            if all(isinstance(it, int) for it in fileira) and len(fileira) == POR:
                cheias.append(r)
            # o texto da fileira é um grupo; o + fica na linha das etiquetas, e só a primeira fileira nasce aberta
            grupos.append([r + 1, r + TX, fi > 0])
            r += 1 + TX
            if fi + 1 < fil:
                r += 1
        r += 1
        grupos.append([cab + 1, r - 1, False])

    nc = len(NIV_CAMINHO)
    bloco("caminho", 0, list(range(nc)) + ["Anotações"])
    bloco("trilha", 1, list(range(nc, len(lista))) + ["Escolhas da Trilha", "Anotações"])
    fim = r
    grupos.append([a_secao, fim - 1, False])
    for i, (cn, ct) in pos.items():
        D.poe(cH + 3, 2 + i, ix.FORMULA.format(c=cn))
        D.poe(cH + 4, 2 + i, ix.FORMULA.format(c=ct))
    prof = lambda g: sum(1 for o in grupos if o[0] <= g[0] and g[1] <= o[1])
    for a_ in grupos:
        for b_ in grupos:
            if a_ is not b_ and b_[0] == a_[1] + 1 and prof(a_) == prof(b_):
                raise SystemExit(f"habilidades: os grupos {a_[:2]} e {b_[:2]} estao colados")

    # a arte de respingos, ao lado do título: três colunas, as três primeiras linhas da seção
    arte = None
    for im in ficha.get("imagens", []):
        if im["arquivo"] == ARTE:
            arte = arte_no_titulo(im, r7)

    # o fundo das células vazias da seção, como o resto da FICHA
    dentro = set()
    for m in f.mesclas:
        (l1, c1), (l2, c2) = (ix._lc(x) for x in m.split(":"))
        dentro |= {(l, c) for l in range(l1, l2 + 1) for c in range(c1, c2 + 1)}
    dentro |= {ix._lc(c) for c in f.cel}
    for l in range(r7, fim):
        for c in range(3, ficha["colunas"]):
            if (l, c) not in dentro:
                f.cel[fa._a1(c, l)] = (None, fundo)

    # o que sai: a seção 7 de hoje (as caixas, as mesclagens, as alturas e a mesclagem da arte)
    no_velho = lambda c: r7 <= ix._lc(c)[0] < r8 and ix._lc(c)[1] >= 3
    sai = {c for c in fcel if no_velho(c)} - set(f.cel)
    mesc_sai = [m for m in ficha["mescladas"] if no_velho(m.split(":")[0])]
    copias = [[cheias[0], cheias[0] + TX, cheias[1:], C1, CN]] if len(cheias) > 1 else []
    return {"r7": r7, "r8_velho": r8, "fim": fim, "celulas": {NOME: {c: (v[0], c) for c, v in f.cel.items()}},
            "_estilos": f.cel, "sai": sai, "mescladas_sai": {NOME: mesc_sai}, "mescladas": {NOME: f.mesclas},
            "grupos": grupos, "riscar": riscar, "arte": arte, "copias": copias, "cartas": lista,
            "tabela": cH, "titulos": cT, "alt_nome": sorted(alt_nome)}


def aplica(layout, tm):
    """põe a seção na FICHA. Devolve quantas células mudaram. Roda antes do menu_rapido.aplica"""
    ficha = ix._aba(layout, NOME)
    ficha["celulas"] = [c for c in ficha["celulas"] if c[0] not in tm["sai"]]
    por = {c[0]: c for c in ficha["celulas"]}
    n = 0
    for coord, (v, est) in tm["_estilos"].items():
        if coord in por:
            por[coord][1], por[coord][2] = v, est
        else:
            ficha["celulas"].append([coord, v, est])
        n += 1
    ficha["mescladas"] = [m for m in ficha["mescladas"] if m not in tm["mescladas_sai"][NOME]] + tm["mescladas"][NOME]
    # as alturas: o título da seção fica com a do título, e as linhas finas de hoje (5,25) saem; as que estão depois da
    # seção nova são da seção 8 de hoje, e o menu rápido cuida delas
    ficha["linhas_alt"] = ([a for a in ficha["linhas_alt"] if a[0] < tm["r7"]] + [[tm["r7"], 27.0]] +
                           [[r, ALT_NOME] for r in tm["alt_nome"]] +
                           [a for a in ficha["linhas_alt"] if a[0] >= tm["fim"]])
    ficha["grupos"] = {"linhas": (ficha.get("grupos") or {}).get("linhas", []) + tm["grupos"], "colunas": []}
    # as etiquetas e os títulos são conta: ficam fora da trava (moram em linha de grupo), e o onEdit devolve a conta
    ficha["sem_trava"] = ficha.get("sem_trava", []) + [[tm["r7"], tm["fim"] - 1]]
    ficha["condicional_gs"] = ficha.get("condicional_gs", []) + tm["riscar"]
    ficha["copias"] = ficha.get("copias", []) + tm["copias"]
    if tm["arte"]:
        ficha["imagens"] = [tm["arte"] if im["arquivo"] == ARTE else im for im in ficha["imagens"]]
    return n
