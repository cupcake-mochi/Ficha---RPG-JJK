# -*- coding: utf-8 -*-
"""Lê do livro as habilidades de cada Caminho e de cada Trilha, e grava em ficha-v01/habilidades-do-livro.json.

    python3 ficha-v01/extrair_habilidades.py            # lê o manual.txt e regrava o arquivo
    python3 ficha-v01/extrair_habilidades.py --confere  # só compara o arquivo com o manual.txt, sem gravar

Por que este arquivo existe: a seção 7 da FICHA (as cartas de Habilidades, B34) nasceu escrita à mão, com a forma já
pronta para o livro. Em 05/10/2026 o Mizuki escolheu que a carta traga o livro e que o jogador possa apagar e escrever o
que preferir ("B - mas dando permissão para o jogador apagar o texto e colocar oq preferir"), e no mesmo dia pôs as
cartas numa coluna só, com a caixa do texto esticando conforme a escolha ("Acompanha a Escolha, mas ainda tendo a caixa
retratil da descrição"): a carta traz o nome e o texto inteiro.

De onde sai cada coisa, sem nada digitado:
  · os níveis e os nomes, da tabela de progressão de cada Caminho e de cada Trilha ("Nível | Habilidade"); as Trilhas
    do Guia não têm tabela, e o nome sai do título "Nível N — Nome", ou do título logo acima do parágrafo "Nível N.";
  · as rotas, dos títulos "Trilha: rota" (o Batedor tem três, e o livro manda escolher uma no nível 2). Cada rota é uma
    entrada do menu de Trilha ("Batedor · Yumi"), pedido do Mizuki em 05/10/2026;
  · as marcas de cada habilidade são o parágrafo "Nível N:", "Nível N." ou "Nível N ·", o título "Nível N — Nome", um
    título com "nível N", e a primeira vez que o nome dela abre um título ou um parágrafo. Cada marca abre um trecho, que
    vai até a marca seguinte, e o trecho é da habilidade dona da marca: o livro nem sempre segue a ordem dos níveis (o
    Pugilista põe a Rajada Marcial, do nível 7, entre o Corpo Treinado e o Quebrar o Compasso, do nível 2);
  · o texto são os parágrafos, os subtítulos, as fileiras de tabela e os itens de lista dos trechos, sem os exemplos,
    sem as marcas "Nível N." soltas e sem a marca "Nível N:" do começo do parágrafo. Ele vem legível ("n esqueça de
    tentar deixar de forma legivel, espaçar os paragrafos e talz"): uma linha em branco entre os blocos, a tabela e a
    lista inteiras, e os subtítulos à parte, em `titulos`, que o Codigo.gs põe em negrito.
  · uma entrega de Trilha num nível que não é de Trilha (o nível 7 do Pugilista, a Rajada Marcial) vai para
    `no_caminho`: o livro diz que ela "Não acrescenta um novo degrau de Trilha no nível 7", e o Mizuki a pôs na carta
    do nível 7 do Caminho ("No caso do pungilista, o nv7 seria do caminho mesmo").

O --confere refaz tudo e compara; e cada parágrafo e cada nome gravados têm de estar no manual.
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)
import livro as Lv

SAIDA = os.path.join(AQUI, "habilidades-do-livro.json")
CAPITULO = "## 6. Caminhos e Trilhas"
NIV_CAMINHO, NIV_TRILHA = (2, 7, 15, 23, 30), (2, 11, 19, 27)
SEP_ROTA = " · "


def _sem_ponto(s):
    return s.strip().rstrip(".").strip()


def _nomes(s):
    """"Ataque Extra, Nem Um Arranhão e Ainda de Pé" -> as três"""
    return [x for x in (_sem_ponto(p) for p in re.split(r",|;| e |: ", s)) if x]


def extrai():
    L = Lv.linhas(os.path.join(RAIZ, "manual.txt"))
    CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    ini_cap = L.index(CAPITULO)
    fim_cap = next(i for i in range(ini_cap + 1, len(L)) if L[i].startswith("## "))
    titulos = {L[i][4:]: i for i in range(ini_cap, fim_cap) if L[i].startswith("### ")}

    # os donos: os Caminhos, e as Trilhas com as rotas abertas
    rotas = {t: [h[len(t) + 2:] for h in titulos if h.startswith(t + ": ")] for t in CAT["trilhas"]}
    rotas = {t: r for t, r in rotas.items() if r}
    donos = {c: ("caminho", c) for c in CAT["caminhos"]}
    for t in CAT["trilhas"]:
        for r in rotas.get(t, [None]):
            donos[t + SEP_ROTA + r if r else t] = ("trilha", f"{t}: {r}" if r else t)
    faltam = [d for d, (_, h) in donos.items() if h not in titulos]
    if faltam:
        raise SystemExit(f"sem título no capítulo 6: {faltam}")
    inicio = {d: titulos[h] for d, (_, h) in donos.items()}
    marcos = sorted(inicio.values()) + [fim_cap]
    fim = {d: next(x for x in marcos if x > i) for d, i in inicio.items()}

    def tabela(d):
        """[(nível, nome)] da tabela de progressão; as rotas leem a coluna delas na tabela da primeira rota"""
        t, r = (d.split(SEP_ROTA) + [None])[:2]
        a, b = (inicio[t + SEP_ROTA + rotas[t][0]], fim[t + SEP_ROTA + rotas[t][0]]) if r else (inicio[d], fim[d])
        for i in range(a, b):
            if L[i].startswith("Nível | "):
                cab = L[i].split(" | ")
                col = cab.index(r) if r else 1
                out, k = [], i + 1
                while k < b and " | " in L[k]:
                    f = L[k].split(" | ")
                    out.append((int(f[0]), _sem_ponto(f[col])))
                    k += 1
                return out
        return None

    def sem_tabela(d):
        """as Trilhas do Guia: "#### Nível N — Nome", ou "Nível N." logo abaixo do título que lhe dá nome"""
        out = []
        for i in range(inicio[d], fim[d]):
            m = re.match(r"^(?:#### )?Nível (\d+)(?: — (.+)|\.(?: |$))", L[i])
            if not m:
                continue
            if m.group(2):
                out.append((int(m.group(1)), _sem_ponto(m.group(2))))
            else:
                tit = next(L[j] for j in range(i - 1, i - 4, -1) if L[j].startswith("#"))
                out.append((int(m.group(1)), tit.lstrip("#").strip()))
        return out

    def marcas(d, n, nome):
        """as linhas que abrem um trecho desta habilidade: "Nível N" (parágrafo ou título), título com "nível N", título
        com o nome, ou parágrafo que abre pelo nome. Cada nome conta a primeira vez que aparece"""
        nomes = [x.lower() for x in _nomes(nome)] + [nome.lower()]
        out, achados = set(), set()
        for i in range(inicio[d] + 1, fim[d]):
            l = L[i]
            if re.match(rf"^(?:#### )?Nível {n}(?: —|[.:·](?: |$))", l):
                out.add(i)
            elif l.startswith("#"):
                t = _sem_ponto(l.lstrip("#").strip()).lower()
                if re.search(rf"\bnível {n}\b", t):
                    out.add(i)
                elif t in nomes and t not in achados:
                    out.add(i); achados.add(t)
            else:
                x = next((x for x in nomes if l.lower().startswith(x + ". ") or l.lower().startswith(x + ": ")), None)
                if x and x not in achados:
                    out.add(i); achados.add(x)
        return out

    def bloco(l, n, nome):
        """(tipo, texto) da linha: título, fileira de tabela, item de lista ou parágrafo. O título que só repete o nome
        sai (o nome já está na carta), e a marca "Nível N:" do começo do parágrafo também (a etiqueta da carta já diz o
        nível)"""
        s = l.strip()
        if not s or s.startswith("Exemplo") or re.fullmatch(r"Nível \d+\.", s):
            return None
        if s.startswith("#"):
            t = re.sub(rf"^Nível {n} — ", "", s.lstrip("#").strip())
            return None if _sem_ponto(t).lower() == nome.lower() else ("titulo", t)
        if " | " in s:
            return ("tabela", s)
        if s.startswith("- "):
            return ("item", s)
        s = re.sub(r"^Nível \d+(?:: [^.]{1,80}\.|\.| ·) ", "", s)
        return ("par", s) if s else None

    def junta(blocos):
        """o texto da carta, legível ("espaçar os paragrafos e talz", pedido do Mizuki em 05/10/2026): uma linha em
        branco entre os blocos, e as fileiras de uma tabela e os itens de uma lista um embaixo do outro"""
        out = ""
        for k, (tipo, t) in enumerate(blocos):
            if k:
                out += "\n" if tipo == blocos[k - 1][0] and tipo in ("tabela", "item") else "\n\n"
            out += t
        return out

    out = {"caminhos": {}, "trilhas": {}, "no_caminho": {}}
    for d, (tipo, _) in donos.items():
        ents = tabela(d) or sem_tabela(d)
        niveis = NIV_CAMINHO if tipo == "caminho" else NIV_TRILHA
        dona = {}
        for k, (n, nome) in enumerate(ents):
            ms = marcas(d, n, nome)
            if not ms:
                raise SystemExit(f"{d}, nível {n} ({nome}): não achei onde o texto começa")
            for i in ms:
                if i in dona and dona[i] != k:
                    raise SystemExit(f"{d}: a linha {i + 1} abre duas habilidades")
                dona[i] = k
        # a seção que lista entradas com o nível no subtítulo ("#### Corrigir uma Falha — nível 2") abre com regras
        # comuns a todas elas: a introdução é da primeira entrada da lista, e não da habilidade de antes (o Evocador:
        # as Intervenções de Vínculo vinham parar na carta do nível 7, achado em 05/10/2026)
        for i in range(inicio[d] + 1, fim[d]):
            if L[i].startswith("### ") and i not in dona:
                j = next((x for x in sorted(dona) if x > i), None)
                if j is not None and not any(L[x].startswith("### ") for x in range(i + 1, j)) and re.search(r" — nível \d+$", L[j]):
                    dona[i] = dona[j]
        corte = sorted(dona) + [fim[d]]
        for k, (n, nome) in enumerate(ents):
            blocos = []
            for a, b in zip(corte, corte[1:]):
                if dona[a] != k:
                    continue
                trecho = [x for x in (bloco(l, n, nome) for l in L[a:b]) if x]
                while trecho and trecho[-1][0] == "titulo":
                    trecho.pop()                      # o título que fecha o trecho é da seção seguinte
                blocos += trecho
            h = {"nome": nome, "texto": junta(blocos), "titulos": [t for tipo, t in blocos if tipo == "titulo"]}
            if n in niveis:
                out["caminhos" if tipo == "caminho" else "trilhas"].setdefault(d, {})[str(n)] = h
            elif tipo == "trilha" and n in NIV_CAMINHO:
                out["no_caminho"].setdefault(d, {})[str(n)] = h
            else:
                raise SystemExit(f"{d}: o nível {n} não é de carta nenhuma")
        tem = set(int(x) for x in out["caminhos" if tipo == "caminho" else "trilhas"].get(d, {}))
        if tem != set(niveis):
            raise SystemExit(f"{d}: os níveis {sorted(tem)} não são {list(niveis)}")
    fonte = json.load(open(os.path.join(RAIZ, "manual-fonte.json"), encoding="utf-8"))
    return {"_meta": {"versao_do_livro": fonte["livro"], "sha256_do_livro": fonte["sha256"], "capitulo": CAPITULO[3:],
                      "o_que_e": "o nome e o texto de cada habilidade de Caminho e de Trilha, "
                                 "para as cartas da seção 7 da FICHA",
                      "niveis": {"caminho": list(NIV_CAMINHO), "trilha": list(NIV_TRILHA)}},
            "rotas": rotas, **out}


def confere_no_manual(dados):
    """cada nome e cada parágrafo gravado está no manual palavra por palavra"""
    M = Lv.texto(os.path.join(RAIZ, "manual.txt"))
    ruins = []
    for grupo in ("caminhos", "trilhas", "no_caminho"):
        for d, por in dados[grupo].items():
            for n, h in por.items():
                for p in [h["nome"]] + h["texto"].split("\n") + h["titulos"]:
                    if p and p not in M:
                        ruins.append(f"{d} {n}: {p[:60]}")
    return ruins


if __name__ == "__main__":
    novo = extrai()
    ruins = confere_no_manual(novo)
    if ruins:
        raise SystemExit("fora do manual: " + " · ".join(ruins[:5]))
    if "--confere" in sys.argv:
        velho = json.load(open(SAIDA, encoding="utf-8"))
        igual = json.dumps(velho, ensure_ascii=False, sort_keys=True) == json.dumps(novo, ensure_ascii=False, sort_keys=True)
        print("o arquivo bate com o livro" if igual else "o arquivo NAO bate com o livro")
        sys.exit(0 if igual else 1)
    json.dump(novo, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = sum(len(v) for g in ("caminhos", "trilhas", "no_caminho") for v in novo[g].values())
    print(f"{SAIDA}: {len(novo['caminhos'])} Caminhos, {len(novo['trilhas'])} Trilhas (com as rotas), {n} habilidades")
