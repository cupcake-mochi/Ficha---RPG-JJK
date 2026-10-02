# -*- coding: utf-8 -*-
"""Monta o estudo do menu rápido da seção 8 da FICHA (mockup/menu-rapido-estudo.html).

Pedido do Mizuki no B31 (01/10/2026): trocar a seção 8 da FICHA por um menu retrátil com o que foi pego na FICHA
AMALDIÇOADA. Em 02/10/2026 ele respondeu que o menu vale para todo mundo (B), e que a Ficha Amaldiçoada muda conforme a
Origem para o menu funcionar igual em qualquer ficha. Este estudo mostra quatro formas do menu nas quatro rotas de
criação, antes de construir.

O desenho da página é o do estudo da Ficha Pessoal (o CSS é copiado de lá), e a folha usa a grade de 47 colunas da FICHA.
Os dados saem do ficha-v01/tecnica-do-livro.json (feitiços prontos, Passivas, aptidões, Liberação, Técnica Máxima,
Domínio) e, no que ele não tem (as Passivas da Técnica Marcial e as Bênçãos), do livro. Nenhum número de regra é
digitado aqui.

    python3 mockup/estudo_menu_rapido.py
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
LIVRO = "/media/mizuki/HD Externo II/Claude/Claude 2/sistema/05-material/livro/manual"
TEC = json.load(open(os.path.join(RAIZ, "ficha-v01", "tecnica-do-livro.json"), encoding="utf-8"))
NIVEL = 20                       # o exemplo: duas Liberações (10 e 20) e a Técnica Máxima da faixa 17 a 20


def capitulo(arq):
    return open(os.path.join(LIVRO, arq), encoding="utf-8").read()


def bloco_do_livro(arq, nome):
    """a primeira linha de citação da entrada: '> **Nome** — o que faz', sem o nome e sem crase nem negrito"""
    m = re.search(r"^> \*\*`?" + re.escape(nome) + r"`?\*\* — (.+)$", capitulo(arq), re.M)
    if not m:
        raise SystemExit(f"não achei a entrada {nome} em {arq}")
    return limpa(m.group(1))


def limpa(t):
    return ini(re.sub(r"[`*]", "", t).strip())


def ini(t):
    """toda caixa abre em maiúscula, como na Ficha Amaldiçoada (B31)"""
    return t[:1].upper() + t[1:]


def primeira_frase(t):
    """a primeira frase da regra; se ela for só a ação ('Ação padrão.'), vai com a seguinte"""
    fr = re.split(r"(?<=\.) ", t)
    return fr[0] if len(fr[0]) >= 25 or len(fr) == 1 else fr[0] + " " + fr[1]


def classe_passiva_marcial(nome):
    """a Classe Passiva das Passivas de exemplo do capítulo da Técnica Marcial: a linha 'Classe Passiva X.' da entrada"""
    txt = capitulo("42-tecnica-marcial.md")
    i = txt.index(f"### `{nome}`")
    m = re.search(r"Classe Passiva (Livre|\d)", txt[i:])
    return m.group(1)


def frase_marcial(nome):
    """a primeira regra em negrito da entrada da Técnica Marcial ('**Saque.** Você saca ...')"""
    txt = capitulo("42-tecnica-marcial.md")
    i = txt.index(f"### `{nome}`")
    m = re.search(r"^> \*\*[^*]+\.\*\* (.+)$", txt[i:], re.M)
    return limpa(m.group(1))


def bencao(nome):
    linhas = [l for l in capitulo("47-bencaos-e-lapidacao.md").split("\n") if l.startswith(f"| {nome} |")]
    req, cp = [c.strip() for c in linhas[0].strip("|").split("|")][1:3]
    return {"cp": "—" if cp == "—" else cp, "nome": nome, "faz": bloco_do_livro("47-bencaos-e-lapidacao.md", nome),
            "marca": "de graça" if "grátis" in req else ""}


FORMAS = {f["nome"]: f for f in TEC["formas"]}
CURTO = {"Rolagem de acerto": "Acerto", "Teste de Resistência, metade no sucesso": "TR, metade",
         "Automático": "Automático", "Automático no aliado, acerto no hostil": "Aliado: automático"}
PRONTOS = {f["nome"]: f for f in TEC["feiticos_prontos"]}


def poder(nome):
    f = PRONTOS[nome]
    resolve = FORMAS[f["forma"]]["resolve"]
    return {"c": f["classe"], "nome": f["nome"], "pe": f.get("pe", 3 * f["classe"]), "forma": f["forma"],
            "resolve": CURTO.get(resolve, resolve), "faz": ini(f["livro"])}


# a lista do exemplo: feitiços prontos do capítulo de Fundamento, os mesmos nas quatro rotas (só muda o nome da peça)
LISTA = ["Estalo", "Perfurar", "Lança Negra", "Palma Trovejante", "Marca do Carrasco", "Costura", "Julgamento Vertical",
         "Purga Escarlate", "Chuva de Agulhas"]
LIBS = ["Rachadura", "Golpe do Voto"]                      # uma no nível 10, outra no 20
tm = next(f for f in TEC["tecnica_maxima"]["faixas"] if f["de"] <= NIVEL <= f["ate"])
MAIOR = tm["pe"] // TEC["tecnica_maxima"]["pe_por_classe"]   # a maior Classe da faixa: a Técnica Máxima custa 5 × ela
dom = TEC["dominio"]
inc = dom["degraus"][0]

APT = {a["nome"]: a for a in TEC["aptidoes"]}


def aptidao(nome, marca=""):
    a = APT[nome]
    return {"cp": a["classe_passiva"], "nome": nome, "faz": ini(primeira_frase(a["faz"])), "marca": marca}


PAS = {p["nome"]: p for p in TEC["passivas"]}


def passiva(nome):
    return {"cp": PAS[nome]["classe_passiva"], "nome": nome, "faz": ini(PAS[nome]["faz"]), "marca": ""}


def passiva_marcial(nome):
    return {"cp": classe_passiva_marcial(nome), "nome": nome, "faz": frase_marcial(nome), "marca": ""}


def maximas(lib, tecmax, com_dominio):
    out = [{"tipo": "lib", "c": PRONTOS[n]["classe"], "nome": n, "pe": PRONTOS[n]["pe"], "forma": PRONTOS[n]["forma"],
            "resolve": CURTO[FORMAS[PRONTOS[n]["forma"]]["resolve"]], "faz": ini(PRONTOS[n]["livro"]), "rot": lib} for n in LIBS]
    # a Técnica Máxima não tem Classe (capítulo de Fundamento): o dano é o da faixa de nível, e o PE é 5 × a maior Classe
    out.append({"tipo": "tm", "c": "—", "nome": tecmax, "pe": tm["pe"], "forma": "—", "resolve": "Fixo",
                "faz": f"{tm['dados']}d8 = {int(tm['dados'] * 4.5)}, o dano fixo da faixa do nível {tm['de']} a {tm['ate']}. Não aceita Restrição",
                "rot": tecmax})
    if com_dominio:
        out.append({"tipo": "dom", "c": "—", "nome": "Expansão incompleta", "pe": dom["pe_por_classe"] * MAIOR,
                    "forma": "Domínio", "resolve": "Acerto",
                    # o custo cheio (6 × a maior Classe) já está na caixa de PE da carta; o resumo traz o desconto e a duração
                    "faz": f"{ini(dom['frases'][1].split(',')[0])}. {dom['frases'][2]}",
                    "rot": "Domínio"})
    return out


ROTAS = [
    {"id": "fund", "nome": "Fundamento", "quem": "Latente, Receptáculo, Descendente, Reencarnado, Feto, e a Restrição Celestial pelo corpo",
     "poder": "Feitiço", "poderes": "Feitiços", "lib": "Liberação Máxima", "tm": "Técnica Máxima", "dom": True,
     "apt": "Aptidões", "escala": "Refino",
     "maximas": maximas("Liberação Máxima", "Técnica Máxima", True),
     "passivas": [passiva(n) for n in ("Leitura", "Instinto", "Fluxo")],
     "aptidoes": [aptidao("Cobrir-se de energia", "de graça"), aptidao("Canalizar energia", "de graça"),
                  aptidao("Projetar energia"), aptidao("Barreira Simples"), aptidao("Domínio Simples")]},
    {"id": "sem", "nome": "Sem Técnica", "quem": "sub-origem de Latente, Receptáculo, Descendente, Reencarnado ou Feto",
     "poder": "Manejo", "poderes": "Manejos", "lib": "Liberação Máxima", "tm": "Auge", "dom": False,
     "apt": "Aptidões", "escala": "Refino",
     "maximas": maximas("Liberação Máxima", "Auge", False),
     "passivas": [passiva(n) for n in ("Leitura", "Instinto", "Fluxo")],
     "aptidoes": [aptidao("Energia Reversa", "semente"), aptidao("Cobrir-se de energia", "de graça"),
                  aptidao("Canalizar energia", "de graça"), aptidao("Barreira Simples")]},
    {"id": "corpo", "nome": "Corpo Amaldiçoado", "quem": "Técnica Marcial, com energia amaldiçoada",
     "poder": "Kata", "poderes": "Katas", "lib": "Ruptura", "tm": "Ōgi", "dom": False,
     "apt": "Aptidões", "escala": "Refino",
     "maximas": maximas("Ruptura", "Ōgi", False),
     "passivas": [passiva_marcial(n) for n in ("Calo", "Maldição do Inventário", "Contragolpe")],
     "aptidoes": [aptidao("Cobrir-se de energia", "de graça"), aptidao("Canalizar energia", "de graça"),
                  aptidao("Barreira Simples"), aptidao("Kokusen Constante")]},
    {"id": "celeste", "nome": "Restrição Celestial sem energia", "quem": "Técnica Marcial, sem energia amaldiçoada",
     "poder": "Kata", "poderes": "Katas", "lib": "Ruptura", "tm": "Ōgi", "dom": False,
     "apt": "Bênçãos", "escala": "Lapidação",
     "maximas": maximas("Ruptura", "Ōgi", False),
     "passivas": [passiva_marcial(n) for n in ("Calo", "Leitura", "Segundo Fôlego")],
     "aptidoes": [bencao("Defesa sem Armadura"), bencao("Estímulo Muscular"), bencao("Ímpeto"), bencao("Faro"),
                  bencao("Antecipar")]},
]
for r in ROTAS:
    r["lista"] = [poder(n) for n in LISTA]

# Quinto estudo (02/10/2026): o menu mostra o que o jogador escreveu, e a Ficha Amaldiçoada mostra a conta ("a ficha
# amaldiçoada apresenta o calculo, menu rapido as informações do jogador"). Os textos abaixo são de preenchimento, na
# técnica de peso do exemplo da Kaori; os curtos vêm do estudo da Ficha Amaldiçoada. O Maré Negra é o feitiço com peça
# criada da pergunta de 02/10: Classe 3, Projétil, Efeito Próprio (Média) e Restrição Própria (Leve), 9 − 3 + 2 = 8d8.
COMO = {
    "Estalo": "Ela bate as mãos e o ar entre elas ganha peso. O que sai é um soco sem braço.",
    "Perfurar": "Parada, ela aperta o ar até virar uma ponta e solta num alvo só.",
    "Lança Negra": "Uma rodada inteira apertando o ar entre as palmas. Sai uma haste escura que atravessa proteção.",
    "Palma Trovejante": "Ela abre as mãos de uma vez e o peso sai em leque, derrubando o que estiver na frente.",
    "Marca do Carrasco": "O peso fica grudado no alvo depois do golpe e continua esmagando. Uma vez por cena.",
    "Maré Negra": "Ela pisa na poça e o peso sobe pela água até a mão. O jato sai escuro, acerta um alvo só e empurra ele 3 m "
                  "para trás, na direção em que saiu (Efeito Próprio, Média, combinado com o mestre). Sem água no chão ela não "
                  "tem o que puxar: o feitiço só sai com o pé molhado (Restrição Própria, Leve).",
    "Costura": "Ela tira o peso de cima do ferimento de um aliado, e a carne volta para o lugar.",
    "Julgamento Vertical": "O peso cai de cima numa linha reta, como uma porta de ferro fechando.",
    "Purga Escarlate": "Ela não mira: o peso acha o alvo e desce sem pedir licença.",
    "Chuva de Agulhas": "Seis pontas de ar pesado, uma atrás da outra, enquanto ela fica parada.",
    "Rachadura": "O chão aguenta o peso até não aguentar mais. A rachadura corre em linha reta e engole o que estiver em cima.",
    "Golpe do Voto": "Tudo que ela segurou na luta inteira, devolvido num golpe só.",
}
MARE = {"c": 3, "nome": "Maré Negra", "pe": 9, "forma": "Projétil", "resolve": CURTO[FORMAS["Projétil"]["resolve"]],
        "faz": "8d8 = 36"}
COMO_TM = ("Ela fecha as duas mãos sobre o alvo e para de segurar o peso que carregou a vida inteira. O ar em volta fica "
           "parado, a poeira cai reta no chão, e por um instante tudo ali pesa o mesmo que uma montanha. Quem estiver no meio "
           "não cai: afunda. O nome vem do que a avó dizia quando ela era criança e não conseguia levantar a mala sozinha.")
COMO_DOM = ("Uma sala sem paredes, com o chão de pedra polida e uma balança enorme no centro. Tudo que entra tem o peso "
            "medido, e quem pesa mais que ela sente o corpo puxado para o chão a cada passo. Não há teto: olhando para cima, "
            "só escuro.")
LIVRE = {"cp": "Livre", "nome": "Passiva Livre", "faz": "", "marca": "",
         "texto": "Ela sente o peso de tudo que toca: sabe quanto um objeto pesa só de encostar."}
REGRA = {"cp": "—", "nome": "Regra Própria", "faz": "", "marca": "", "sem": "Esta técnica não tem Regra Própria"}
TEXTO_DO_JOGADOR = {
    "Fluxo": "Quando ela solta uma Classe 3, o peso que sobra fica em volta dela como uma capa.",
    "Canalizar energia": "O soco dela chega com o peso de um carro.",
    "Contragolpe": "Errou nela, o peso da arma volta para a mão de quem atacou.",
    "Ímpeto": "Ela corre baixo, quase encostando o peito no chão.",
}
PROPRIAS = {
    "passiva": {"cp": "1", "nome": "Passiva Própria (CP 1)", "faz": "", "marca": "criada",
                "texto": "Nada que ela segure cai da mão dela contra a vontade dela."},
    "aptidao": {"cp": "1", "nome": "Aptidão Própria (CP 1)", "faz": "", "marca": "criada",
                "texto": "Ela deixa um objeto pesado por uma cena inteira, sem gastar PE, enquanto não soltar ele."},
    "bencao": {"cp": "1", "nome": "Bênção Própria (CP 1)", "faz": "", "marca": "criada",
               "texto": "Ela levanta e carrega o dobro do que o corpo dela deveria aguentar, por uma cena."},
}
for r in ROTAS:
    lista = [dict(p, como=COMO[p["nome"]]) for p in r["lista"]]
    r["lista"] = lista[:5] + [dict(MARE, como=COMO["Maré Negra"])] + lista[5:]
    for m in r["maximas"]:
        if m["tipo"] == "lib":
            m["como"] = COMO[m["nome"]]
        elif m["tipo"] == "tm":
            m.update(nome="Peso do Mundo", como=COMO_TM)
        else:
            m.update(nome="Balança Escura", como=COMO_DOM)
    r["passivas"] = [LIVRE, REGRA] + [dict(p, texto=TEXTO_DO_JOGADOR.get(p["nome"], "")) for p in r["passivas"]] + [PROPRIAS["passiva"]]
    r["aptidoes"] = [dict(a, texto=TEXTO_DO_JOGADOR.get(a["nome"], "")) for a in r["aptidoes"]] + \
                    [PROPRIAS["bencao" if r["apt"] == "Bênçãos" else "aptidao"]]
# o texto corrido que enche uma caixa, para a página medir quantas linhas a carta do menu precisa
ENCHE = " ".join(a["faz"] for a in TEC["aptidoes"]).replace("`", "")

# a prova dos textos (segundo estudo, 02/10/2026): todo resumo que o livro dá para cada tipo de carta, para a página
# conferir quantos cabem na caixa de cada variação. O feitiço usa o resultado que o livro imprime; a Passiva, a regra
# inteira; a aptidão, a primeira frase da caixa de regra (a caixa inteira chega a 1.303 letras e fica na Ficha
# Amaldiçoada); a Bênção, a linha da entrada.
NOMES_BENCAOS = [l.split("|")[1].strip() for l in capitulo("47-bencaos-e-lapidacao.md").split("\n")
                 if re.match(r"^\| [^|]+ \| [^|]+ \| [^|]+ \|$", l) and not l.startswith("| Bênção |") and "---" not in l]
MARCIAIS = ["Calo", "Maldição do Inventário", "Leitura", "Segundo Fôlego", "Contragolpe", "Aliança"]
fund = maximas("Liberação Máxima", "Técnica Máxima", True)
PROVA = {      # [nome, resumo]
    "feitiços": [[f["nome"], ini(f["livro"])] for f in TEC["feiticos_prontos"]]
                + [[m["nome"], m["faz"]] for m in fund if m["tipo"] in ("tm", "dom")],
    "Passivas": [[p["nome"], ini(p["faz"])] for p in TEC["passivas"]] + [[n + " (marcial)", frase_marcial(n)] for n in MARCIAIS],
    "aptidões e Bênçãos": [[a["nome"], ini(primeira_frase(a["faz"]))] for a in TEC["aptidoes"]]
                          + [[n, bencao(n)["faz"]] for n in NOMES_BENCAOS],
}

# o teto da aba, que o menu tem de comportar (B29): 36 lugares de feitiço, 3 Liberações, a Técnica Máxima, o Domínio,
# 12 Passivas e 12 aptidões
CAP = {"poderes": 36, "maximas": 5, "passivas": 14, "aptidoes": 12}     # Passivas: a Livre e a Regra Própria, mais as 12

css = re.search(r"<style>([\s\S]*?)</style>", open(os.path.join(AQUI, "ficha-pessoal-estudo.html"), encoding="utf-8").read()).group(1)
modelo = open(os.path.join(AQUI, "menu-rapido-estudo.modelo.html"), encoding="utf-8").read()
# a linha de números da carta (terceiro estudo): o PE, a Forma e como resolve têm de caber inteiros, numa linha só
LINHA = {"pe": [f"{m} PE" for m in sorted({p["pe"] for r in ROTAS for p in r["lista"] + r["maximas"]})],
         "forma": [f["nome"] for f in TEC["formas"]] + ["Domínio", "—"],
         "resolve": sorted(set(CURTO.values()) | {"Fixo"})}
dados = {"rotas": ROTAS, "cap": CAP, "nivel": NIVEL, "versao": TEC["_meta"]["versao_do_livro"], "prova": PROVA, "linha": LINHA, "enche": ENCHE}
html = modelo.replace("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/", css).replace("/*DADOS*/", json.dumps(dados, ensure_ascii=False))
open(os.path.join(AQUI, "menu-rapido-estudo.html"), "w", encoding="utf-8").write(html)
print("escrito: mockup/menu-rapido-estudo.html", len(html) // 1024, "KB")
