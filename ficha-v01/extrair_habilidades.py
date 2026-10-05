# -*- coding: utf-8 -*-
"""Lê do livro as habilidades de cada Caminho e de cada Trilha, e grava em ficha-v01/habilidades-do-livro.json.

    python3 ficha-v01/extrair_habilidades.py            # lê o manual.txt e regrava o arquivo
    python3 ficha-v01/extrair_habilidades.py --confere  # só compara o arquivo com o manual.txt, sem gravar

Por que este arquivo existe: a seção 7 da FICHA (as cartas de Habilidades, B34) nasceu escrita à mão, com a forma já
pronta para o livro. Em 05/10/2026 o Mizuki escolheu a opção B da medida: a carta traz o nome e o primeiro
parágrafo do livro, o texto inteiro fica na nota da carta, e o jogador pode apagar e escrever o que preferir ("B - mas
dando permissão para o jogador apagar o texto e colocar oq preferir"). O texto inteiro não cabe: das 109 cartas, só 4
cabem inteiras nas 7 linhas da caixa, e o primeiro parágrafo cabe em 108.

De onde sai cada coisa, sem nada digitado:
  · os níveis e os nomes, da tabela de progressão de cada Caminho e de cada Trilha ("Nível | Habilidade"); as Trilhas
    do Guia não têm tabela, e o nome sai do título "Nível N — Nome", ou do título logo acima do parágrafo "Nível N.";
  · as rotas, dos títulos "Trilha: rota" (o Batedor tem três, e o livro manda escolher uma no nível 2). Cada rota é uma
    entrada do menu de Trilha ("Batedor · Yumi"), pedido do Mizuki em 05/10/2026;
  · as marcas de cada habilidade são o parágrafo "Nível N:", "Nível N." ou "Nível N ·", o título "Nível N — Nome", um
    título com "nível N", e a primeira vez que o nome dela abre um título ou um parágrafo. Cada marca abre um trecho, que
    vai até a marca seguinte, e o trecho é da habilidade dona da marca: o livro nem sempre segue a ordem dos níveis (o
    Pugilista põe a Rajada Marcial, do nível 7, entre o Corpo Treinado e o Quebrar o Compasso, do nível 2);
  · o texto inteiro são os parágrafos, os subtítulos e as fileiras de tabela dos trechos, sem os exemplos e sem as
    marcas "Nível N." soltas. O resumo é o primeiro parágrafo, sem a marca do começo; o parágrafo curto (menos de CURTO
    letras) e a linha de ficha ("Reação + 2 PE.") levam o seguinte junto, e o resumo fica em frases inteiras até CABE
    letras. O nome na carta vai inteiro até NOME_CABE letras, e acima disso, "as primeiras e mais N".
  · uma entrega de Trilha num nível que não é de Trilha (o nível 7 do Pugilista, a Rajada Marcial) vai para
    `no_caminho`: o livro diz que ela "Não acrescenta um novo degrau de Trilha no nível 7", e o Mizuki a pôs na carta
    do nível 7 do Caminho ("No caso do pungilista, o nv7 seria do caminho mesmo").

O --confere refaz tudo e compara; e cada parágrafo, cada resumo e cada nome gravados têm de estar no manual.
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
CURTO = 80                  # o parágrafo com menos letras que isto não diz sozinho o que a habilidade faz
CABE = 330                  # letras que a caixa da carta mostra: 13 colunas de 28 px por 6 linhas de 21 px, em Roboto 10
                            # (medido em 05/10/2026 com a fonte: 330 letras em frases inteiras cabem nas 7 linhas)
NOME_CABE = 75              # o nome da carta tem duas linhas de 10 colunas, em Castoro 11 (pedido do Mizuki em 05/10/2026);
                            # medido com a fonte: os nomes de até 73 letras cabem, e os de 84 ou mais pedem três linhas


def _sem_ponto(s):
    return s.strip().rstrip(".").strip()


def _nomes(s):
    """"Ataque Extra, Nem Um Arranhão e Ainda de Pé" -> as três"""
    return [x for x in (_sem_ponto(p) for p in re.split(r",|;| e |: ", s)) if x]


def _corta(t):
    """o resumo em frases inteiras até CABE letras; a primeira frase fica sempre, mesmo maior"""
    if len(t) <= CABE:
        return t
    frases = re.findall(r".+?[.:](?= |\n|$)|.+$", t, re.S)
    out = frases[0]
    for f in frases[1:]:
        if len(out + f) > CABE:
            break
        out += f
    return out.rstrip()


def nome_na_carta(nome):
    """o nome inteiro, se cabe; se não, as primeiras habilidades da lista que cabem e "e mais N" (a nota tem o resto)"""
    if len(nome) <= NOME_CABE:
        return nome
    itens = [x.strip() for x in re.split(r", | e ", nome)]
    for k in range(len(itens) - 1, 0, -1):
        t = ", ".join(itens[:k]) + f" e mais {len(itens) - k}"
        if len(t) <= NOME_CABE:
            return t
    return itens[0] + f" e mais {len(itens) - 1}"


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

    def linha(l, n, nome):
        """a linha como vai para o texto: título vira linha comum, e o título que só repete o nome sai"""
        s = l.strip()
        if not s.startswith("#"):
            return s
        t = s.lstrip("#").strip()
        t = re.sub(rf"^Nível {n} — ", "", t)
        return None if _sem_ponto(t).lower() == nome.lower() else t

    def resumo(pars):
        """o primeiro parágrafo, sem a marca do começo. A linha de ficha ("Ação Bônus · Sem custo de PE.") e o parágrafo
        curto ("O raio de Olhos Em Mim aumenta para 9 m.") levam junto o parágrafo seguinte, que é o que a habilidade faz"""
        limpos = []
        for p in pars:
            if " | " in p or len(p) <= 12 or p.startswith("- ") or not re.search(r"[.:]$|[.:] ", p):
                continue
            p = re.sub(r"^Nível \d+(?:: [^.]{1,80}\.|\.| ·) ", "", p)
            limpos.append(p)
            if len(limpos) == 2 or not ((" · " in p and len(p) < 120) or len(p) < CURTO):
                break
        return _corta("\n".join(limpos))

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
        corte = sorted(dona) + [fim[d]]
        for k, (n, nome) in enumerate(ents):
            pars = []
            for a, b in zip(corte, corte[1:]):
                if dona[a] != k:
                    continue
                trecho = [linha(l, n, nome) for l in L[a:b]]
                trecho = [x for x in trecho if x and not x.startswith("Exemplo") and not re.fullmatch(r"Nível \d+\.", x)]
                while trecho and not re.search(r"[.:]$|[.:] | \| ", trecho[-1]):
                    trecho.pop()                      # o título que fecha o trecho é da seção seguinte
                pars += trecho
            h = {"nome": nome, "nome_na_carta": nome_na_carta(nome), "resumo": resumo(pars), "texto": "\n".join(pars)}
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
                      "o_que_e": "o nome, o primeiro parágrafo e o texto inteiro de cada habilidade de Caminho e de Trilha, "
                                 "para as cartas da seção 7 da FICHA",
                      "niveis": {"caminho": list(NIV_CAMINHO), "trilha": list(NIV_TRILHA)}},
            "rotas": rotas, **out}


def confere_no_manual(dados):
    """cada nome, resumo e parágrafo gravado está no manual palavra por palavra"""
    M = Lv.texto(os.path.join(RAIZ, "manual.txt"))
    ruins = []
    for grupo in ("caminhos", "trilhas", "no_caminho"):
        for d, por in dados[grupo].items():
            for n, h in por.items():
                for p in [h["nome"]] + h["resumo"].split("\n") + h["texto"].split("\n"):
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
