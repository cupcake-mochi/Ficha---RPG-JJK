# -*- coding: utf-8 -*-
"""Le a Ficha (PROJETO M) 0.1 e escreve o layout.json que o monta.py replica.

Ele NAO copia bytes: ele extrai o DESENHO e limpa o ruido que o Google Sheets
deixou na ida e volta. As quatro limpezas, todas decididas pelo Mizuki:

  1. as celulas em Arial 10 preto -- 3165 delas, TODAS vazias. E o estilo de
     fabrica do Sheets em celula que o gerador nao pintou.
  2. a largura 3,63 volta a ser 4,0. O gerador escreve 4,0, o Sheets converte
     para pixel e devolve 3,63: e a mesma coluna.
  3. a condicional verde B7E1CD em D114 -- o "nao esta vazio" de fabrica do
     Google, numa linha sem conteudo.
  4. as tres barras "agora" voltam a =J23, =J27 e =J31. A planilha viva e onde
     ele joga, e ela exporta com o personagem em campo -- o molde nasce cheio.

O que ele PRESERVA: valor e formula de cada celula, as cinco fontes com
tamanho e cor, os preenchimentos, as bordas, o alinhamento, as mesclagens, as
alturas de linha, os menus suspensos, a formatacao condicional de estado da
decisao A5, as imagens e a ordem das abas.
"""
import json, os, re, shutil, sys, zipfile
from openpyxl import load_workbook
from openpyxl.worksheet.formula import ArrayFormula
from openpyxl.utils import get_column_letter as L

AQUI = os.path.dirname(os.path.abspath(__file__))
ORIG = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "original.xlsx")
SAIDA = os.path.join(AQUI, "layout.json")
ARTE = os.path.join(AQUI, "arte")
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), "ficha"))
from estilo import CORPO

# --- as quatro limpezas, nomeadas para o comparador poder cobra-las --------
RUIDO_FONTE = ("Arial", 10.0)          # limpeza 1
LARGURA_CERTA = 4.0                    # limpeza 2 (o Sheets devolve 3.63)
LARGURA_DO_SHEETS = 3.63

# limpeza 4: as tres barras "agora" voltam a nascer CHEIAS.
#
# D23, D27 e D31 sao vida, energia e integridade ATUAIS, e o desenho delas e'
# apontar para a maxima ao lado -- e' assim que a ficha nova nasce inteira. Mas
# a planilha viva e' onde o Mizuki JOGA: quando ele exporta com um personagem
# em campo, essas tres vem como numero (19, 8, 25 na exportacao de 07/09/2026),
# e o molde do repositorio passaria a nascer com a vida daquele personagem.
#
# Ela e' limpeza e nao conserto: o numero na planilha dele esta certo. O que
# esta errado e' ele virar molde.
# 17/09/2026: os enderecos deixaram de ser escritos aqui. O Mizuki inseriu linhas na FICHA, e
# D23/J23 viraram D26/J26 -- as tres barras e os quatro campos de mesa agora saem dos rotulos,
# depois que a planilha e lida (ver _derivar_enderecos, logo abaixo do load_workbook).
BARRAS_CHEIAS = {}
CF_DE_FABRICA = "FFB7E1CD"             # limpeza 3

# limpeza 5, de 14/09/2026: o estado de mesa que nao e desenho volta VAZIO.
#
# E a regra da limpeza 4 aplicada a mais quatro celulas -- o numero esta certo
# na planilha dele, e errado no molde. Os tres `_delta` o Codigo.gs apaga sozinho
# depois de aplicar (`e.range.clearContent()`), entao um 0 ali foi digitado. E o
# `equipamento` vazio quer dizer "usa a protecao da aptidao", que e o que a nota
# da propria celula diz: um 1 ali e a protecao de um personagem.
ESTADO_VAZIO = {}

# limpeza 6, de 14/09/2026, decidida pelo Mizuki: o Arial que sobra depois da limpeza 1
# vira a fonte de corpo. Ele aparece em celula que o Sheets pintou com o estilo dele,
# e fica fora das cinco fontes da decisao C4.
ARIAL_VIRA_CORPO = "Arial"

# limpeza 7, de 14/09/2026: o carimbo de versao volta a ser texto. Numa planilha em
# portugues o ponto e separador de milhar, e o Sheets leu "0.104" como 104. E ruido de
# ida e volta, como a largura 3,63 da limpeza 2. O texto volta a ser 0.NNN, o que a planilha
# escreveu -- e nao a versao do catalogo, que desde a v0.239 do sistema pode estar na frente
# da planilha viva (a DADOS sai do catalogo no monta.py, limpeza 8).
CARIMBO = {"DADOS": ["B1", "D1"]}

wb = load_workbook(ORIG)


def _derivar_enderecos(s):
    """as barras 'agora' e os campos de mesa da FICHA, achados pelo rotulo impresso.
    A barra e a celula abaixo do rotulo `X - Atual/Máxima`; a maxima e a primeira formula a
    direita dela na mesma linha que nao e o SPARKLINE. Os campos de mesa sao os de baixo do
    `± PERDA &/ou GANHO` e do `EQUIPAMENTO`."""
    barras, vazio = {}, []
    for lin in s.iter_rows():
        for c in lin:
            v = c.value.strip() if isinstance(c.value, str) else None
            if not v:
                continue
            abaixo = s.cell(row=c.row + 1, column=c.column)
            if v.endswith("- Atual/Máxima"):
                maxima = next((x for x in s[c.row + 1][c.column:]
                               if isinstance(x.value, str) and x.value.startswith("=")
                               and "SPARKLINE" not in x.value), None)
                if maxima is None:
                    raise SystemExit(f"nao achei a maxima da barra {v!r} na linha {c.row + 1}")
                barras[abaixo.coordinate] = "=" + maxima.coordinate
            elif v in ("± PERDA &/ou GANHO", "EQUIPAMENTO"):
                vazio.append(abaixo.coordinate)
    if len(barras) != 3 or len(vazio) != 4:
        raise SystemExit(f"esperava 3 barras e 4 campos de mesa na FICHA, achei {barras} e {vazio}")
    return {"FICHA": barras}, {"FICHA": vazio}


BARRAS_CHEIAS, ESTADO_VAZIO = _derivar_enderecos(wb["FICHA"])
estilos, indice = [], {}

def cor(c):
    if c is None or getattr(c, "rgb", None) in (None, "00000000"):
        return None
    rgb = c.rgb
    return rgb if isinstance(rgb, str) else None

def chave_estilo(cel):
    f, p, b, a = cel.font, cel.fill, cel.border, cel.alignment
    fonte = None
    if f and f.name:
        # limpeza 1: o Arial 10 de fabrica nao entra no estilo
        if not (f.name == RUIDO_FONTE[0] and f.sz == RUIDO_FONTE[1]):
            nome_f = f.name
            if nome_f == ARIAL_VIRA_CORPO:                     # limpeza 6
                nome_f = CORPO
                arial_trocadas.append(f"{cel.parent.title}!{cel.coordinate}")
            fonte = [nome_f, f.sz, cor(f.color), bool(f.b), bool(f.i)]
    fundo = cor(p.start_color) if (p and p.fill_type == "solid") else None
    bordas = None
    if b:
        lados = {}
        for lado in ("top", "bottom", "left", "right"):
            s = getattr(b, lado)
            if s and s.style:
                lados[lado] = [s.style, cor(s.color)]
        bordas = lados or None
    alinha = None
    if a and (a.horizontal or a.vertical or a.wrap_text or a.text_rotation):
        alinha = [a.horizontal, a.vertical, bool(a.wrap_text), a.text_rotation or 0]
    fmt = cel.number_format if cel.number_format != "General" else None
    return json.dumps([fonte, fundo, bordas, alinha, fmt], ensure_ascii=False,
                      sort_keys=True)

def idx_estilo(cel):
    k = chave_estilo(cel)
    if k == '[null, null, null, null, null]':
        return None
    if k not in indice:
        indice[k] = len(estilos)
        estilos.append(json.loads(k))
    return indice[k]

# A imagem DENTRO da celula some quando o Sheets exporta .xlsx. Desde 15/09/2026 o script poe as
# imagens na celula, entao a exportacao da planilha viva pode vir sem nenhuma: nesse caso a aba fica
# com as imagens do layout anterior, que passa a ser o dono delas, e o extrator avisa.
try:
    _ANTES = json.load(open(SAIDA, encoding="utf-8"))["abas"]
    IMAGENS_ANTES = {a["nome"]: a["imagens"] for a in _ANTES}
    TEXTOS_ANTES = {a["nome"]: [(r[0], r[1]) for r in a["celulas"]] for a in _ANTES}
except (OSError, ValueError, KeyError):
    IMAGENS_ANTES, TEXTOS_ANTES = {}, {}


def _linhas_movidas(nome, s):
    """{linha antiga: linha nova}, pelos textos que aparecem uma vez so nas duas versoes da aba.
    17/09/2026: o Mizuki inseriu linhas na FICHA, e o selo mantido do layout anterior ficava na
    linha 85 com a caixa dele indo para a 91."""
    def unicos(pares):
        d = {}
        for coord, v in pares:
            if isinstance(v, str) and v.strip() and not v.startswith("="):
                d.setdefault(v.strip(), []).append(int(re.sub(r"^[A-Z]+", "", coord)))
        return {k: l[0] for k, l in d.items() if len(l) == 1}
    antes = unicos(TEXTOS_ANTES.get(nome, []))
    agora = unicos((c.coordinate, c.value) for lin in s.iter_rows() for c in lin)
    return sorted((antes[k], agora[k]) for k in antes if k in agora)


def _move_linha(lin, pares):
    antes = [(a, b) for a, b in pares if a <= lin]
    if not antes:
        return lin
    a, b = max(antes)
    return lin + (b - a)

abas = []
IMAGENS_MANTIDAS = {}
barras_repostas = []
estado_limpo = []
arial_trocadas = []
carimbos = []
for nome in wb.sheetnames:
    s = wb[nome]
    celulas = []
    for lin in s.iter_rows():
        for c in lin:
            e = idx_estilo(c)
            if c.value is None and e is None:
                continue
            # ⚠ FORMULA MATRICIAL. O openpyxl devolve um objeto ArrayFormula, e
            # nao uma string -- e ele nao serializa em JSON. Ate a ficha ganhar
            # as cinco do INDEX/MATCH da aba INVOCACAO, este extrator nunca
            # tinha visto uma, e ele MORRIA no json.dump em vez de avisar.
            #
            # Guardamos o texto e a FAIXA dela. A faixa importa: numa matricial
            # de uma celula so ela e a propria celula, mas numa de varias ela
            # diz ate onde o resultado se espalha, e escrever so o texto
            # transformaria a formula numa comum, calada.
            v, ref = c.value, None
            if isinstance(v, ArrayFormula):
                v, ref = v.text, v.ref
            _cheia = BARRAS_CHEIAS.get(nome, {}).get(c.coordinate)
            if _cheia is not None and v != _cheia:
                barras_repostas.append(f"{nome}!{c.coordinate} {v!r} -> {_cheia}")
                v = _cheia
            if c.coordinate in ESTADO_VAZIO.get(nome, []) and v is not None:
                estado_limpo.append(f"{nome}!{c.coordinate} {v!r} -> vazio")
                v, ref = None, None
                if e is None:
                    continue
            if (c.coordinate in CARIMBO.get(nome, []) and isinstance(v, (int, float))
                    and not isinstance(v, bool)
                    and float(v).is_integer() and 0 < v < 1000):
                _txt = "0.%03d" % int(v)
                carimbos.append(f"{nome}!{c.coordinate} {v!r} -> {_txt!r}")
                v = _txt
            celulas.append([c.coordinate, v, e] + ([ref] if ref else []))

    # as colunas: o Sheets colapsa tudo num range so, e a largura volta a 4,0
    cols = []
    for k, v in s.column_dimensions.items():
        if v.width:
            larg = LARGURA_CERTA if abs(v.width - LARGURA_DO_SHEETS) < 0.01 else v.width
            cols.append([v.min, v.max, larg])
    linhas_h = [[int(k), v.height] for k, v in s.row_dimensions.items() if v.height]

    menus = []
    for v in s.data_validations.dataValidation:
        menus.append({"onde": str(v.sqref), "tipo": v.type, "formula": v.formula1,
                      "vazio_ok": bool(v.allow_blank),
                      "mostra_seta": not bool(v.showDropDown)})

    # a condicional: as de estado da A5 ficam, a verde de fabrica sai
    cfs = []
    for faixa in s.conditional_formatting:
        for r in faixa.rules:
            f_bg = None
            if r.dxf and r.dxf.fill and r.dxf.fill.bgColor:
                f_bg = cor(r.dxf.fill.bgColor)
            f_cor = None
            if r.dxf and r.dxf.font and r.dxf.font.color:
                f_cor = cor(r.dxf.font.color)
            if f_bg == CF_DE_FABRICA:          # limpeza 3
                continue
            # o Sheets exporta a formula entre aspas extras
            forms = [re.sub(r'^"|"$', "", x) for x in (r.formula or [])]
            cfs.append({"onde": str(faixa.sqref), "tipo": r.type,
                        "formula": forms, "cor_texto": f_cor, "fundo": f_bg})

    mescladas = [str(r) for r in s.merged_cells.ranges]

    imagens = []
    # A imagem que o script poe DENTRO da celula volta na exportacao ancorada no canto da caixa
    # mesclada, com tamanho de tela sem sentido (29x0) e a arte ja reduzida pelo Sheets. Lida assim,
    # ela desmontaria as caixas: a aba fica com as imagens do layout anterior, e a arte nao e regravada.
    _cantos = {(m.min_row, m.min_col) for m in s.merged_cells.ranges}
    _exp = list(getattr(s, "_images", []))
    if (_exp and IMAGENS_ANTES.get(nome)
            and all((im.anchor._from.row + 1, im.anchor._from.col + 1) in _cantos for im in _exp)):
        _pares = _linhas_movidas(nome, s)
        imagens = []
        for _im in IMAGENS_ANTES[nome]:
            _nova = dict(_im, lin=_move_linha(_im["lin"], _pares))
            if _nova["lin"] != _im["lin"]:
                print(f"  [aviso] {nome}: a imagem {_im['arquivo']} andou da linha {_im['lin']} para a "
                      f"{_nova['lin']}, com as linhas da aba")
            imagens.append(_nova)
        IMAGENS_MANTIDAS[nome] = len(imagens)
        print(f"  [aviso] {nome}: as {len(_exp)} imagens vieram de dentro da celula; ficaram as do layout anterior")
        _exp = []
    for i, im in enumerate(_exp):
        arq = f"{nome.lower().replace(' ', '-')}-{i+1}.png"
        try:
            dados = im.ref.getvalue() if hasattr(im.ref, "getvalue") else open(im.ref, "rb").read()
            open(os.path.join(ARTE, arq), "wb").write(dados)
        except Exception as exc:
            print(f"  [aviso] nao extrai a imagem {i+1} de {nome}: {exc}")
            continue
        a = im.anchor
        # O tamanho e o da TELA, e nao o do arquivo: a faixa de pincel tem 1600x120 no arquivo e
        # aparece com 1240x14 na planilha viva. O deslocamento dentro da celula entra junto, porque o
        # selo da FICHA nao comeca no canto dela. Ate 15/09/2026 aqui estavam im.width e im.height.
        ext = getattr(a, "ext", None)
        if ext is None:
            print(f"  [aviso] a imagem {i+1} de {nome} nao tem tamanho de tela no .xlsx; usei o do arquivo")
        imagens.append({"arquivo": arq, "col": a._from.col + 1, "lin": a._from.row + 1,
                        "larg": round(ext.width / 9525) if ext is not None else im.width,
                        "alt": round(ext.height / 9525) if ext is not None else im.height,
                        "desloc_x": round(a._from.colOff / 9525),
                        "desloc_y": round(a._from.rowOff / 9525)})
    if not imagens and IMAGENS_ANTES.get(nome):
        imagens = IMAGENS_ANTES[nome]
        print(f"  [aviso] {nome}: o .xlsx nao trouxe imagem, e ficaram as {len(imagens)} do layout anterior")

    abas.append({"nome": nome, "estado": s.sheet_state,
                 "linhas": s.max_row, "colunas": s.max_column,
                 "colunas_larg": cols, "linhas_alt": linhas_h,
                 "altura_padrao": s.sheet_format.defaultRowHeight,
                 "grade": bool(s.sheet_view.showGridLines),
                 "celulas": celulas, "mescladas": mescladas,
                 "menus": menus, "condicional": cfs,
                 "imagens": imagens})

layout = {
    "_meta": {
        "o_que_e": "o desenho da Ficha (PROJETO M) 0.1, extraido do .xlsx que o "
                   "Mizuki mandou. O monta.py replica isto.",
        "origem": os.path.basename(ORIG),
        # o comparador LE daqui em vez de guardar a propria copia: um numero,
        # um dono. Sem isto ele acusaria as tres como divergencia nao explicada.
        "barras_cheias": BARRAS_CHEIAS,
        "estado_vazio": ESTADO_VAZIO,
        "arial_vira_corpo": ARIAL_VIRA_CORPO,
        "carimbo_texto": CARIMBO,
        # o emissor precisa da largura que o Sheets exportou para achar o pixel dela
        "largura_limpa": {"exportada": LARGURA_DO_SHEETS, "no_layout": LARGURA_CERTA},
        # as abas cujas imagens a exportacao trouxe de dentro da celula, e ficaram as do layout anterior:
        # o comparador aceita a diferenca de tamanho nelas
        "imagens_mantidas": IMAGENS_MANTIDAS,
        "veio_do_sheets": "https://docs.google.com/spreadsheets/d/"
                          "1rH43Xw6nneXwIPkI1VpsnPPkTZTPIqbiocY0KQdPwZ8/edit",
        "limpezas": [
            "as celulas em Arial 10 preto, todas vazias, saem: e o estilo de "
            "fabrica do Sheets. Quantas sao, o comparador conta -- numero em "
            "prosa deriva, e este ja derivou de 3165 para 3161 numa edicao.",
            "a largura 3,63 volta a 4,0, que e o que o gerador escreve antes da "
            "ida e volta de unidade",
            "a condicional verde B7E1CD de D114, o 'nao esta vazio' de fabrica do "
            "Google, sai",
            "as tres barras 'agora' -- vida, energia e integridade -- voltam a "
            "apontar para a maxima (=J23, =J27, =J31). A planilha viva e onde o "
            "Mizuki JOGA, entao ela exporta com o personagem dele em campo; o "
            "molde tem de nascer cheio. Quantas foram repostas, o extrator conta: "
            + (", ".join(barras_repostas) if barras_repostas else "nenhuma nesta rodada"),
            "o estado de mesa que nao e desenho volta vazio: os tres campos de dano, "
            "que o Codigo.gs apaga sozinho, e o equipamento, que vazio usa a protecao "
            "da aptidao. E a regra da limpeza anterior aplicada a mais quatro celulas. "
            "O extrator conta: " + (", ".join(estado_limpo) if estado_limpo else "nenhuma nesta rodada"),
            "o Arial que sobra depois da primeira limpeza vira a fonte de corpo, decidido pelo "
            "Mizuki em 14/09/2026. Quantas, o extrator conta: " + str(len(arial_trocadas)),
            "o carimbo de versao que o Sheets em portugues leu como numero volta a ser o texto "
            "0.NNN. O extrator conta: " + (", ".join(carimbos) if carimbos else "nenhum nesta rodada"),
            "a aba DADOS sai do catalogo, e nao da exportacao: as doze listas das colunas A a L e o "
            "carimbo em B1 e D1. Decidido pelo Mizuki em 14/09/2026, quando o catalogo foi da v0.104 "
            "a v0.239 e a planilha viva ainda carregava o de antes. O monta.py aplica, e o comparador "
            "conta quantas celulas mudaram.",
            "o Teste de Resistencia treinado soma a maestria, e nao 2: a planilha viva somava a "
            "regra do manual da v0.104, e o capitulo 1 soma a maestria desde a v0.117 do sistema. E o "
            "B14. So o termo somado no treino das quatro formulas muda, e ele aponta para a celula que "
            "o indice publica com o nome que o catalogo da. O monta.py aplica, e o comparador conta.",
            "a Defesa aplica o uniforme, o escudo e o refino escolhido: o EQUIPAMENTO vira menu das "
            "combinacoes de uniforme e escudo, a tabela delas sai da chave equipamento_defesa do catalogo "
            "para a DADOS, e o REFINO ESCOLHIDO entra ao lado do BLOQUEAR, com o estilo dele. E o B3, na "
            "opcao A, decidida pelo Mizuki em 16/09/2026. O monta.py aplica, e o comparador conta.",
            "o indice da DADOS guarda o endereco em formula (ADDRESS), derivado dos rotulos da FICHA: "
            "em 17/09/2026 o Mizuki inseriu linhas pelo Sheets e o indice de texto ficou apontando para "
            "o lugar antigo. O monta.py aplica antes das outras limpezas, e o comparador conta.",
            "a ficha conta sozinha: o atributo grande soma o pequeno e o marco de Corpo, os X de Y de "
            "pontos, pericias, oficios, Testes de Resistencia, aptidoes e Passivas do Leque, o Marco "
            "Escolhido, o espaco de feitico do Leque, as Passivas divididas com duas linhas a mais, os "
            "rotulos com erro de digitacao e a coluna de oficio fixo que o livro nao tem. Pedido pelo "
            "Mizuki em 17/09/2026. O monta.py aplica, e o comparador conta.",
            "o desenho que a mesa pediu em 17/09/2026: a caixinha de Buff/Debuff ao lado da Defesa, da Iniciativa, "
            "da CD, da Conjuracao, do Corpo a Corpo, do A Distancia e do Deslocamento; o Marco Escolhido com "
            "Refino, Corpo e Leque; a foto maior na CARTEIRA, com a moldura redesenhada; o nome do sistema "
            "saindo da DADOS; o portador e o registrado por com texto de exemplo; o SERVIDOR USADO; e a coluna "
            "de respiro da direita na CARTEIRA, na INVOCACAO e no CATALOGO. O monta.py aplica antes de todas, e "
            "o comparador conta.",
        ],
        "onde_ela_vive": "Google Sheets. Por isso o IFS fica cru e o SPARKLINE "
                         "continua: no Excel os dois quebram, e isso esta aceito.",
    },
    "estilos": estilos,
    "abas": abas,
}
json.dump(layout, open(SAIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"layout escrito: {SAIDA}")
print(f"  {len(estilos)} estilos distintos")
for a in abas:
    print(f"  {a['nome']:10} {len(a['celulas']):>5} celulas · "
          f"{len(a['mescladas']):>3} mescl. · {len(a['menus'])} menus · "
          f"{len(a['condicional'])} cond. · {len(a['imagens'])} imgs")
