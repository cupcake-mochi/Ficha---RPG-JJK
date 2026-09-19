# -*- coding: utf-8 -*-
"""Deriva as duas versões (clara e escura) de cada paleta da lista grande.

Cada tema entra como as QUATRO cores de uma paleta real (Color Hunt, populares e
conferidas por curtida), sem escolha no olho. O script tira de cada paleta o
MATIZ e a SATURAÇÃO do texto e do acento — a identidade da cor —, e fixa a
LUMINOSIDADE de cada papel por regra, igual nos trinta temas: fundo e painel
sempre na mesma faixa de claro (ou de escuro), pra nenhum tema pastel virar um
"escuro" fraco e nenhum tema já escuro virar um "claro" sem contraste. Cada
par é medido contra WCAG (4,5 pra texto, 3,0 pra acento, com folga de segurança
até 4,7 e 3,3) contra o fundo E contra o painel; quem não passa é ajustado
automaticamente, sem trocar de matiz, até passar ou até o script avisar.
"""
import colorsys
import json

def rgb(h): return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
def hexa(t): return "%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in t)

def lum(h):
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return sum(k * f(c / 255) for k, c in zip((0.2126, 0.7152, 0.0722), rgb(h)))

def contraste(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

def hls(h):
    r, g, b = [c / 255 for c in rgb(h)]
    return colorsys.rgb_to_hls(r, g, b)

def de_hls(hh, l, s):
    l = max(0.0, min(1.0, l))
    s = max(0.0, min(1.0, s))
    r, g, b = colorsys.hls_to_rgb(hh, l, s)
    return hexa([c * 255 for c in (r, g, b)])

def saturacao(h):
    return hls(h)[2]

# ---------------------------------------------------------------------------
# AS TRINTA — nome escolhido, as quatro cores são a paleta real, sem mudar
# nenhum hex. Fonte: colorhunt.co/palettes/popular, /dark, /pastel — filtradas
# por curtida, 17/09/2026.
TEMAS = {
    "Blush":            ["4A4A4A", "E2B4BD", "F7D6D0", "FFF5F5"],
    "Crepúsculo":       ["FFEBB8", "EA9D9D", "BD5579", "601D49"],
    "Alfazema":         ["946D6D", "A290B7", "B0CDE6", "FDF4D2"],
    "Meia-Noite":       ["ABD2FA", "7692FF", "1B2CC1", "091540"],
    "Pôr do Sol":       ["FF7E7E", "FFA259", "FFCB56", "FFEDB9"],
    "Sálvia":           ["EEEEEE", "EAE2D6", "F7F2EB", "8B9A6E"],
    "Recife":           ["CCFBFA", "B1E5E6", "F7ADAD", "F29191"],
    "Vinho":            ["D45060", "FFF9F2", "F3E6D5", "800020"],
    "Neon":             ["FFD51E", "FF467A", "AB03A9", "5003C0"],
    "Oceano Profundo":  ["15D8B3", "49A4BB", "2E6FA0", "2F39A9"],
    "Tropical":         ["118AB2", "06D6A0", "FFD166", "FF7F50"],
    "Obsidiana":        ["E1DCC9", "412D15", "1F150C", "000000"],
    "Brasa":            ["E6501B", "C3110C", "740A03", "280905"],
    "Sangue":           ["3A2525", "9E2A3A", "FF0000", "000080"],
    "Abismo":           ["320A6B", "065084", "0F828C", "78B9B5"],
    "Arcano":           ["FFCC00", "B13BFF", "471396", "090040"],
    "Rubi":             ["EF88AD", "A53860", "670D2F", "3A0519"],
    "Ardósia":          ["DFD0B8", "948979", "393E46", "222831"],
    "Musgo":            ["1F7D53", "255F38", "27391C", "18230F"],
    "Terra":            ["DCD7C9", "A27B5C", "3F4F44", "2C3930"],
    "Eclipse":          ["000000", "0B192C", "1E3E62", "FF6500"],
    "Oliva":            ["ECDFCC", "697565", "3C3D37", "181C14"],
    "Púrpura Real":     ["EBD3F8", "AD49E1", "7A1CAC", "2E073F"],
    "Céu de Verão":     ["F2EFE7", "C8DFDB", "66A3BF", "3368A0"],
    "Cerâmica":         ["FDF0D5", "E76F51", "E9C46A", "249D8F"],
    "Algodão-Doce":     ["C5B3D3", "F5CBCB", "FFE2E2", "FBEFEF"],
    "Eucalipto":        ["E6F2DD", "B1D3B9", "88BDA4", "659287"],
    "Pêssego":          ["FFF0BE", "FFD6A6", "FFB399", "FF9A86"],
    "Outono":           ["FF7444", "FFF8DE", "B7BDF7", "576A8F"],
    "Aquarela":         ["D9F9DF", "AEE2FF", "B5BAFF", "9FA1FF"],
}

# A segunda leva, pedida pelo Mizuki depois de aprovar a primeira: comemorativas
# (ocidentais e asiáticas) e contos/criaturas/lendas da Ásia e do próprio anime.
# Mesma regra da primeira leva — nenhuma cor inventada, todas de paleta real do
# Color Hunt (populares, gold, christmas, halloween, cold), escolhida pelo
# tema e não pela paleta. A pesquisa de cor por trás de cada nome está no
# `mensagem-de-commit.txt` desta leva.
COMEMORATIVAS = {
    "Natal":              ["6D2323", "A31D1D", "E5D0AC", "FEF9E1"],
    "Halloween":          ["1B1833", "441752", "AB4459", "F29F58"],
    "Páscoa":             ["F6FFDC", "DAF9DE", "CFECF3", "F9B2D7"],
    "Réveillon":          ["000000", "E2DDB4", "F6EFD2", "E43636"],
    "Carnaval":           ["4D6787", "7DCCAD", "FFEA88", "F599C6"],
    "Ano Novo Chinês":    ["FCAD38", "EB7F31", "E45742", "972828"],
    "Tanabata":           ["FFF4B7", "006A67", "003161", "000B58"],
    "Hanami":             ["DC9B9B", "F6F4E8", "E5EEE4", "C0E1D2"],
    "Obon":               ["EDE4C2", "F5824A", "A03A13", "254F22"],
    "Setsubun":           ["FFCC00", "EB5B00", "B12C00", "640D5F"],
}
LENDAS = {
    "Kitsune":            ["FF5F00", "FF8C00", "FFC300", "FFD400"],
    "Tengu":              ["EEEAD7", "757D6F", "2D0000", "6D0808"],
    "Yuki-Onna":          ["0D47A1", "2196F3", "90CAF9", "E3F2FD"],
    "Kappa":              ["36ADA3", "2F578A", "232F72", "121358"],
    "Nekomata":           ["F97300", "E2DFD0", "524C42", "32012F"],
    "Ryu":                ["E8DDB4", "DEC384", "DAA464", "767F9E"],
    "Kirin":              ["F16767", "FF9B17", "FCB454", "FFF085"],
    "Kyuubi":             ["EA2F14", "E6521F", "FB9E3A", "FCEF91"],
    "Baku":               ["9290C3", "535C91", "1B1A55", "070F2B"],
    "Jorogumo":           ["910A67", "720455", "3C0753", "030637"],
    "Tanuki":             ["D99B7F", "A56F63", "464858", "0F3040"],
    "Nurarihyon":         ["000000", "854836", "FFB22C", "F7F7F7"],
    "Momotaro":           ["FFF6A1", "FDC086", "D46D25", "A4B885"],
    "Urashima Tarō":      ["F2F2ED", "7CD5C7", "118AB2", "464B71"],
    "Kaguya-Hime":        ["EAE0CF", "7288AE", "4B5694", "111844"],
    "Amaterasu":          ["F6CE71", "CC561E", "FF6500", "C40C0C"],
    "Vazio Infinito":     ["080616", "1A1953", "162E93", "2F2FE4"],
    "Santuário Malévolo": ["F14A00", "C62300", "500073", "2A004E"],
    "Dez Sombras":        ["211832", "412B6B", "5C3E94", "F25912"],
}

# As duas obrigatórias, fora das listas de cima porque não vêm do Color Hunt:
# Mizuki é a paleta do livro (v0.200, Neve Saturado); Noite é a roxa que a
# ficha já usa hoje. As duas entram pelo mesmo derivador, com o mesmo teste.
OBRIGATORIAS = {
    "Mizuki": ["251727", "BC2A6E", "F8C7DC", "FDF0F6"],  # tinta·acento·linha·washi
    "Noite":  ["120F1D", "756588", "3B3360", "F4F1F7"],  # fundo·claro·menu·texto
}

TUDO = {**OBRIGATORIAS, **TEMAS, **COMEMORATIVAS, **LENDAS}

# As faixas de luminosidade por papel, fixas nos trinta — é isso que garante
# que um tema pastel vire um "escuro" tão escuro quanto um tema que já
# nasceu escuro, e vice-versa. Medido para dar folga de contraste, não só o
# mínimo: ver a checagem no fim.
FAIXA = {
    "escuro": {"fundo": 0.09, "painel": 0.16, "painel_alto": 0.24, "texto": 0.94},
    "claro":  {"fundo": 0.97, "painel": 0.91, "painel_alto": 0.84, "texto": 0.10},
}


def papeis(cores):
    """Ordena as quatro por luminosidade: a mais escura e a mais clara dão
    matiz pro texto de cada modo; das duas do meio, a mais saturada vira
    acento e a outra vira a segunda linha (linha/texto_fraco)."""
    por_luz = sorted(cores, key=lum)
    escura, clara = por_luz[0], por_luz[-1]
    meio = sorted(por_luz[1:3], key=saturacao, reverse=True)
    acento, linha_base = meio
    return escura, clara, acento, linha_base


def com_luz(cor, l):
    hh, _, s = hls(cor)
    s = max(s, 0.12)  # nenhum papel nasce cinza puro só por causa da faixa fixa
    return de_hls(hh, l, s)


def com_luz_carater(cor, l, sat_min):
    """Como com_luz, mas com piso de SATURAÇÃO bem mais alto — porque em luminosidade muito baixa
    (perto de 0.05) o olho não distingue matiz nenhum, saturado ou não: qualquer cor vira "preto"
    igual. Existe só pro `tinta` (ver abaixo); os outros papéis moram em luminosidade alta o
    bastante pra 0.12 já bastar."""
    hh, _, s = hls(cor)
    s = max(s, sat_min)
    return de_hls(hh, l, s)


def corrige_contraste(cor, contra_a, contra_b, alvo, escurecer, passos=60):
    hh, l, s = hls(cor)
    passo = (l / passos) if escurecer else ((1 - l) / passos)
    melhor = cor
    for _ in range(passos):
        pior = min(contraste(de_hls(hh, l, s), contra_a), contraste(de_hls(hh, l, s), contra_b))
        melhor = de_hls(hh, l, s)
        if pior >= alvo:
            break
        l = l - passo if escurecer else l + passo
        l = max(0.02, min(0.98, l))
    return melhor, min(contraste(melhor, contra_a), contraste(melhor, contra_b))


def com_sat(cor, l, fator_sat):
    hh, _, s = hls(cor)
    s = max(0.12, min(1.0, s * fator_sat))
    return de_hls(hh, l, s)


def deriva_variante(escura, clara, acento, linha_base, modo):
    F = FAIXA[modo]
    ancora = escura if modo == "escuro" else clara
    fundo = com_luz(ancora, F["fundo"])
    painel = com_luz(ancora, F["painel"])
    painel_alto = com_luz(ancora, F["painel_alto"])
    linha = com_luz(linha_base, F["painel_alto"])
    texto = com_luz(clara if modo == "escuro" else escura, F["texto"])
    texto_fraco = com_luz(linha_base, F["texto"] * (0.9 if modo == "escuro" else 1.08))
    ac = acento

    # As seis a mais que o vocabulario do estilo.py tem e o gabarito de sete
    # nao cobria: tinta, papel e painel_baixo sao mais um degrau da MESMA
    # familia do fundo — tinta e sempre a tinta mais escura que existe, papel
    # e painel_baixo ficam entre fundo e painel. Bloco e mais um degrau da
    # familia da linha, entre ela e o texto fraco. Menu_grande e regua sao
    # as duas que a ficha usa sem nomear em lugar nenhum — a saturacao delas
    # e maior de proposito, porque uma delas e borda e a outra e caixa de
    # menu grande, e as duas precisam se destacar do fundo mais que um painel.
    #
    # 19/09/2026, pedido do Mizuki testando no Sheets: com luminosidade 0.05 e o piso de saturação
    # de com_luz (0.12), o tinta de QUALQUER tema vira essencialmente preto puro — o olho não
    # distingue matiz nenhum perto de L=0.05, saturado ou não, porque a luminosidade já é baixa
    # demais pra carregar cor. O sintoma: a CARTEIRA inteira (ela pinta o corpo principal com
    # tinta, não fundo) e a lombada das outras abas pareciam "não mudar" ao trocar de tema, mesmo
    # tendo mudado de verdade por trás — 0F0910 e 0A0810 são hex diferentes, mas indistinguíveis a
    # olho nu. Testado contra as 61 paletas reais (não só uma amostra): a combinação L=0.06 com
    # piso de saturação 0.50 é a mais alta que cabe SEM nenhuma das 61 ficar mais clara, em
    # luminância WCAG de verdade (não só em L do HLS), que o fundo escuro correspondente — o
    # Sálvia (o mais verde, e verde pesa mais na fórmula de luminância) é quem menos folga sobra,
    # e mesmo ele passa com folga real. Resultado: cada tema carrega um matiz de tinta bem mais
    # perceptível (ex.: Mizuki vai de "0F0910" pra algo bem mais magenta-escuro), sem deixar de
    # ser a cor mais escura da ficha.
    tinta = com_luz_carater(escura, 0.06, 0.50)
    #
    # Ainda 19/09/2026, o "problema grande" do Mizuki: o tinta ficava ESCURO também nos temas
    # claros — a CARTEIRA inteira e a lombada das outras abas saíam marrom-quase-preto no "Brasa ·
    # Claro", no meio de uma ficha que era toda pêssego. Quem escolhe a versão clara quer o tema
    # INTEIRO claro, então nos claros o tinta vira um pastel do mesmo matiz, um degrau abaixo do
    # fundo (0.94 contra 0.97), pra o cartão ainda se destacar do cabeçalho. O que ficava sobre ele
    # com fonte clara (o selo, a lombada) passa a ser resolvido pela rede de segurança de
    # legibilidade do repintarPaleta_, que troca a fonte por uma cor da paleta que leia.
    if modo == "claro":
        tinta = com_luz_carater(ancora, 0.94, 0.55)
    if modo == "escuro":
        papel = com_luz(ancora, F["fundo"] * 1.35)
        painel_baixo = com_luz(ancora, F["fundo"] * 1.75)
        regua_l, menu_l = 0.60, F["painel_alto"] * 0.90
    else:
        papel = com_luz(ancora, 1 - (1 - F["fundo"]) * 1.35)
        painel_baixo = com_luz(ancora, 1 - (1 - F["fundo"]) * 1.75)
        regua_l, menu_l = 0.40, 1 - (1 - F["painel_alto"]) * 0.90
    bloco = com_luz(linha_base, (F["painel_alto"] + F["texto"] * 0.9) / 2)
    menu_grande = com_sat(painel_alto, menu_l, 1.35)
    regua = com_sat(ancora, regua_l, 1.30)

    avisos = []
    pior_texto = min(contraste(texto, fundo), contraste(texto, painel))
    if pior_texto < 4.7:
        texto, pior_texto = corrige_contraste(
            texto, fundo, painel, 4.7, escurecer=(modo == "claro"))
        avisos.append(f"texto ajustado (ficou {pior_texto:.2f})")

    pior_ac = min(contraste(ac, fundo), contraste(ac, painel))
    if pior_ac < 3.3:
        ac, pior_ac = corrige_contraste(
            ac, fundo, painel, 3.3, escurecer=(modo == "claro"))
        avisos.append(f"acento ajustado (ficou {pior_ac:.2f})")

    pior_regua = contraste(regua, fundo)
    if pior_regua < 1.8:
        regua, pior_regua = corrige_contraste(
            regua, fundo, fundo, 1.8, escurecer=(modo == "claro"))
        avisos.append(f"régua ajustada (ficou {pior_regua:.2f})")

    return {
        "fundo": fundo, "painel": painel, "painel_alto": painel_alto,
        "linha": linha, "texto": texto, "texto_fraco": texto_fraco,
        "acento": ac, "tinta": tinta, "papel": papel,
        "painel_baixo": painel_baixo, "bloco": bloco,
        "menu_grande": menu_grande, "regua": regua,
    }, {
        "texto/fundo": contraste(texto, fundo),
        "texto/painel": contraste(texto, painel),
        "acento/fundo": contraste(ac, fundo),
        "acento/painel": contraste(ac, painel),
        "texto/tinta": contraste(texto, tinta),
    }, avisos


def resolve_osso_por_papel(paleta, oposta, piso=4.5):
    """
    O OSSO (E8DCD4) não é um papel do estilo.py — é a cor de estado "vida
    cheia" (decisão A5), mas o gerador Python (aba_ficha.py, ficha-invocacao/
    gramatica.py e companhia) também usa ela como cor PADRÃO de texto em
    praticamente todo título e valor da ficha, sem relação com vida/energia.
    Achado testando no Sheets em 18/09/2026: numa paleta clara, esse texto
    fixo em osso (um creme claro, pensado pro fundo escuro de fábrica) fica
    quase invisível.

    Pedido do Mizuki: em vez de UM substituto por tema, um substituto POR
    PAPEL DE FUNDO — a caixa que hoje é osso pode estar sobre fundo, painel,
    painel_alto, menu_grande ou acento, e nenhum desses tem a mesma
    luminosidade dentro do mesmo tema. Pra cada papel, testa texto e
    texto_fraco da MESMA variante primeiro (harmonia visual com o resto do
    tema); se nenhum dos dois cruza o piso, tenta os da variante OPOSTA
    (escapa pro claro ou pro escuro, o que contrastar); se ainda assim
    nenhum cruza, fica com o melhor preto/branco puro que sobrar — nunca some
    o aviso, ele entra em PROBLEMAS pra alguém olhar.
    """
    candidatos_mesma = [paleta["texto"], paleta["texto_fraco"]]
    candidatos_outra = [oposta["texto"], oposta["texto_fraco"]]
    candidatos_extremos = ["FFFFFF", "000000"]

    resultado = {}
    avisos = []
    for papel, fundo_hex in paleta.items():
        melhor, melhor_c = None, -1.0
        for grupo in (candidatos_mesma, candidatos_outra, candidatos_extremos):
            for cand in grupo:
                c = contraste(cand, fundo_hex)
                if c > melhor_c:
                    melhor, melhor_c = cand, c
            if melhor_c >= piso:
                break
        resultado[papel] = melhor
        if melhor_c < piso:
            avisos.append(f"osso/{papel} sem candidato acima do piso (ficou {melhor_c:.2f})")
    return resultado, avisos


def resolve_aviso_por_papel(paleta, piso=4.5):
    """
    O ÂMBAR de texto PADRÃO (D89B3A) — o "sobrou ponto" da conferência da INVOCAÇÃO, o "MORRE DE
    VEZ" e outros títulos em destaque — é uma cor fixa que não é papel de tema. Testando no Sheets em
    19/09/2026 o Mizuki apontou que ele seguia amarelo em toda paleta ("vão precisar de sua fonte
    mudada, já que essas cores padrão muitas vezes não vão ser fáceis de se ajustar ao tema").

    Ela passa a seguir o ACENTO da paleta, que é o papel feito pra destacar — mas o acento cru só
    garante 3,3 de contraste contra fundo e painel, e essas células moram em painel e painel_alto:
    medido, o acento cru cai abaixo de 3,0 sobre o painel_alto em 45 de 244 combinações. Então, por
    PAPEL DE FUNDO (igual ao osso_por_papel), o acento é mantido se cruza o piso, e senão tem só a
    luminosidade ajustada — mesmo matiz, então continua reconhecível como o acento do tema — até
    cruzar. A direção do ajuste vem da luminância do fundo daquele papel (fundo claro escurece o
    texto, fundo escuro clareia), e não do modo do tema, porque num tema claro alguns papéis
    (texto, tinta) são escuros. Se nem assim cruzar, fica o melhor entre texto, texto_fraco, branco
    e preto — e o aviso entra em PROBLEMAS pra alguém olhar.
    """
    resultado, avisos = {}, []
    acento = paleta["acento"]
    for papel, fundo_hex in paleta.items():
        if contraste(acento, fundo_hex) >= piso:
            melhor = acento
        else:
            melhor, _ = corrige_contraste(acento, fundo_hex, fundo_hex, piso,
                                          escurecer=lum(fundo_hex) > 0.18)
        melhor_c = contraste(melhor, fundo_hex)
        if melhor_c < piso:
            for cand in (paleta["texto"], paleta["texto_fraco"], "FFFFFF", "000000"):
                c = contraste(cand, fundo_hex)
                if c > melhor_c:
                    melhor, melhor_c = cand, c
        resultado[papel] = melhor
        if melhor_c < piso:
            avisos.append(f"aviso/{papel} sem candidato acima do piso (ficou {melhor_c:.2f})")
    return resultado, avisos


RESULT = {}
PROBLEMAS = []
for nome, cores in TUDO.items():
    escura, clara, acento, linha_base = papeis(cores)
    RESULT[nome] = {}
    for modo in ("claro", "escuro"):
        paleta, medidas, avisos = deriva_variante(escura, clara, acento, linha_base, modo)
        RESULT[nome][modo] = {"cores": paleta, "contraste": medidas, "avisos": avisos}
        for par, c in medidas.items():
            piso = 4.5 if par.startswith("texto") else 3.0
            if c < piso:
                PROBLEMAS.append(f"{nome} · {modo} · {par} = {c:.2f} (< {piso})")
    for modo, oposto in (("claro", "escuro"), ("escuro", "claro")):
        osso, avisos_osso = resolve_osso_por_papel(
            RESULT[nome][modo]["cores"], RESULT[nome][oposto]["cores"])
        RESULT[nome][modo]["osso_por_papel"] = osso
        for a in avisos_osso:
            PROBLEMAS.append(f"{nome} · {modo} · {a}")
        aviso, avisos_aviso = resolve_aviso_por_papel(RESULT[nome][modo]["cores"])
        RESULT[nome][modo]["aviso_por_papel"] = aviso
        for a in avisos_aviso:
            PROBLEMAS.append(f"{nome} · {modo} · {a}")

print(f"{len(TUDO)} temas · {len(TUDO) * 2} entradas (claro + escuro cada)\n")
for nome in TUDO:
    for modo in ("claro", "escuro"):
        r = RESULT[nome][modo]
        av = f"  ⚠ {' · '.join(r['avisos'])}" if r["avisos"] else ""
        print(f"{nome:16} {modo:7} fundo #{r['cores']['fundo']}  texto #{r['cores']['texto']}"
              f"  acento #{r['cores']['acento']}  "
              f"[texto/fundo {r['contraste']['texto/fundo']:.1f} · texto/painel "
              f"{r['contraste']['texto/painel']:.1f} · acento/fundo "
              f"{r['contraste']['acento/fundo']:.1f} · acento/painel "
              f"{r['contraste']['acento/painel']:.1f}]{av}")

print()
if PROBLEMAS:
    print(f"{len(PROBLEMAS)} PROBLEMA(S) que o ajuste automático não resolveu:")
    for p in PROBLEMAS:
        print("  -", p)
else:
    print("Todas as", len(TUDO) * 2, "entradas passam no piso de contraste",
          "(4,5 texto · 3,0 acento, contra fundo E painel, com folga até 4,7 e 3,3;",
          "4,5 pro osso_por_papel e pro aviso_por_papel, contra cada um dos treze papéis).")

with open("paletas-grandes.json", "w", encoding="utf-8") as f:
    json.dump(RESULT, f, ensure_ascii=False, indent=2)
print("\nescrito: paletas-grandes.json")
