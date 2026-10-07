# -*- coding: utf-8 -*-
"""Lê do livro o que a FICHA AMALDIÇOADA calcula e o catálogo não tem, e grava em ficha-v01/tecnica-do-livro.json.

    python3 ficha-v01/extrair_tecnica.py            # lê o manual.txt e regrava o arquivo
    python3 ficha-v01/extrair_tecnica.py --confere  # só compara o arquivo com o manual.txt, sem gravar

Por que este arquivo existe: o catalogo-projeto-m.json não traz os Talentos, as aptidões, as escadas de alcance, o
Domínio, a Técnica Máxima nem os pactos. A aba lê deste arquivo, que carrega a versão do livro de onde saiu. O gerador
(ficha_amaldicoada.py) nunca lê o livro: lê só este arquivo, que mora no repositório.

04/10/2026: o livro passou a ser a candidata reconstruída, e este script deixou de ler os capítulos em Markdown do HD
do Mizuki. Ele lê o manual.txt do repositório (extrair-manual.py), pelo livro.py. Os nomes das chaves continuam os da
v0.331 (passivas, classe_passiva), para não mexer em quem lê; os VALORES são os do livro novo, que chama a Passiva de
Talento e a Classe Passiva de Categoria de Efeito.

Nenhum número é digitado aqui. Tabela vira lista, lendo a tabela; número que o livro só escreve em frase é tirado da
frase, que tem de estar no manual palavra por palavra. A única lista escrita à mão são os exemplos de montagem, e cada
um carrega a frase do livro com o resultado, conferida.
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, RAIZ)
import livro as Lv

SAIDA = os.path.join(AQUI, "tecnica-do-livro.json")
_NUM = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "três": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7}


def _n(p):
    return int(p) if p.isdigit() else _NUM[p.lower()]


def _sem_ponto(s):
    return s.strip().rstrip(".").strip()


def capitulo(titulo):
    S = Lv.secao(titulo)
    if not S:
        raise SystemExit(f"o manual.txt nao tem o capitulo {titulo!r}")
    return S


def sec(titulo, dentro, n=0):
    S = Lv.secao(titulo, n, dentro=dentro)
    if not S:
        raise SystemExit(f"o manual.txt nao tem a secao {titulo!r}")
    return S


def tab(S, primeira):
    cab, fil = Lv.tabela(S, primeira)
    if cab is None:
        raise SystemExit(f"o manual.txt nao tem a tabela que comeca por {primeira!r}")
    return fil


def re_frase(rx, S=None):
    """a frase do livro que casa com a expressão; devolve o match"""
    t = " ".join(("\n".join(S) if S else Lv.texto()).split())
    m = re.search(rx, t)
    if not m:
        raise SystemExit(f"o livro nao tem mais a frase: {rx!r}")
    return m


def subsecoes(S, nivel=4):
    """[(título, linhas)] das seções de um nível dentro de um trecho"""
    out, atual = [], None
    for l in S[1:]:
        if Lv.nivel(l) and Lv.nivel(l) <= nivel:
            atual = (l.lstrip("#").strip(), []) if Lv.nivel(l) == nivel else None
            if atual:
                out.append(atual)
        elif atual:
            atual[1].append(l)
    return out


def primeiro(L):
    p = Lv.paragrafos(L)
    return p[0] if p else ""


# o cabeçalho de aquisição que abre uma entrada: já tem coluna própria na aba (requisito e Categoria de Efeito)
CABECALHO = re.compile(r"^(?:(?:Requisitos?(?: adicional)?|Aquisição): .+?\.\s+(?=[A-Z]))?(?:Sem requisito adicional\.\s*)?"
                       r"(?:Categoria de Efeito \d(?: ou \d)?\.\s*)?(?:Bênção gratuita, Lapidação 1\.\s*)?")


def texto_curto(L, teto=1300):
    """os parágrafos de uma entrada, até o teto de letras da caixa da aba, sem o cabeçalho de aquisição"""
    out = ""
    for k, p in enumerate(Lv.paragrafos(L)):
        if k == 0:
            p = CABECALHO.sub("", p)
        if len(out) + len(p) + 1 > teto and out:
            break
        out = (out + " " + p).strip()
    return out


# ---------------------------------------------------------------------------------------------
def talentos(cap11):
    out = []
    for titulo in ("Talentos de Categoria 1", "Talentos de Categoria 2", "Proteção e presença", "Talentos de Categoria 3"):
        S = sec(titulo, cap11)
        intro = " ".join(Lv.paragrafos(S, ate_subtitulo=True))
        ce = re.search(r"Categoria (\d)$", titulo) or re.search(r"Categoria de Efeito (\d)", intro)
        for nome, L in subsecoes(S):
            out.append({"nome": nome, "classe_passiva": ce.group(1), "faz": re.sub(r"^Talento\. ", "", primeiro(L))})
    for nome in ("Regra Própria", "Talento Próprio"):
        S = sec(nome, cap11)
        out.append({"nome": nome, "classe_passiva": "1, 2 ou 3", "faz": Lv.paragrafos(S, ate_subtitulo=True)[0]})
    return out


def escala_de(S, valor):
    """o que o Refino (ou a Lapidação) escala: as colunas da tabela que começa por ele, ou as linhas quando ela está deitada"""
    for cab, fil in Lv.tabelas(S or []):
        if cab[0] == valor:
            e = " e ".join(f[0] for f in fil) if cab[1][:1].isdigit() else " e ".join(cab[1:])
            return e[:1].lower() + e[1:]
    return "—"


def aptidoes(cap12):
    out = []
    for nome, req, ce in tab(cap12, "Aptidão"):
        S = Lv.secao(nome, dentro=cap12) or Lv.secao(nome, dentro=capitulo("15. Ritual e Pactos"))
        escala = escala_de(S, "Refino")
        if S:
            # a primeira frase da entrada repete o requisito ("Gratuita no Refino 1."): ela já tem coluna própria
            faz = texto_curto([re.sub(r"^" + re.escape(_sem_ponto(req)) + r"\.\s*", "", l) for l in S])
        else:
            faz = ""
        out.append({"nome": nome, "requisito": _sem_ponto(req), "classe_passiva": ce, "escala": escala, "faz": faz})
    return out


def base_por_classe(cap10):
    """a tabela Alcance e área, no formato que a aba lê: "raio 3 m, a 18 m", "raio 3 m, em você", "—" """
    S = sec("Alcance e área", cap10)
    out = {}

    def norm(c):
        c = _sem_ponto(c)
        if c.startswith("Indisponível"):
            return "—"
        m = re.match(r"Alcance (\S+ m); raio (\S+ m)", c)
        if m:
            return f"raio {m.group(2)}, a {m.group(1)}"
        m = re.match(r"Em você; raio (\S+ m)", c)
        if m:
            return f"raio {m.group(1)}, em você"
        return c
    for forma, c0, c15, c67 in tab(S, "Forma"):
        if forma == "Cura e Apoio":
            m = re.match(r"Apoio: (\S+ m)", _sem_ponto(c0))
            out["Cura"] = {"classe_0": "—", "classes_1_a_5": norm(c15), "classes_6_e_7": norm(c67)}
            out["Apoio"] = {"classe_0": m.group(1), "classes_1_a_5": norm(c15), "classes_6_e_7": norm(c67)}
        else:
            out[forma] = {"classe_0": norm(c0), "classes_1_a_5": norm(c15), "classes_6_e_7": norm(c67)}
    return out


def formas(cap10):
    out = []
    for nome, custo, alc, res in tab(sec("Formas de ataque", cap10), "Forma"):
        out.append({"nome": nome, "custa": "—" if custo == "0" else custo, "o_que_e": alc, "resolve": res})
    auto = re_frase(r"(Cura e Apoio são automáticos em alvos dispostos)\.").group(1)
    for nome, custo, alvo in tab(sec("Formas de amparo e Efeito", cap10), "Forma"):
        out.append({"nome": nome, "custa": "—" if custo == "0" else custo, "o_que_e": alvo,
                    "resolve": "Sem dano" if nome == "Efeito" else auto})
    return out


def escadas(cap10):
    t = {m: [d.strip() for d in _sem_ponto(g).split(";")] for m, g in tab(sec("Aumentos", cap10), "Medida")}
    return {"alcance": t["Distância ao alvo ou ponto"], "raio": t["Raio de esfera"], "comprimento": t["Comprimento de Cone ou Linha"]}


def classe_0(cap10):
    S = sec("Feitiços de Classe 0", cap10)
    cab, fil = Lv.tabela(S, "Seu nível")
    lin = {f[0]: f[1:] for f in fil}
    return {"niveis": [int(c.split(" a ")[0]) for c in cab[1:]], "quantos": [int(x) for x in lin["Quantidade conhecida"]],
            "dados": [int(x.split("d")[0]) for x in lin["Dano-base"]],
            "frase": Lv.frase("Você pode acrescentar uma Melhoria Leve, retirando um dado do dano-base."),
            "nao_cura": Lv.frase("Cura e Onda não estão disponíveis.")}


def liberacao(cap10):
    S = sec("Liberação Máxima", cap10)
    m = re_frase(r"Você recebe uma no nível (\d+), outra no (\d+) e outra no (\d+)\.", S)
    c = re_frase(r"Monte a Liberação antes da sessão, em Classe (\d) ou maior", S)
    return {"niveis": [int(x) for x in m.groups()], "classe_minima": int(c.group(1)),
            "frases": [Lv.frase(m.group(0)), Lv.frase("acrescente +Classe em d8 ao dano da montagem. Ela não serve para cura."),
                       Lv.frase("O custo é 3 × Classe de PE, aumentado em 50%, arredondado para cima. A Liberação exige Ação Completa.")]}


def tecnica_maxima(cap10):
    S = sec("Técnica Máxima", cap10)
    faixas = [{"de": int(n.split(" a ")[0]), "ate": int(n.split(" a ")[1]), "dados": int(d.split("d")[0]), "montagem": int(p), "pe": int(pe)}
              for n, d, p, pe in tab(S, "Nível")]
    pe = re_frase(r"A Máxima custa Ação Completa e (\d) × sua maior Classe em PE\.", S)
    return {"faixas": faixas, "pe_por_classe": int(pe.group(1)),
            "frases": [Lv.frase(pe.group(0)), Lv.frase("A Máxima não aceita Restrições que devolvam pontos.")]}


def dominio(cap14):
    S = sec("Expansão de Domínio", cap14)
    deg = []
    for d, esp, req, acerto in tab(S, "Degrau"):
        nivel = re.search(r"[Nn]ível (\d+)", req)
        deg.append({"degrau": d, "espacos": int(esp), "nivel": int(nivel.group(1)) if nivel else None,
                    "refino": int(re.search(r"refino (\d+)", req).group(1)), "abre_em": _sem_ponto(req), "acerto": _sem_ponto(acerto)})
    ab = {m: (c, r, d) for m, c, r, d in tab(sec("Abrir e manter", cap14), "Modo")}
    pe = lambda s: int(re.match(r"(\d) × maior Classe em PE", s).group(1))
    raio = re.match(r"([\d,]+) m × refino, até ([\d,]+ m)", ab["Incompleta"][1])
    vida = re_frase(r"Por fora, a barreira possui (\d+) × metade do refino em pontos de vida", cap14)
    return {"degraus": deg, "pe_por_classe": pe(ab["Incompleta"][0]), "pe_por_classe_sem_barreira": pe(ab["Aberto"][0]),
            "raio_por_refino": raio.group(1), "raio_da_incompleta": raio.group(2), "raio_sem_barreira": ab["Aberto"][1],
            "vida_da_barreira": int(vida.group(1)),
            "frases": [Lv.frase("Depois da abertura, conte metade do refino, arredondada para baixo, em turnos seus, no mínimo um."),
                       Lv.frase("Um custo positivo não cai abaixo de 1 PE; Classe 0 continua gratuita."),
                       Lv.frase(vida.group(0))]}


def pactos(cap15):
    S = sec("Pactos", cap15)
    formas_ = [{"forma": f, "quando": _sem_ponto(q), "teto": _sem_ponto(t)} for f, q, t in tab(S, "Forma")]
    b = re_frase(r"O pacto pode conceder uma aptidão, um espaço conhecido adicional ou um aumento do PE máximo igual à sua maior Classe\.", cap15)
    q = re_frase(r"metade da Essência em pactos permanentes, arredondada para baixo", cap15)
    return {"formas": formas_,
            "concede": [{"concede": "uma aptidão", "quem": "quem tem aptidão"},
                        {"concede": "um espaço conhecido", "quem": "qualquer rota, no repertório dela"},
                        {"concede": "PE máximo igual à maior Classe", "quem": "qualquer ficha"}],
            "frase": Lv.frase(b.group(0)), "quantos": Lv.frase(q.group(0))}


def numeros(cap10):
    S = sec("Pontos e preços", cap10)
    dev = {f[0]: f[3] for f in tab(S, "Classe") if len(f) == 4}
    teto = re_frase(r"o total não pode passar de (\d) × Classe em d8", cap10)
    out = []
    for c, _, pts, l, m, p in [f for f in tab(S, "Classe") if len(f) == 6]:
        out.append({"classe": int(c), "pontos": int(pts), "leve": int(l), "media": int(m), "pesada": int(p),
                    "devolucao": 2 * int(c) if all(v == "2 × Classe" for v in dev.values()) else None,
                    "teto": int(teto.group(1)) * int(c)})
    return out


def melhorias_por_classe(cap10):
    S = sec("Quantidade de peças", cap10)
    out = []
    for faixa, mel, res, _ in tab(S, "Classe"):
        a, b = [int(x) for x in re.findall(r"\d", faixa)][:2] if len(re.findall(r"\d", faixa)) > 1 else (int(faixa), int(faixa))
        out.append([f"{a} a {b}", str(Lv.numero(mel)), str(Lv.numero(res))])
    return out


# Os exemplos de montagem do livro: a prova da conta da aba. Cada um traz as peças, as Famílias Livres que o exemplo
# usa e a frase do livro com o resultado; o número de dados tem de estar na frase.
EXEMPLOS = [
    {"nome": "Fio de Arrasto", "classe": 1, "lib": False, "forma": "Projétil", "mel": ["Empurrão"], "res": [], "livres": ["Alcance"],
     "dados": 2, "pe": 3, "frase": "Sobram 3 − 0 − 1 = 2 pontos, que viram 2d8 de dano."},
    {"nome": "Peso nas Mãos", "classe": 1, "lib": False, "forma": "Toque", "mel": ["Derrubado"], "res": [], "livres": ["Controle", "Castigo"],
     "dados": 3, "pe": 3, "frase": "No acerto, causa 3d8 de Concussão, e o alvo faz TR Físico contra CD 12."},
    {"nome": "Corte Medido 2", "classe": 2, "lib": False, "forma": "Projétil", "mel": ["Fura", "Precisão"], "res": ["Parado"], "livres": ["Mira"],
     "dados": 5, "pe": 6, "frase": "2 | 6 | 1 | 1 | +1 | 5d8 | 6"},
    {"nome": "Corte Medido 3", "classe": 3, "lib": False, "forma": "Projétil", "mel": ["Fura", "Precisão"], "res": ["Parado"], "livres": ["Mira"],
     "dados": 9, "pe": 9, "frase": "Parado devolve os 2 pontos gastos: 9 − 2 + 2 = 9d8."},
    {"nome": "Corte Medido 5", "classe": 5, "lib": False, "forma": "Projétil", "mel": ["Fura", "Precisão"], "res": ["Parado"], "livres": ["Mira"],
     "dados": 15, "pe": 15, "frase": "Parado paga esses 3 pontos: 15 − 3 + 3 = 15d8"},
    {"nome": "Salto de exemplo", "classe": 2, "lib": False, "forma": "Projétil", "mel": ["Salto"], "res": ["Gesto"], "livres": [],
     "dados": 5, "pe": 6, "frase": "Projétil + Salto, de preço normal, gasta 2; Gesto devolve 1. São 5d8 no primeiro alvo."},
    {"nome": "Rede de contenção", "classe": 3, "lib": False, "forma": "Explosão", "mel": ["Atordoado", "Terreno"], "res": [],
     "livres": ["Amparo", "Tempo"], "dados": 0, "pe": 9, "frase": "Gasta os 9 pontos, usa duas Melhorias e não compra Restrição. O saldo é zero: não causa dano."},
    {"nome": "Fura sem desconto", "classe": 3, "lib": False, "forma": "Projétil", "mel": ["Fura"], "res": [], "livres": [],
     "dados": 6, "pe": 9, "frase": "Um Projétil de Classe 3 tem Fura por 3 pontos, sem desconto, e causa 6d8."},
    {"nome": "Aura com Fura", "classe": 3, "lib": False, "forma": "Aura", "mel": ["Fura"], "res": [], "livres": [],
     "dados": 7, "pe": 9, "frase": "Uma Aura de Classe 3, sem desconto, tem Fura: custo 2 + 3, com devolução 3 de Corpo a Corpo. Causa 7d8."},
    {"nome": "Corte de ruptura", "classe": 3, "lib": True, "forma": "Linha", "mel": [], "res": [], "livres": [],
     "dados": 10, "pe": 14, "frase": "A Liberação acrescenta 3d8: 10d8 numa linha de 18 m por 1,5 m."},
]


def exemplos():
    for e in EXEMPLOS:
        Lv.frase(e["frase"])
        if f"{e['dados']}d8" not in e["frase"] and not (e["dados"] == 0 and "não causa dano" in e["frase"]):
            raise SystemExit(f"o exemplo {e['nome']} diz {e['dados']} dados e a frase do livro nao")
    return EXEMPLOS


def rotas(cap13, cap12, catalogo_armas):
    marc = sec("Técnica Marcial", cap13)
    st = sec("Sem Técnica", cap13)
    ru = re_frase(r"(\w+) é o nome da sua Liberação Máxima\.", marc).group(1)
    og = re_frase(r"(\S+) é sua Técnica Máxima, disponível a partir do nível 17\.", marc).group(1)
    au = re_frase(r"(\w+) é o nome da sua Técnica Máxima, a partir do nível 17\.", st).group(1)
    re_frase(r"Você recebe Liberação Máxima normalmente", st)
    # o atributo de cada categoria de arma: a regra de Regras gerais (corpo a corpo com Força, Fineza deixa usar Destreza;
    # à distância com Destreza), aplicada às armas de cada categoria
    re_frase(r"Corpo a corpo, com arma ou desarmado \| d20 \+ Força \+ maestria\. Fineza permite usar Destreza no corpo a corpo\.")
    re_frase(r"À distância, com arma \| d20 \+ Destreza \+ maestria\. Inclui disparos e arremessos\.")
    so_tiro = ("Yumi", "Balestra", "Arma de Fogo")
    grupos = {}
    for nome, a in catalogo_armas.items():
        ats = grupos.setdefault(a["categoria"], [])
        if a["categoria"] not in so_tiro and "Força" not in ats:
            ats.append("Força")
        if (a["categoria"] in so_tiro or "Fineza" in a["propriedades"] or a.get("longo_alcance")) and "Destreza" not in ats:
            ats.append("Destreza")
    grupos = {k: sorted(v, key=["Força", "Destreza"].index) for k, v in grupos.items()}
    marciais = []
    for titulo in ("Talentos marciais", "Talentos de resposta"):
        for nome, L in subsecoes(sec(titulo, cap13)):
            m = re.match(r"(.+?) — Categoria de Efeito (\d)$", nome)
            marciais.append({"nome": m.group(1), "classe_passiva": m.group(2), "faz": primeiro(L)})
    ben = sec("Bênçãos", cap13)
    lap = {ce: int(Lv.numero(v)) for ce, v in tab(ben, "Categoria de Efeito")}
    bencaos = []
    gratis = re_frase(r"(\w[\w ]+?) e (\w[\w ]+?) são gratuitas desde Lapidação 1\.", ben)
    for nome in gratis.groups():
        S = sec(nome, cap13)
        bencaos.append({"nome": nome, "requisito": "Gratuita na Lapidação 1", "classe_passiva": "—",
                        "faz": texto_curto(S), "escala": escala_de(S, "Lapidação")})
    entradas = {}
    for titulo in [l.lstrip("#").strip() for l in cap13 if Lv.nivel(l) == 3 and l.lstrip("#").strip().startswith("Bênçãos de ")]:
        for nome, L in subsecoes(sec(titulo, cap13)):
            m = re.match(r"(.+?) — Categoria de Efeito (\d)$", nome)
            entradas[m.group(1)] = texto_curto(L)
    for nome, ce, req in tab(ben, "Bênção"):
        if nome == "Bênção Própria":
            S = sec(nome, cap13)
            bencaos.append({"nome": nome, "requisito": _sem_ponto(req), "classe_passiva": ce, "faz": texto_curto(S), "escala": "—"})
            continue
        r = f"Lapidação {lap[ce]}" + ("" if req == "—" else f" e {_sem_ponto(req)}")
        bencaos.append({"nome": nome, "requisito": r, "classe_passiva": ce, "faz": entradas[nome], "escala": "—"})
    return {
        "nomes": {"Sem Técnica": {"feitico": "Manejo", "liberacao": "Liberação Máxima", "tecnica_maxima": au},
                  "Técnica Marcial": {"feitico": "Kata", "liberacao": ru, "tecnica_maxima": og}},
        "frases": [Lv.frase("Kata é uma aplicação de Técnica Marcial. Manejo é uma aplicação da rota Sem Técnica."),
                   Lv.frase("Esta rota não concede Expansão de Domínio, incompleta ou completa, nem Extensão de Domínio."),
                   Lv.frase("O equipamento em uso é seu Selo."),
                   Lv.frase("PE significa Pontos de Energia para quem possui energia amaldiçoada e Pontos de Esforço para quem não possui.")],
        "sementes": [n for n, _ in subsecoes(sec("Sementes", cap13))],
        "semente_frase": Lv.frase("Ela conta como uma aptidão adicional."),
        "grupos_de_arma": grupos,
        "rota_de_arma": Lv.frase("Ao escolher esta rota, selecione três categorias de armas diferentes entre as categorias de Equipamento."),
        "atributo_de_arma": Lv.frase("Use o atributo de ataque da arma empregada naquela execução tanto para o ataque quanto para a CD da Kata:"),
        "ferramenta": [Lv.frase("Na criação, registre se seus ataques desarmados passam pelo objeto."),
                       Lv.frase("Escolha um dos cinco atributos para os ataques e a CD de suas Katas.")],
        "passivas_marciais": marciais,
        "passivas_sem_tecnica": Lv.frase("Você pode escolher Talentos do Catálogo de criação e Talentos marciais compatíveis com sua semente"),
        "bencaos": bencaos,
        "bencaos_de_graca": list(gratis.groups()),
        "bencaos_frases": [Lv.frase(gratis.group(0))],
    }


def extrai():
    cap9, cap10, cap11 = capitulo("9. Progressão"), capitulo("10. Fundamento"), capitulo("11. Catálogo de criação")
    cap12, cap13, cap14, cap15 = capitulo("12. Aptidões e Refino"), capitulo("13. Rotas de criação"), capitulo("14. Poderes avançados"), capitulo("15. Ritual e Pactos")
    cat = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
    fonte = json.load(open(os.path.join(RAIZ, "manual-fonte.json"), encoding="utf-8"))
    ce = re_frase(r"Suas Categorias de Efeito \(CE\) 1, 2 e 3 custam respectivamente (\d), (\d) e (\d) espaços e ficam disponíveis nos níveis (\d+), (\d+) e (\d+)\.", cap10)
    pagas = re_frase(r"O máximo é (\w+) Talentos pagos\.", cap10)
    graca = re_frase(r"Quem tem energia amaldiçoada começa com (.+?) e (.+?), sem gastar uma escolha\.", cap12)
    return {
        "_meta": {
            "o_que_e": "o que a FICHA AMALDIÇOADA calcula e o catalogo-projeto-m.json não tem, lido do manual.txt",
            "versao_do_livro": fonte["livro"], "sha256_do_livro": fonte["sha256"], "extraido_por": "ficha-v01/extrair_tecnica.py",
            "capitulos": ["9. Progressão", "10. Fundamento", "11. Catálogo de criação", "12. Aptidões e Refino",
                          "13. Rotas de criação", "14. Poderes avançados", "15. Ritual e Pactos"],
            "nomes_das_chaves": "passivas e classe_passiva são os Talentos e a Categoria de Efeito do livro novo",
        },
        "passivas": talentos(cap11),
        "classe_passiva": [{"classe_passiva": "Livre", "custa": "nada", "nivel": 1}] +
                          [{"classe_passiva": str(i + 1), "custa": f"{ce.group(i + 1)} espaço" + ("s" if ce.group(i + 1) != "1" else ""),
                            "nivel": int(ce.group(i + 4))} for i in range(3)],
        "passivas_pagas": {"cinco": _n(pagas.group(1)), "frase": Lv.frase(pagas.group(0))},
        "regra_propria": {"frase": Lv.frase("Ao melhorar de Categoria de Efeito 2 para 3, ocupe somente mais um espaço."),
                          "espacos": {ce_: l for ce_, _, l in tab(sec("Regra Própria", cap11), "Categoria de Efeito")}},
        "aptidoes": aptidoes(cap12),
        "aptidoes_de_graca": list(graca.groups()),
        "aptidoes_frases": [Lv.frase(graca.group(0)),
                            Lv.frase("Se escolher Refino, receba mais +1 de Refino e uma aptidão. Se o ganho básico já deixou seu Refino em 10, receba duas aptidões, em vez desse aumento adicional e de uma aptidão."),
                            Lv.frase("Sem Traje e sem Revestimento, sua proteção é 1 + um terço do Refino, arredondado para baixo.")],
        "escadas": escadas(cap10),
        "base_por_classe": base_por_classe(cap10),
        "formas": formas(cap10),
        "toque": Lv.frase("Toque permanece a 1,5 m."),
        "classe_0": classe_0(cap10),
        "liberacao": liberacao(cap10),
        "tecnica_maxima": tecnica_maxima(cap10),
        "dominio": dominio(cap14),
        "pactos": pactos(cap15),
        "leque": {"frases": [Lv.frase("Leque | Um feitiço adicional e um Talento, sem pagar espaços por eles."),
                             Lv.frase("Cada Leque abre uma vaga própria para ele além do limite de cinco Talentos pagos.")]},
        "controle": {"frases": [Lv.frase("Com saldo de dano até a Classe, seus efeitos de Controle duram uma rodada a mais. Com saldo zero, eles também recebem +2 na CD.")]},
        "numeros_da_montagem": numeros(cap10),
        "melhorias_por_classe": melhorias_por_classe(cap10),
        "feiticos_prontos": exemplos(),
        "rotas": rotas(cap13, cap12, cat["equipamento"]["armas"]),
    }


if __name__ == "__main__":
    novo = extrai()
    if "--confere" in sys.argv:
        velho = json.load(open(SAIDA, encoding="utf-8"))
        igual = json.dumps(velho, ensure_ascii=False, sort_keys=True) == json.dumps(novo, ensure_ascii=False, sort_keys=True)
        difere = [k for k in novo if json.dumps(velho.get(k), ensure_ascii=False, sort_keys=True) != json.dumps(novo[k], ensure_ascii=False, sort_keys=True)]
        print("o arquivo bate com o livro" if igual else f"o arquivo NAO bate com o livro: {difere}")
        sys.exit(0 if igual else 1)
    json.dump(novo, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{SAIDA}: {len(novo['passivas'])} Talentos, {len(novo['aptidoes'])} aptidões, "
          f"{len(novo['feiticos_prontos'])} exemplos de montagem")
