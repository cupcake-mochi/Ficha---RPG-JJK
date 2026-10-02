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
                    "faz": f"Custa {dom['pe_por_classe']} × a maior Classe de PE, {dom['frases'][1].split(',')[0]}. {dom['frases'][2]}",
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

# o teto da aba, que o menu tem de comportar (B29): 36 lugares de feitiço, 3 Liberações, a Técnica Máxima, o Domínio,
# 12 Passivas e 12 aptidões
CAP = {"poderes": 36, "maximas": 5, "passivas": 12, "aptidoes": 12}

css = re.search(r"<style>([\s\S]*?)</style>", open(os.path.join(AQUI, "ficha-pessoal-estudo.html"), encoding="utf-8").read()).group(1)
modelo = open(os.path.join(AQUI, "menu-rapido-estudo.modelo.html"), encoding="utf-8").read()
dados = {"rotas": ROTAS, "cap": CAP, "nivel": NIVEL, "versao": TEC["_meta"]["versao_do_livro"]}
html = modelo.replace("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/", css).replace("/*DADOS*/", json.dumps(dados, ensure_ascii=False))
open(os.path.join(AQUI, "menu-rapido-estudo.html"), "w", encoding="utf-8").write(html)
print("escrito: mockup/menu-rapido-estudo.html", len(html) // 1024, "KB")
