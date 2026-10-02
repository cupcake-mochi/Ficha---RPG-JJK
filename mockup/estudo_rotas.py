# -*- coding: utf-8 -*-
"""Monta o estudo da Ficha Amaldiçoada nas quatro rotas de criação (mockup/rotas-estudo.html).

Pedido do Mizuki em 02/10/2026: o menu rápido da seção 8 da FICHA vale para todo mundo, e a Ficha Amaldiçoada "tem q se
modificar para cada origem". Ele escolheu fazer esta rodada antes de construir o menu (A). O livro decide a rota pela
Origem: Fundamento (as cinco principais e a Restrição Celestial pelo corpo), Sem Técnica (a sub-origem), e a Técnica
Marcial, com energia (Corpo Amaldiçoado) e sem energia (Restrição Celestial pelo ramo sem energia).

O estudo desenha a seção da Técnica, o título do Domínio e a linha de caixas das aptidões, na largura da aba de verdade
(21 colunas de largura própria), em três formas de pôr na aba o que só uma rota tem. Os exemplos são as técnicas prontas
do livro: a Régua, a Redoma, a Fisga e a Bancada. Nenhum número de regra é digitado aqui.

    python3 mockup/estudo_rotas.py
"""
import json, os, re

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
LIVRO = "/media/mizuki/HD Externo II/Claude/Claude 2/sistema/05-material/livro/manual"
TEC = json.load(open(os.path.join(RAIZ, "ficha-v01", "tecnica-do-livro.json"), encoding="utf-8"))
CAT = json.load(open(os.path.join(RAIZ, "catalogo-projeto-m.json"), encoding="utf-8"))


def capitulo(arq):
    return open(os.path.join(LIVRO, arq), encoding="utf-8").read()


def limpa(t):
    return re.sub(r"[`*]", "", t).strip()


def tabela(arq, titulo, depois_de=None):
    """as linhas da tabela que vem depois de **titulo** (e, se dado, depois do cabeçalho `depois_de`), sem o cabeçalho"""
    txt = capitulo(arq)
    if depois_de:
        txt = txt[txt.index(depois_de):]
    linhas = txt.split("\n")
    i = next(k for k, l in enumerate(linhas) if l.strip() == f"**{titulo}**")
    out = []
    for l in linhas[i + 1:]:
        if l.startswith("|"):
            cel = [limpa(c) for c in l.strip().strip("|").split("|")]
            if not set("".join(cel)) <= set("-: "):
                out.append(cel)
        elif out:
            break
    return out


def ficha_pronta(arq, nome, titulo):
    """a ficha pronta do livro como {campo: valor}: a tabela de duas colunas que vem depois de ### Nome"""
    return {k: v for k, v in tabela(arq, titulo, depois_de=f"### {nome}")}


def sem_tipo(descricao):
    """a Descrição sem o "Tipo de dano: x." do fim, e o tipo à parte"""
    m = re.search(r"\s*Tipo de dano: ([^.]+)\.\s*$", descricao)
    return (descricao[:m.start()].strip(), m.group(1)) if m else (descricao, "")


regua = ficha_pronta("40-fundamento.md", "Régua", "Ficha de feitiço")
redoma = ficha_pronta("43-sem-tecnica.md", "Redoma", "Ficha de Fundamento")
fisga = ficha_pronta("42-tecnica-marcial.md", "Fisga", "Ficha de Técnica Marcial")
bancada = ficha_pronta("42-tecnica-marcial.md", "Bancada", "Ficha de Técnica Marcial")

# os grupos de arma por atributo de acerto (Técnica Marcial, rota de arma): a Lâmina Longa está nos dois
GRUPOS = {}
for atributo, _, quais in tabela("42-tecnica-marcial.md", "Grupos por atributo de acerto")[1:]:
    for g in quais.split(" · "):
        GRUPOS.setdefault(g, []).append(atributo)
SEMENTES = [s for s, _ in tabela("43-sem-tecnica.md", "Sementes")[1:]]
FAMILIAS = list(CAT["familias"])


def tecnica(ficha, nome, selo=None, semente=None, equipamento=None):
    desc, tipo = sem_tipo(ficha["Descrição"])
    return {"nome": nome, "tipo": tipo, "descricao": desc, "regra": ficha["Regra"].strip('"“”'),
            "livres": ficha["Livres"].split(" · "), "fechadas": ficha["Fechadas"].split(" · "),
            "selo": selo, "semente": semente, "equipamento": equipamento, "atributo": ficha.get("Atributo", ""),
            "passiva": ficha.get("Passiva", "")}


def grupos_da(ficha):
    return [{"grupo": g, "atributo": " ou ".join(GRUPOS[g])} for g in ficha["Grupos"].split(" · ")]


ferramenta = bancada["Ferramenta"]
ROTAS = [
    {"id": "fund", "nome": "Fundamento", "origem": "Latente", "criacao": "Fundamento, capítulo 9",
     "poderes": "Feitiços", "lib": "Liberação", "tm": "Técnica Máxima", "dom": True, "apt": "Aptidões", "escala": "Refino",
     "graca": ["Cobrir-se de energia", "Canalizar energia"], "muda": "Nada: o Fundamento é a rota que a aba já desenha.",
     "tec": tecnica(regua, "Régua", selo=regua["Selo"])},
    {"id": "sem", "nome": "Sem Técnica", "origem": "Latente · Sem Técnica", "criacao": "Sem Técnica, capítulo 11",
     "poderes": "Manejos", "lib": "Liberação", "tm": "Auge", "dom": False, "apt": "Aptidões", "escala": "Refino",
     "graca": ["Cobrir-se de energia", "Canalizar energia"],
     "muda": "Feitiço se lê Manejo, e Técnica Máxima se lê Auge. Sem Expansão de Domínio. A semente vem aberta, sem os "
             "gates de nível e de refino, e conta como uma aptidão a mais. A Regra é sobre a semente.",
     "tec": tecnica(redoma, "Redoma", selo="", semente=limpa(redoma["Semente"]))},    # o livro não traz o Selo da Redoma
    {"id": "corpo", "nome": "Corpo Amaldiçoado", "origem": "Corpo Amaldiçoado", "criacao": "Técnica Marcial, capítulo 10",
     "poderes": "Katas", "lib": "Ruptura", "tm": "Ōgi", "dom": False, "apt": "Aptidões", "escala": "Refino",
     "graca": ["Cobrir-se de energia", "Canalizar energia"],
     "muda": "Feitiço se lê Kata, Liberação Máxima se lê Ruptura, e Técnica Máxima se lê Ōgi. Sem Selo: o equipamento "
             "ocupa o lugar dele. Sem Expansão de Domínio, e a Extensão de Domínio não se compra.",
     "tec": tecnica(fisga, "Fisga", equipamento={"rota": "arma", "grupos": grupos_da(fisga)})},
    {"id": "celeste", "nome": "Restrição Celestial sem energia", "origem": "Restrição Celestial · sem energia",
     "criacao": "Técnica Marcial, capítulo 10, com o 13 no lugar do 12",
     "poderes": "Katas", "lib": "Ruptura", "tm": "Ōgi", "dom": False, "apt": "Bênçãos", "escala": "Lapidação",
     "graca": ["Defesa sem Armadura", "Estímulo Muscular"],
     "muda": "Feitiço se lê Kata, Liberação Máxima se lê Ruptura, e Técnica Máxima se lê Ōgi. Sem Selo: o equipamento "
             "ocupa o lugar dele. Sem Expansão de Domínio. Bênçãos e Lapidação no lugar das aptidões e do refino. PE se lê "
             "Pontos de Esforço.",
     "tec": tecnica(bancada, "Bancada", equipamento={"rota": "ferramenta", "ferramenta": ferramenta.split(".")[0],
                                                       "ataca": "Fere maldição" if "dá para usar para atacar" in ferramenta else "Não fere"})},
]
# a conta das caixas de aptidão de graça, no exemplo de refino (ou Lapidação) 6, pelas fórmulas que a aba já usa
REF = 6
CAIXAS = {"protecao": f"Proteção {REF // 3 + 1}", "arma": f"+{4 if REF >= 9 else 3 if REF >= 6 else 2 if REF >= 3 else 1}{'d6' if REF >= 10 else 'd4'} na arma",
          "reacao": f"RD {int(1.5 * REF)} por 2 PE", "ref": REF}

css = re.search(r"<style>([\s\S]*?)</style>", open(os.path.join(AQUI, "ficha-pessoal-estudo.html"), encoding="utf-8").read()).group(1)
modelo = open(os.path.join(AQUI, "rotas-estudo.modelo.html"), encoding="utf-8").read()
dados = {"rotas": ROTAS, "familias": FAMILIAS, "grupos": GRUPOS, "sementes": SEMENTES, "caixas": CAIXAS,
         "versao": TEC["_meta"]["versao_do_livro"]}
html = modelo.replace("/*CSS-DO-ESTUDO-DA-FICHA-PESSOAL*/", css).replace("/*DADOS*/", json.dumps(dados, ensure_ascii=False))
open(os.path.join(AQUI, "rotas-estudo.html"), "w", encoding="utf-8").write(html)
print("escrito: mockup/rotas-estudo.html", len(html) // 1024, "KB")
