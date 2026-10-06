# -*- coding: utf-8 -*-
"""Lê do livro o que a aba INVOCAÇÕES calcula, e grava em ficha-v01/invocacao-do-livro.json.

    python3 ficha-v01/extrair_invocacao.py            # lê o manual.txt e regrava o arquivo
    python3 ficha-v01/extrair_invocacao.py --confere  # só compara o arquivo com o manual.txt, sem gravar

O livro reconstruído trocou a invocação inteira: ela virou entidade, com ficha própria (capítulo 17, Construir
invocações) e regras de campo num capítulo à parte (16, Invocações em campo). O Evocador muda as duas (Famílias da
Trilha, escolhas a mais, aprimoramentos e o limite de ativas). O catalogo-projeto-m.json não tem nada disso; a aba lê
deste arquivo, que carrega de que livro saiu. O gerador (ficha_invocacoes.py) nunca lê o livro.

Nenhum número é digitado aqui. Tabela vira lista, lendo a tabela; o que o livro só escreve em frase entra como frase
conferida: ela tem de estar no manual palavra por palavra, e a conta que a aba faz com ela está escrita ao lado.
"""
import json, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SAIDA = os.path.join(AQUI, "invocacao-do-livro.json")


def ler():
    MAN = open(os.path.join(RAIZ, "manual.txt"), encoding="utf-8").read().split("\n")
    FONTE = json.load(open(os.path.join(RAIZ, "manual-fonte.json"), encoding="utf-8"))
    i16, i17, i18 = (MAN.index(t) for t in ("## 16. Invocações em campo", "## 17. Construir invocações", "# Parte 5 — Mestrar e consultar"))
    CAMPO, CONSTRUIR, TUDO = MAN[i16:i17], MAN[i17:i18], "\n".join(MAN)

    def tabela(cabecalho, onde):
        """as fileiras da tabela que abre com esse cabeçalho, sem ele"""
        if onde.count(cabecalho) != 1:
            raise SystemExit(f"extrair_invocacao: a tabela {cabecalho!r} aparece {onde.count(cabecalho)} vez(es)")
        out = []
        for l in onde[onde.index(cabecalho) + 1:]:
            if " | " not in l:
                break
            out.append([c.strip() for c in l.split(" | ")])
        return out

    def faixa(t):
        a = [int(x) for x in re.findall(r"\d+", t)]
        return a[0], a[-1]

    # --- as frases de que a aba tira uma conta: cada uma tem de estar no livro, e a conta fica escrita ao lado
    frases = {
        "atributos": ("Distribua 9 pontos entre Força, Destreza, Constituição, Inteligência e Essência.", "9 pontos"),
        "inicio": ("Cada atributo começa entre 0 e 3.", "de 0 a 3 na criação"),
        "marcos": ("Nos níveis 6, 10, 14, 18, 22, 26 e 30, acrescente 1 ponto a um atributo, até o máximo de 6.", "1 ponto por marco, teto 6"),
        "ataque": ("Ataque | d20 + atributo de acerto da entidade + maestria do invocador.", "acerto + maestria"),
        "cd": ("CD das habilidades | 8 + atributo de acerto da entidade + maestria do invocador.", "8 + acerto + maestria"),
        "tr": ("TR treinado | d20 + atributo do TR + maestria do invocador.", "atributo + maestria"),
        "tr_atributos": ("Físico usa Força ou Destreza, escolhida na montagem. Vigor usa Constituição, Intelecto usa Inteligência e Espírito usa Essência.", ""),
        "pericias": ("A entidade tem treino em 4 + metade da Inteligência, arredondada para baixo, perícias.", "4 + INT/2"),
        "vida": ("Entidade comum | 5 + Constituição + (3 + Constituição) × (nível − 1).", "5 + CON + (3 + CON) × (nível − 1)"),
        "vida_criacao": ("Corpo amaldiçoado de criação | 5 + Constituição + (4 + Constituição) × (nível − 1).", "5 + CON + (4 + CON) × (nível − 1)"),
        "defesa": ("Some 10 + Destreza da entidade + metade da Essência ou da Inteligência do invocador, arredondada para baixo.", "10 + DES + metade"),
        "deslocamento": ("Deslocamento terrestre-base: 9 m.", "9 m"),
        "basicas": ("A entidade conhece uma básica até o nível 10 e duas a partir do nível 11.", "1 até o 10, 2 do 11"),
        "espacos": ("Os espaços de especiais são metade de (2 + nível ÷ 2), arredondada para baixo.", "INT((2 + nível/2)/2)"),
        "talentos": ("A entidade ganha um no nível 1 e outro nos níveis 6, 10, 14, 18, 22, 26 e 30.", "1 + marcos"),
        "pe": ("A especial custa 3 × sua Classe real em PE a cada uso.", "3 × Classe"),
        "livre": ("Ao comprar uma Melhoria dessa Família, desconte metade da Classe real, arredondada para baixo, com desconto mínimo de 1. O preço final também tem mínimo de 1.", "MAX(1, preço − MAX(1, INT(Classe/2)))"),
        "forma_sem_livre": ("Formas não recebem desconto de Família Livre.", ""),
        "formas_exigem": ("Explosão, Aura, Cone e Linha exigem Área aberta. Cura, Apoio e Onda exigem Amparo aberto.", ""),
        "embutida": ("Toque e Aura incluem Corpo a Corpo, com devolução Média nas especiais.", ""),
        "devolucao": ("As Restrições devolvem pontos para pagar Forma e Melhorias, até 2 × a Classe real e até o total gasto nessas peças.", "MIN(devolução, 2 × Classe, gasto)"),
        "teto": ("O total não passa de 4 × Classe.", "4 × Classe"),
        "apoio": ("Em Apoio, cada ponto útil vira 3 pontos de vida temporária.", "3 por ponto"),
        "basica_leve": ("A básica pode ter uma Melhoria Leve. Retire um dado de seu dano-base para pagá-la.", "−1 dado"),
        "basica_restricao": ("Pode haver uma Restrição Leve, que precisa ser cumprida, mas não devolve pontos nem o dado gasto.", "não devolve"),
        "basica_sem": ("Cura e Onda não estão disponíveis na Classe 0.", ""),
        "controle": ("Uma especial com Melhoria de Controle e dano final de até a Classe real em dados recebe uma rodada adicional nos efeitos de Controle. Sem dano, recebe também +2 na CD desses efeitos.", ""),
        "resolucao": ("Na montagem, trocar ataque por TR, ou o contrário, não custa pontos. Registre o TR, a resolução e o resultado no sucesso.", ""),
        "tipo_de_dano": ("Escolha também um tipo de dano permitido pelo catálogo geral para cada ataque.", ""),
        "equipamento": ("Registre o equipamento usado, a proteção, os requisitos e a carga.", ""),
        "ativas": ("Você pode manter duas entidades ativas ao mesmo tempo", "2"),
        "entrada": ("O custo normal de entrada é a maior Classe permitida pelo nível da entidade.", "Classe máxima"),
        "retorno": ("pague o dobro do PE da entrada e sua Bônus", "2 × entrada"),
        "talisma": ("Na entrada comum, pague metade do custo normal, arredondada para cima, com mínimo de 1 PE.", "MAX(1, CEILING(entrada/2))"),
        "reserva": ("Reserva máxima = nível da entidade × (1 + um terço da Essência dela, arredondado para baixo).", "nível × (1 + INT(ESS/3))"),
        "carga": ("Uma entidade segue o limite geral de carga de 5 + Força, em Volume", "5 + Força"),
        "corpos": ("Você pode manter um total de corpos igual ao atributo escolhido para a Defesa das entidades + sua capacidade de entidades ativas.", "atributo + ativas"),
        "ordens": ("Cada corpo mantém uma especial aguardando execução: antecipada, preparada, Armado, Segura ou Carregar.", ""),
        "trunfos": ("Somente maldições domadas com técnica própria podem ter Liberação Máxima, Técnica Máxima e Expansão de Domínio.", ""),
        "liberacoes": ("A domada conhece uma no nível 10, duas no 20 e três no 30.", "10, 20 e 30"),
        "liberacao_pe": ("O custo é 3 × Classe × 1,5 PE, para cima.", "CEILING(4,5 × Classe)"),
        "liberacao_dados": ("Use os pontos da especial daquela Classe e acrescente Classe d8", "pontos + Classe d8"),
        "expansao_pe": ("Abrir custa sua Ação Completa, uma básica da domada e 6 × a maior Classe dela em PE. Abrir sem barreira custa 7 × essa Classe.", "6 × ou 7 × Classe"),
        "expansao_acerto": ("Um Acerto de dano da domada causa Classe d8.", "Classe d8"),
        "trilhas": ("Escolha uma Trilha no nível 2: Invocação Principal, Parceria ou Múltiplas Invocações.", ""),
        "principal_familias": ("A ficha da principal passa a ter quatro Famílias Fechadas e cinco abertas.", "5 abertas"),
        "principal_livre": ("Entre as abertas, escolha uma Família Livre adicional, totalizando duas.", "2 Livres"),
        "principal_escolhas": ("Nos níveis 8, 16 e 24 da invocação, acrescente uma escolha à ficha: uma capacidade básica de Classe 0, uma especial normal ou um talento de Categoria de Efeito 1", "3 escolhas"),
        "parceria_familias": ("A ficha passa a ter cinco Famílias Fechadas, quatro abertas e uma Livre.", "4 abertas"),
        "multiplas_familias": ("Sua ficha passa a ter cinco Famílias Fechadas e quatro abertas, mantendo uma Família Livre.", "4 abertas"),
        "multiplas_ativas": ("Durante o combate, seu limite é de quatro invocações ativas.", "4"),
        "vinculo": ("Você começa o combate com 0 Pontos de Vínculo. No começo de cada turno seu, enquanto consciente, recebe 1 ponto, até o máximo de 3.", "0 a 3"),
        "aprimoramento": ("Você mantém um aprimoramento em uma invocação por vez.", ""),
    }
    onde = {"ativas": CAMPO, "entrada": CAMPO, "retorno": CAMPO, "talisma": CAMPO, "reserva": CAMPO, "carga": CAMPO, "corpos": CAMPO,
            "ordens": CAMPO, "trunfos": CAMPO, "liberacoes": CAMPO, "liberacao_pe": CAMPO, "liberacao_dados": CAMPO,
            "expansao_pe": CAMPO, "expansao_acerto": CAMPO}
    T17, T16 = "\n".join(CONSTRUIR), "\n".join(CAMPO)
    for k, (f, _) in frases.items():
        texto = T16 if k in onde else TUDO if k in ("trilhas", "principal_familias", "principal_livre", "principal_escolhas",
                                                    "parceria_familias", "multiplas_familias", "multiplas_ativas", "vinculo",
                                                    "aprimoramento") else T17
        if f not in texto:
            raise SystemExit(f"extrair_invocacao: o livro não diz mais ({k}): {f!r}")

    # --- a progressão, os números da especial e as Formas
    prog = []
    for nivel, classe, basica, pontos in tabela("Nível | Classe máxima | Dano-base da básica | Pontos da especial nessa Classe", CONSTRUIR):
        de, ate = faixa(nivel)
        if not basica.endswith("d6"):
            raise SystemExit(f"extrair_invocacao: a básica não é mais em d6: {basica}")
        prog.append({"de": de, "ate": ate, "classe": int(classe), "basica": int(basica[:-2]), "pontos": int(pontos)})
    classes = [{"classe": int(c), "pontos": int(p), "pe": int(pe), "melhorias": int(m)}
               for c, p, pe, m in tabela("Classe | Pontos | PE | Máximo de Melhorias", CONSTRUIR)]
    if [p["classe"] for p in prog] != [c["classe"] for c in classes] or prog[0]["de"] != 1 or prog[-1]["ate"] != 30 \
            or any(a["pontos"] != b["pontos"] or b["pe"] != 3 * b["classe"] for a, b in zip(prog, classes)):
        raise SystemExit("extrair_invocacao: a progressão e a tabela de pontos e PE não batem")
    desconto = tabela("Classe da especial | 1 | 2 | 3 | 4 | 5 | 6 | 7", CONSTRUIR)[0]
    if desconto[0] != "Desconto da Família Livre" or [int(x) for x in desconto[1:]] != [max(1, c // 2) for c in range(1, 8)]:
        raise SystemExit("extrair_invocacao: o desconto da Família Livre não é mais metade da Classe para baixo, mínimo 1")
    reduzida = tabela("Classe real | 1 | 2 | 3 | 4 | 5 | 6 | 7", CONSTRUIR)[0]
    if [int(x) for x in reduzida[1:]] != [max(1, c - 1) for c in range(1, 8)]:
        raise SystemExit("extrair_invocacao: a Classe do efeito reduzido não é mais uma a menos, mínimo 1")
    reduzidas = [l[0] for l in tabela("Peça | Valor que usa a Classe reduzida", CONSTRUIR) if l[0] != "Formas de área"]
    reduzidas = [n.strip() for x in reduzidas for n in re.split(r" e ", x)]
    peso = {"0": None, "Leve": "Leve", "Média": "Media", "Pesada": "Pesada"}
    exige = {"Explosão": "Área", "Aura": "Área", "Cone": "Área", "Linha": "Área", "Cura": "Amparo", "Apoio": "Amparo", "Onda": "Amparo"}
    formas = [{"nome": n, "custa": peso[c], "exige": exige.get(n), "embutida": n in ("Toque", "Aura"), "aplicacao": a}
              for n, c, a in tabela("Forma | Preço | Aplicação", CONSTRUIR)]
    # o alcance e a área das entidades: a base de cada Forma, na Classe 0, nas Classes 1 a 5, na 6 e na 7 (o alcance
    # sobe na 6, a área só na 7)
    alc, area = {}, {}
    for linha in tabela("Forma | Classe 0 | Classes 1–5 | Classes 6–7", CONSTRUIR):
        for n in re.split(r" e ponto de | e ", linha[0]):
            alc[n.strip()] = [linha[1], linha[2], linha[3], linha[3]]
    for linha in tabela("Área básica | Classe 0 | Especiais 1–6 | Especial 7", CONSTRUIR):
        for n in re.split(r" e ", linha[0].split(":")[0]):
            area[n.strip()] = [linha[1], linha[2], linha[2], linha[3]]

    # --- os talentos, os tipos e as aquisições
    talentos = [{"nome": n, "ce": 1, "funcao": f} for n, f, _ in tabela("Talento de CE1 | Função | Texto completo no Catálogo", CONSTRUIR)]
    for n, ce, f in tabela("Talento | CE | Função e localização no Catálogo", CONSTRUIR):
        talentos.append({"nome": n, "ce": int(ce) if ce.isdigit() else [int(x) for x in re.findall(r"\d", ce)], "funcao": f.split(". ")[0] + "."})
    teto_ce = [{"niveis": [int(x) for x in re.findall(r"\d+", n)], "ce": int(c)} for n, c in tabela("Nível do ganho | CE máxima da escolha", CONSTRUIR)]
    tipos = [{"nome": n, "corpo": c, "ficha": f} for n, c, f in tabela("Tipo | Origem e corpo | Característica da ficha", CONSTRUIR)]
    aquisicoes = [{"nome": n, "custa": c, "evolui": e, "acompanha": "companha" in e} for n, c, e in tabela("Aquisição | Investimento | Evolução", CONSTRUIR)]
    familias = [l[0] for l in tabela("Família | Aplicações comuns", CONSTRUIR)]

    # --- os trunfos da domada
    maxima = []
    for nivel, dados, pontos, custo in tabela("Nível da domada | Dados fixos | Pontos de montagem | Custo", CAMPO):
        de, ate = faixa(nivel)
        maxima.append({"de": de, "ate": ate, "dados": dados, "pontos": int(pontos), "pe": int(custo.split()[0])})
    expansao = [{"degrau": n, "custa": a, "pede": q} for n, a, q in tabela("Desenvolvimento | Aquisição na domada | Requisitos", CAMPO)]
    carga = [{"classe": c, "adianta": a, "paga": p} for c, a, p in tabela("Classe da entidade | Adiantamento | Entrada carregada", CAMPO)]

    # --- o Evocador: os aprimoramentos, com o nível em que cada um chega
    a, b = MAN.index("### Usos dos aprimoramentos"), MAN.index("### Intervenções de Vínculo")
    aprimoramentos = [{"nome": m.group(1), "nivel": int(m.group(2))} for m in (re.match(r"^#### (.+) — nível (\d+)$", l) for l in MAN[a:b]) if m]
    if [x["nivel"] for x in aprimoramentos] != [2, 2, 2, 2, 7]:
        raise SystemExit(f"extrair_invocacao: os aprimoramentos do Evocador mudaram: {aprimoramentos}")
    danos = []
    for _g, lista in tabela("Grupo | Tipos", MAN[MAN.index("### Tipos de dano"):]):
        danos += [x.strip() for x in re.split(r", | e ", lista.rstrip("."))]
    if len(danos) != 15:
        raise SystemExit(f"extrair_invocacao: o livro tinha quinze tipos de dano, e tem {len(danos)}")

    # --- os dois exemplos do capítulo: a prova de que a conta da aba é a do livro
    exemplo = lambda *fr: [f for f in fr if f in T17] if all(f in T17 for f in fr) else (_ for _ in ()).throw(SystemExit(f"extrair_invocacao: um exemplo do capítulo 17 mudou: {[f for f in fr if f not in T17]}"))
    exemplo("3 | 2 | 2 | 1 | 1", "Ataque e CD | +4 e CD 12.", "Defesa sem equipamento | 10 + 2 + 1 = 13.", "Vida máxima | 7 + 5 × 1 = 12.",
            "TR treinado | Físico, usando Força: +4.", "Outros TR | Vigor +2, Intelecto +1, Espírito +1.",
            "Mira é Livre. Alcance e Controle são abertas", "No acerto, causa 1d6 de Perfurante.", "A conta é 2 − 1 + 1 = 2d8.",
            "No nível 5, terá 27 de vida, básica de 2d6 e acesso à Classe 2. Sua Mordida precisa poderá ser ampliada para 4d8 por 6 PE.",
            "A vida inteira é recalculada: 8 + 6 × 5 = 38.",
            "0 | 2 | 2 | 3 | 2", "Defesa sem equipamento | 10 + 2 + 2 = 14.", "Vida máxima | 7 + 5 × 4 = 27.", "TR treinado | Intelecto: +4.",
            "As Famílias abertas são Amparo Livre, Auxiliares e Alcance.", "Sobram 4 − 2 − 1 = 1 ponto, convertido em 3 de vida temporária.",
            "Sobram 2 − 1 = 1d8 de cura", "Fura custa 2, ou 1 se Mira for Livre.", "a versão com Mira Livre fica com 3d8",
            "Onda (2) + Impulso (1) + Gesto (devolve 1) cabe nos 2 pontos")

    return {
        "_meta": {"o_que_e": "o que a aba INVOCAÇÕES lê do livro e o catálogo não tem", "livro": FONTE["livro"],
                  "sha256_do_livro": FONTE["sha256"], "gerado_por": "ficha-v01/extrair_invocacao.py"},
        "frases": {k: {"livro": f, "conta": c} for k, (f, c) in frases.items()},
        "progressao": prog, "classes": classes, "marcos": [int(x) for x in re.findall(r"\d+", frases["marcos"][0])[:7]],
        "familias": familias, "formas": formas, "alcance": alc, "area": area, "reduzidas": reduzidas,
        "talentos": talentos, "teto_de_ce": teto_ce, "tipos": tipos, "aquisicoes": aquisicoes,
        "tecnica_maxima": maxima, "expansao": expansao, "carga_do_talisma": carga,
        "trilhas": ["Invocação Principal", "Parceria", "Múltiplas Invocações"], "aprimoramentos": aprimoramentos,
        "tipos_de_dano": danos, "ordens": ["Antecipada", "Preparada", "Armado", "Segura", "Carregar"],
    }


if __name__ == "__main__":
    novo = json.dumps(ler(), ensure_ascii=False, indent=1) + "\n"
    if "--confere" in sys.argv:
        velho = open(SAIDA, encoding="utf-8").read() if os.path.exists(SAIDA) else ""
        if velho != novo:
            raise SystemExit("o invocacao-do-livro.json não bate com o manual.txt: rode ficha-v01/extrair_invocacao.py")
        print("o invocacao-do-livro.json bate com o manual.txt")
    else:
        open(SAIDA, "w", encoding="utf-8").write(novo)
        d = json.loads(novo)
        print(f"{SAIDA}: {len(d['frases'])} frases conferidas, {len(d['formas'])} Formas, {len(d['talentos'])} talentos, "
              f"{len(d['tipos'])} tipos, {len(d['aquisicoes'])} aquisições, {len(d['aprimoramentos'])} aprimoramentos")
