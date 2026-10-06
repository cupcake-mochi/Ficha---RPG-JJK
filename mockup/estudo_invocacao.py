# -*- coding: utf-8 -*-
"""Monta o estudo da aba de invocações (mockup/invocacao-estudo.html).

Pedido do Mizuki em 06/10/2026: refazer a ficha de invocação depois do livro reconstruído, com protótipos antes de
aplicar. A primeira rodada saiu como página de site com campos soltos, e ele recusou: "Eu estava pensando em ser algo
mais, visualmente atrativo, semelhante as outras paginas, sabe? Trazendo caixas, espaços para escrever, tendo sim partes
automatizadas, mas tendo como colocar a imagem da invocação, nome e afins", "pensei em fazer algo mais de lado, ai teria
o espaço retratil entre elas para mostrar cada uma ou n", e o estudo "no formato de ficha de excel/planilhas".

Então o estudo é a aba desenhada na grade da planilha, com o CSS do estudo da Ficha Pessoal (como os outros). As tabelas
de regra saem do manual.txt (capítulo 17, Construir invocações) e as peças do arquivo de dados da ficha
(catalogo-projeto-m.json). Os dois exemplos são os do livro: Cão de sombra e Vigia de papel. Nada de regra é digitado
aqui além das fichas de exemplo, e cada número delas é conferido contra o texto do livro logo abaixo.

    python3 mockup/estudo_invocacao.py
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))
FONTE = json.load(open(os.path.join(RAIZ, "manual-fonte.json"), encoding="utf-8"))
MAN = open(os.path.join(RAIZ, "manual.txt"), encoding="utf-8").read().split("\n")
INI = MAN.index("## 17. Construir invocações")
FIM = MAN.index("# Parte 5 — Mestrar e consultar")
CAP = MAN[INI:FIM]
TEXTO = "\n".join(CAP)


def tabela(cabecalho):
    """as fileiras da tabela do capítulo 17 que abre com esse cabeçalho, sem ele"""
    i = CAP.index(cabecalho)
    out = []
    for l in CAP[i + 1:]:
        if " | " not in l:
            break
        out.append([c.strip() for c in l.split(" | ")])
    return out


def faixa(t):
    a = [int(x) for x in re.findall(r"\d+", t)]
    return a[0], a[-1]


prog = []
for nivel, classe, basica, pontos in tabela("Nível | Classe máxima | Dano-base da básica | Pontos da especial nessa Classe"):
    de, ate = faixa(nivel)
    prog.append({"de": de, "ate": ate, "classe": int(classe), "basica": int(basica.split("d")[0]), "pontos": int(pontos)})
assert [p["classe"] for p in prog] == [1, 2, 3, 4, 5, 6, 7] and prog[0]["de"] == 1 and prog[-1]["ate"] == 30

limite = {int(c): int(m) for c, _p, _pe, m in tabela("Classe | Pontos | PE | Máximo de Melhorias")}
for c, p, pe, _m in tabela("Classe | Pontos | PE | Máximo de Melhorias"):
    assert int(pe) == 3 * int(c) and int(p) == prog[int(c) - 1]["pontos"], c

PESO = {"0": None, "Leve": "Leve", "Média": "Media", "Pesada": "Pesada"}
assert "Explosão, Aura, Cone e Linha exigem Área aberta. Cura, Apoio e Onda exigem Amparo aberto." in TEXTO
assert "Toque e Aura incluem Corpo a Corpo, com devolução Média nas especiais." in TEXTO
EXIGE = {"Explosão": "Área", "Aura": "Área", "Cone": "Área", "Linha": "Área", "Cura": "Amparo", "Apoio": "Amparo", "Onda": "Amparo"}
formas = {}
for nome, custa, aplic in tabela("Forma | Preço | Aplicação"):
    formas[nome] = {"custa": PESO[custa], "exige": EXIGE.get(nome), "aplic": aplic, "embutida": nome in ("Toque", "Aura")}
    assert CAT["formas"][nome]["custa"] == PESO[custa], nome          # o capítulo diz que mantém os preços comuns

alcance = {}
for linha in tabela("Forma | Classe 0 | Classes 1–5 | Classes 6–7"):
    for nome in re.split(r" e ponto de | e ", linha[0]):
        alcance[nome.strip()] = linha[1:]
area = {}
for linha in tabela("Área básica | Classe 0 | Especiais 1–6 | Especial 7"):
    for nome in re.split(r" e ", linha[0].split(":")[0]):
        area[nome.strip()] = {"mede": linha[0].split(":")[1].strip(), "v": linha[1:]}

talentos = [{"n": n, "ce": 1, "faz": f} for n, f, _ in tabela("Talento de CE1 | Função | Texto completo no Catálogo")]
for n, ce, f in tabela("Talento | CE | Função e localização no Catálogo"):
    talentos.append({"n": n, "ce": ce, "faz": f.split(". ")[0] + "."})
assert len(talentos) == 13

tipos = [{"n": n, "corpo": c, "ficha": f} for n, c, f in tabela("Tipo | Origem e corpo | Característica da ficha")]
aquis = [{"n": n, "custa": c, "evolui": e} for n, c, e in tabela("Aquisição | Investimento | Evolução")]

melhorias = {}
for nome, m in CAT["melhorias"].items():
    if m["peso"] == "VARIAVEL":                  # Condição: uma entrada por condição, com o peso dela
        for cond, peso in CAT["condicoes"].items():
            melhorias["Condição: " + cond] = {"familia": m["familia"], "peso": peso}
    else:
        melhorias[nome] = {"familia": m["familia"], "peso": m["peso"]}

# ---------- os dois exemplos do livro, e a prova de que são os do livro ----------
for frase in [
    "Força | Destreza | Constituição | Inteligência | Essência", "3 | 2 | 2 | 1 | 1", "0 | 2 | 2 | 3 | 2",
    "Ataque e CD | +4 e CD 12.", "Defesa sem equipamento | 10 + 2 + 1 = 13.", "Vida máxima | 7 + 5 × 1 = 12.",
    "Defesa sem equipamento | 10 + 2 + 2 = 14.", "Vida máxima | 7 + 5 × 4 = 27.",
    "Perícias treinadas | Atletismo, Furtividade, Percepção e Sobrevivência.",
    "Perícias treinadas | Acrobacia, Furtividade, Investigação, Percepção e Sobrevivência.",
    "Mira é Livre. Alcance e Controle são abertas",
    "As Famílias abertas são Amparo Livre, Auxiliares e Alcance.",
    "Especial de Classe 1. Toque + Precisão.", "A conta é 2 − 1 + 1 = 2d8.",
    "Especial de Classe 2. Apoio + Guarda + Empurrão.", "Sobram 4 − 2 − 1 = 1 ponto, convertido em 3 de vida temporária.",
    "Especial de Classe 1. Cura, sem Melhorias ou Restrições.", "Sobram 2 − 1 = 1d8 de cura",
    "Básica de Classe 0. Apoio + Impulso.", "Distribua 9 pontos entre Força, Destreza, Constituição, Inteligência e Essência.",
    "Vigor usa Constituição, Intelecto usa Inteligência e Espírito usa Essência.",
    "A entidade tem treino em 4 + metade da Inteligência, arredondada para baixo, perícias.",
    "Os espaços de especiais são metade de (2 + nível ÷ 2), arredondada para baixo.",
    "A entidade conhece uma básica até o nível 10 e duas a partir do nível 11.",
    "A entidade ganha um no nível 1 e outro nos níveis 6, 10, 14, 18, 22, 26 e 30.",
    "Entidade comum | 5 + Constituição + (3 + Constituição) × (nível − 1).",
    "Corpo amaldiçoado de criação | 5 + Constituição + (4 + Constituição) × (nível − 1).",
    "Some 10 + Destreza da entidade + metade da Essência ou da Inteligência do invocador, arredondada para baixo.",
    "CD das habilidades | 8 + atributo de acerto da entidade + maestria do invocador.",
    "Deslocamento terrestre-base: 9 m.",
]:
    assert frase in TEXTO, frase
CAMPO = "\n".join(MAN[MAN.index("## 16. Invocações em campo"):INI])
for frase in [
    "O custo normal de entrada é a maior Classe permitida pelo nível da entidade.",
    "pague o dobro do PE da entrada e sua Bônus",
    "Reserva máxima = nível da entidade × (1 + um terço da Essência dela, arredondado para baixo).",
    "Você pode manter duas entidades ativas ao mesmo tempo",
    "Cada corpo mantém uma especial aguardando execução: antecipada, preparada, Armado, Segura ou Carregar.",
]:
    assert frase in CAMPO, frase


def hab(nome="", como="", forma="Projétil", mel=(), res=(), classe=1):
    return {"nome": nome, "como": como, "forma": forma, "mel": (list(mel) + [""] * 4)[:4], "res": (list(res) + ["", ""])[:2], "classe": classe}


def ficha(**k):
    base = {"nome": "", "def": "", "corpo": "", "tipo": "Shikigami de técnica", "aquis": "Espaço conhecido", "nivel": 1,
            "atr": {"FOR": 0, "DES": 0, "CON": 0, "INT": 0, "ESS": 0}, "acerto": "", "trT": "", "fis": "Força",
            "per": [""] * 7, "livre": "", "a1": "", "a2": "", "bas": [hab(classe=0), hab(classe=0)],
            "esp": [hab() for _ in range(8)], "tal": [""] * 8, "desl": "9 m",
            "mesa": {"vida": "", "mov": "9 m", "bas": "Disponível", "ordem": "Nenhuma", "estado": "Guardada", "tarefa": "", "cond": ""}}
    base.update(k)
    return base


cao = ficha(
    nome="Cão de sombra",
    **{"def": "Um cão feito de sombra que reconhece vestígios de energia amaldiçoada e persegue o que seu invocador aponta."},
    corpo="Médio, quatro patas, sem mãos; usa a boca para segurar. Visão, audição e olfato comuns. Entende ordens faladas e responde por latidos e gestos.",
    atr={"FOR": 3, "DES": 2, "CON": 2, "INT": 1, "ESS": 1}, acerto="Força", trT="Físico", fis="Força",
    per=["Atletismo", "Furtividade", "Percepção", "Sobrevivência", "", "", ""], livre="Mira", a1="Alcance", a2="Controle",
    bas=[hab("Mordida", "Perfurante. Consome a atuação básica do cão.", "Toque", classe=0), hab(classe=0)],
    esp=[hab("Mordida precisa", "Perfurante. Não aplica condição nem deixa efeito contínuo.", "Toque", ["Precisão"])] + [hab() for _ in range(7)],
    tal=["Farejador"] + [""] * 7,
    mesa={"vida": "", "mov": "9 m", "bas": "Disponível", "ordem": "Nenhuma", "estado": "Em campo", "tarefa": "Perseguir a criatura apontada.", "cond": ""})
vigia = ficha(
    nome="Vigia de papel",
    **{"def": "Uma pequena figura de papel que registra os sons da missão e desdobra tiras para amparar pessoas."},
    corpo="Pequena, duas pernas, mãos de papel. Visão e audição comuns. Entende ordens faladas e reproduz gravações. Não voa.",
    atr={"FOR": 0, "DES": 2, "CON": 2, "INT": 3, "ESS": 2}, acerto="Inteligência", trT="Intelecto", fis="Destreza",
    per=["Acrobacia", "Furtividade", "Investigação", "Percepção", "Sobrevivência", "", ""], livre="Amparo", a1="Auxiliares", a2="Alcance",
    bas=[hab("Orientação", "O vigia aponta um apoio seguro com suas tiras: vantagem no próximo teste do aliado.", "Apoio", ["Impulso"], classe=0), hab(classe=0)],
    esp=[hab("Tiras de resgate", "O aliado recebe +2 na Defesa e pode aceitar ser movido até 6 m.", "Apoio", ["Guarda", "Empurrão"], classe=2),
         hab("Remendo de papel", "Não remove condições.", "Cura")] + [hab() for _ in range(6)],
    tal=["Talento Próprio"] + [""] * 7,
    mesa={"vida": "", "mov": "9 m", "bas": "Disponível", "ordem": "Nenhuma", "estado": "Em campo", "tarefa": "Amparar quem está na escada.", "cond": ""})
for f in (cao, vigia):
    for h in f["bas"] + f["esp"]:
        assert h["forma"] in formas and all(m == "" or m in melhorias for m in h["mel"]), h

dados = {
    "versao": CAT["_meta"]["versao"], "livro": FONTE["sha256"][:8],
    "prog": prog, "limite": limite, "formas": formas, "alcance": alcance, "area": area,
    "talentos": talentos, "tipos": tipos, "aquis": aquis,
    "familias": list(CAT["familias"].keys()), "melhorias": melhorias,
    "restricoes": {n: r["devolve"] for n, r in CAT["restricoes"].items()},
    "pericias": list(CAT["pericias"].keys()),
    "fichas": [cao, vigia, ficha()],
}

velho = open(os.path.join(AQUI, "ficha-pessoal-estudo.html"), encoding="utf-8").read()
css = re.search(r"<style>\n(.*?)</style>", velho, re.S).group(1)
modelo = open(os.path.join(AQUI, "invocacao-estudo.modelo.html"), encoding="utf-8").read()
assert modelo.count("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/") == 1 and modelo.count("/*DADOS*/") == 1
saida = modelo.replace("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/", css).replace(
    "/*DADOS*/", json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
destino = os.path.join(AQUI, "invocacao-estudo.html")
open(destino, "w", encoding="utf-8").write(saida)
print(f"{destino}: {len(saida) // 1024} KB · {len(melhorias)} Melhorias, {len(dados['restricoes'])} Restrições, "
      f"{len(formas)} Formas, {len(talentos)} talentos, {len(tipos)} tipos, {len(aquis)} aquisições")
