# -*- coding: utf-8 -*-
"""Lê do livro o que a FICHA AMALDIÇOADA calcula e o arquivo de dados ainda não tem, e grava em
ficha-v01/tecnica-do-livro.json.

    python3 ficha-v01/extrair_tecnica.py            # lê o livro e regrava o arquivo
    python3 ficha-v01/extrair_tecnica.py --confere  # só compara o arquivo com o livro, sem gravar

Por que este arquivo existe: o catalogo-projeto-m.json está na v0.258 e não traz as Passivas, as aptidões, as
escadas de alcance, o Domínio, a Técnica Máxima nem os pactos. O livro que o Mizuki escreve hoje (os capítulos em
Markdown, na pasta do sistema) está adiante dele. Pôr essas tabelas no catálogo é decisão do Mizuki, e até lá a aba
lê deste arquivo, que carrega a versão do livro de onde saiu. O gerador (ficha_amaldicoada.py) nunca lê o livro: lê
só este arquivo, que mora no repositório.

Nenhum número é digitado aqui. Tabela vira lista, lendo a tabela; número que o livro só escreve em frase é conferido
contra a frase, que tem de estar no capítulo palavra por palavra.
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
LIVRO = "/media/mizuki/HD Externo II/Claude/Claude 2/sistema/05-material/livro/manual"
ESTADO = "/media/mizuki/HD Externo II/Claude/Claude 2/sistema/ESTADO-ATUAL.md"
SAIDA = os.path.join(AQUI, "tecnica-do-livro.json")


def _cap(arquivo):
    return open(os.path.join(LIVRO, arquivo), encoding="utf-8").read()


def _limpa(c):
    return c.strip().replace("`", "").replace("**", "")


def tabela(texto, titulo, cabecalho=False):
    """as linhas da tabela que vem depois de **titulo**, como listas de células sem crase e sem negrito"""
    linhas = texto.split("\n")
    i = next(k for k, l in enumerate(linhas) if l.strip() == f"**{titulo}**")
    out = []
    for l in linhas[i + 1:]:
        if l.startswith("|"):
            cel = [_limpa(c) for c in l.strip().strip("|").split("|")]
            if not set("".join(cel)) <= set("-: "):
                out.append(cel)
        elif out:
            break
    return out if cabecalho else out[1:]


def regra_da_aptidao(texto, nome):
    """a caixa de regra da aptidão: o bloco de citação que abre com **Nome**, sem o parágrafo do requisito"""
    linhas = texto.split("\n")
    ini = next((k for k, l in enumerate(linhas) if l.startswith(f"> **{nome}**")), None)
    if ini is None:
        return ""
    bloco = []
    for l in linhas[ini:]:
        if not l.startswith(">"):
            break
        bloco.append(l[1:].strip())
    paragrafos = [p.strip() for p in "\n".join(bloco).split("\n\n") if p.strip() and not p.strip().startswith("Requisito")]
    t = " ".join(" ".join(p.split()) for p in paragrafos)
    t = re.sub(r"^\*\*[^*]+\*\*\s*—\s*", "", t).replace("`", "").replace("**", "").replace("*", "")
    return t[:1].upper() + t[1:]


def frase(texto, trecho):
    """o trecho tem de estar no capítulo, do jeito que está escrito aqui (sem a crase e o negrito do Markdown)"""
    limpo = " ".join(texto.replace("`", "").replace("**", "").replace("*", "").split())
    if trecho not in limpo:
        raise SystemExit(f"o livro nao tem mais a frase: {trecho!r}")
    return trecho


def prontos(fund, cat):
    """os feitiços prontos do capítulo de Fundamento, da tabela `Como foi montado`: são a prova da conta da aba,
    porque cada um traz o resultado que o livro imprime"""
    from math import ceil
    preco = lambda peso, c: {"Leve": ceil(c / 2), "Media": c, "Pesada": ceil(c * 1.5)}[peso]
    txt = fund[fund.index("## Feitiços prontos"):fund.index("### Técnicas Máximas")]
    out, classe, lib = [], None, False
    for l in txt.split("\n"):
        m = re.match(r"### Classe (\d)", l)
        if m:
            classe = int(m.group(1))
        elif l.startswith("### Liberações"):
            lib = True
        if not l.startswith("| `"):
            continue
        nome, como, resultado = [c.strip() for c in l.strip().strip("|").split("|")]
        f = {"nome": nome.strip("`"), "classe": classe, "lib": lib, "mel": [], "res": [], "livro": resultado.replace("`", "")}
        for peca in como.split(" · "):
            m = re.match(r"Classe (\d)$", peca)
            if m:
                f["classe"] = int(m.group(1)); continue
            n = re.match(r"`([^`]+)`", peca).group(1)
            valor = re.search(r"\(([−+])(\d+)", peca)
            if n in cat["formas"] and "forma" not in f:
                f["forma"] = n
            elif n in cat["restricoes"]:
                niveis = cat["restricoes"][n]["devolve"].split(" ou ")
                nv = [x for x in niveis if preco(x, f["classe"]) == int(valor.group(2))]
                assert valor.group(1) == "+" and nv, (f["nome"], peca)
                f["res"].append(n if len(niveis) == 1 else n + "|" + nv[0])
            else:
                assert (n in cat["melhorias"] or n in cat["condicoes"]) and valor.group(1) == "−", (f["nome"], peca)
                f["mel"].append(n)
        m = re.search(r"(\d+) dados viram", resultado) or re.search(r"(\d+)d8", resultado)
        t = re.search(r"(\d+) de vida temporária", resultado)
        f["dados"] = int(m.group(1)) if m else int(t.group(1)) // 3 if t else 0 if "zero dano" in resultado else None
        pe = re.search(r"(\d+) PE", resultado)
        if pe:
            f["pe"] = int(pe.group(1))
        out.append(f)
    return out


def extrai():
    fund, apt, pac, exp = _cap("40-fundamento.md"), _cap("45-aptidoes-e-refino.md"), _cap("65-pactos.md"), _cap("80-experiencia-e-progressao.md")
    cat = json.load(open(os.path.join(os.path.dirname(AQUI), "catalogo-projeto-m.json"), encoding="utf-8"))
    versao = re.search(r"\*\*Versão (v[\d.]+)\.\*\*", open(ESTADO, encoding="utf-8").read()).group(1)
    num = lambda s: int(re.search(r"\d+", s).group(0))

    esc = {l[0]: [d.strip() for d in l[1].split("→")] for l in tabela(fund, "Escadas")}
    base = {}
    for l in tabela(fund, "Base por Classe"):
        for forma in l[0].split(" e "):
            base[forma.strip()] = {"classe_0": l[1], "classes_1_a_5": l[2], "classes_6_e_7": l[3]}
    c0 = tabela(fund, "Classe 0", cabecalho=True)
    tm = [{"de": int(l[0].split(" a ")[0]), "ate": int(l[0].split(" a ")[1]), "dados": num(l[1]), "montagem": int(l[2]), "pe": int(l[3])}
          for l in tabela(fund, "Técnica Máxima")]
    dom = []
    for l in tabela(fund, "Degraus"):
        nivel = re.search(r"nível (\d+)", l[2])
        dom.append({"degrau": l[0], "espacos": num(l[1]), "nivel": int(nivel.group(1)) if nivel else None,
                    "refino": int(re.search(r"refino (\d+)", l[2]).group(1)), "abre_em": l[2], "acerto": l[3]})
    return {
        "_meta": {
            "o_que_e": "o que a FICHA AMALDIÇOADA calcula e o catalogo-projeto-m.json ainda não tem, lido dos capítulos do livro",
            "versao_do_livro": versao, "extraido_por": "ficha-v01/extrair_tecnica.py",
            "capitulos": ["40-fundamento.md", "45-aptidoes-e-refino.md", "65-pactos.md", "80-experiencia-e-progressao.md"],
            "aviso": "o catálogo está numa versão anterior do livro; levar estas tabelas para ele é decisão do Mizuki",
        },
        "passivas": [{"nome": l[0], "classe_passiva": l[1], "faz": l[2]} for l in tabela(fund, "Lista")],
        "classe_passiva": [{"classe_passiva": l[0], "custa": l[1], "nivel": int(l[2])} for l in tabela(fund, "Passivas")],
        "passivas_pagas": {"cinco": 5, "frase": frase(fund, "Máximo de cinco Passivas pagas.")},
        "regra_propria": {"frase": frase(fund, "1 espaço para a Classe Passiva 2, e 2 para a 3")},
        "aptidoes": [{"nome": l[0], "requisito": l[1], "classe_passiva": l[2], "escala": l[3], "faz": regra_da_aptidao(apt, l[0])}
                     for l in tabela(apt, "Como ler uma aptidão")],
        "aptidoes_de_graca": ["Cobrir-se de energia", "Canalizar energia"],
        "aptidoes_frases": [frase(apt, "Cobrir-se de energia e Canalizar energia já estão na sua ficha desde o refino 1"),
                            frase(apt, "Refino — mais um de refino, e uma aptidão. Se o seu refino já estiver no teto, você leva duas aptidões no lugar."),
                            frase(apt, "Ela é Classe Passiva 1 ou 2, nunca 3, e você só pode pegá-la uma vez na ficha inteira."),
                            frase(apt, "sem Traje e sem Revestimento, a sua proteção é 1/3 do refino + 1"),
                            frase(apt, "Redução de Dano de 1,5 × refino num golpe, por 2 PE"),
                            frase(apt, "1d4 no refino 1, 2d4 no 3, 3d4 no 6, 4d4 no 9. No refino 10 os dados viram d6: 4d6.")],
        "escadas": {"alcance": esc["Alcance"], "raio": esc["Esfera (raio)"], "comprimento": esc["Cone e Linha"]},
        "base_por_classe": base,
        "formas": [{"nome": l[0], "custa": l[1], "o_que_e": l[2], "resolve": l[3]} for l in tabela(fund, "Formas")],
        "toque": frase(fund, "Toque fica em 1,5 m em qualquer Classe."),
        "classe_0": {"niveis": [int(x) for x in c0[0][1:]], "quantos": [int(x) for x in c0[1][1:]], "dados": [num(x) for x in c0[2][1:]],
                     "frase": frase(fund, "Cabe uma Melhoria Leve e uma Restrição Leve numa Classe 0, tirando um dado para pagar."),
                     "nao_cura": frase(fund, "As Formas Cura e Onda ficam de fora dela.")},
        "liberacao": {"niveis": [10, 20, 30], "classe_minima": 3,
                      "frases": [frase(fund, "Você ganha uma no nível 10, outra no 20 e outra no 30."),
                                 frase(fund, "Cada uma é um feitiço de Classe 3 ou mais"),
                                 frase(fund, "+Classe em dados de dano em cima do que a montagem der."),
                                 frase(fund, "Custa a rodada inteira e +50% de PE, arredondando para cima."),
                                 frase(fund, "Não serve para cura")]},
        "tecnica_maxima": {"faixas": tm, "pe_por_classe": 5,
                           "frases": [frase(fund, "custa 5 × a sua maior Classe"), frase(fund, "Não aceita Restrição.")]},
        "dominio": {
            "degraus": dom,
            "pe_por_classe": 6, "pe_por_classe_sem_barreira": 7, "raio_por_refino": "1,5", "raio_da_incompleta": "7,5 m",
            "raio_sem_barreira": "200 m", "vida_da_barreira": 50,
            "frases": [frase(fund, "as duas cobram 6 × a sua maior Classe de PE"),
                       frase(fund, "−⅓ do refino de PE na incompleta, −metade do refino na completa"),
                       frase(fund, "Dura metade do refino em rodadas, no mínimo uma."),
                       frase(fund, "O domínio tem raio de 1,5 m × refino. A incompleta para em 7,5 m."),
                       frase(fund, "Por fora ela tem 50 × metade do refino de vida"),
                       frase(fund, "Sem barreira, abrir cobra 7 × a sua maior Classe de PE, e lá dentro cada feitiço custa maestria × 2 a menos"),
                       frase(fund, "O raio é de 200 m"),
                       frase(fund, "Nenhum feitiço custa menos de 1 PE.")],
        },
        "pactos": {"formas": [{"forma": l[0], "quando": l[1], "teto": l[2]} for l in tabela(pac, "Formas de pacto")],
                   "concede": [{"concede": l[0], "quem": l[1]} for l in tabela(pac, "O que um pacto permanente concede")],
                   "frase": frase(pac, "um número de pactos permanentes igual a metade da sua Essência, arredondando para baixo")},
        "leque": {"frases": [frase(exp, "Leque — mais um feitiço, que só pode ser feitiço, e uma Passiva."),
                             frase(exp, "Cada escolha de Leque abre uma vaga a mais no teto")]},
        "controle": {"frases": [frase(fund, "Se o dano final for um quarto do teto (o teto é 4 × Classe): os efeitos de Controle duram uma rodada a mais."),
                                frase(fund, "além da rodada extra, a CD contra esses efeitos sobe +2")]},
        "numeros_da_montagem": [{"classe": int(l[0]), "pontos": int(l[2]), "leve": int(l[3]), "media": int(l[4]), "pesada": int(l[5]),
                                 "devolucao": int(l[6]), "teto": int(l[8])} for l in tabela(fund, "Números da montagem")],
        "melhorias_por_classe": tabela(fund, "Melhorias e Restrições por Classe"),
        "feiticos_prontos": prontos(fund, cat),
    }


if __name__ == "__main__":
    if not os.path.isdir(LIVRO):
        print(f"o livro nao esta nesta maquina ({LIVRO}): nada foi lido.")
        sys.exit(0 if "--confere" in sys.argv else 1)
    novo = extrai()
    if "--confere" in sys.argv:
        velho = json.load(open(SAIDA, encoding="utf-8"))
        igual = json.dumps(velho, ensure_ascii=False, sort_keys=True) == json.dumps(novo, ensure_ascii=False, sort_keys=True)
        difere = [k for k in novo if json.dumps(velho.get(k), ensure_ascii=False, sort_keys=True) != json.dumps(novo[k], ensure_ascii=False, sort_keys=True)]
        print("o arquivo bate com o livro " + novo["_meta"]["versao_do_livro"] if igual else f"o arquivo NAO bate com o livro: {difere}")
        sys.exit(0 if igual else 1)
    json.dump(novo, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{SAIDA}: livro {novo['_meta']['versao_do_livro']} · {len(novo['passivas'])} Passivas, {len(novo['aptidoes'])} aptidões, "
          f"{len(novo['feiticos_prontos'])} feitiços prontos")
