# -*- coding: utf-8 -*-
"""O arnes da FICHA AMALDIÇOADA: planta um defeito de cada vez numa COPIA do repositorio, gera a ficha de novo e roda
o regressao-amaldicoada.py. Cada defeito tem de acender a checagem dele. Um teste que passa de primeira (e este passou)
so vale se tambem reprova o que esta errado.

Cada rodada gera a ficha e recalcula no LibreOffice, e leva cerca de um minuto: por isso ele e rodado a mao, e nao
mora no rodar-tudo.sh.

    python3 arnes-amaldicoada.py            # todas as perturbacoes
    python3 arnes-amaldicoada.py 3 7        # so a terceira e a setima
"""
import os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FORA = {".git", "mockup", "__pycache__", "repos", "repo-conserto", ".claude"}
FICHAS = "kaori,velho,meio,bordas,menu,sorteio-13,rota-sem,rota-corpo,rota-celeste,rota-fisga"
GER, MOD, EMI, COD = "ficha-v01/ficha_amaldicoada.py", "ficha/modelo.gs.js", "ficha/emitir_gs.py", "apps-script/Codigo.gs"
MEN, HAB = "ficha-v01/menu_rapido.py", "ficha-v01/habilidades.py"

# (o que e o defeito, arquivo, o trecho certo, o trecho errado, um pedaco do nome da checagem que tem de acender)
PERTURBACOES = [
    ("a Família Livre desconta 1 ponto, e não metade da Classe", GER,
     "return max(1, p - math.ceil(classe / 2)) if livre else p", "return max(1, p - 1) if livre else p", "cartas batem com a regra"),
    ("a devolução deixa de parar em 2 × Classe", GER,
     '''o["dv"] = f"=MIN(2*{Cc},{P('dv0')})"''', '''o["dv"] = f"={P('dv0')}"''', "cartas batem com a regra"),
    ("a Restrição vira dado: o que ela devolve além do gasto não some", GER,
     '''o["usa"] = f"=MIN({P('dv')},{P('g')})"''', '''o["usa"] = f"={P('dv')}"''', "cartas batem com a regra"),
    ("a Liberação Máxima não soma a Classe em dados", GER,
     '''o["d"] = f"=MAX(0,{P('s')})+{P('liberação')}*{Cc}"''', '''o["d"] = f"=MAX(0,{P('s')})"''', "toda caixa das 10 cartas bate com a regra"),
    ("a Liberação Máxima cobra o PE de um feitiço comum", GER,
     '''IF({P("liberação")}=1,CEILING(4.5*{Cc},1),3*{Cc})&" PE"''', '''IF({P("liberação")}=1,3*{Cc},3*{Cc})&" PE"''', "saem com os dados que o livro imprime"),
    ("a Queima deixa de acrescentar a metade dos dados", GER,
     'SOMAM_METADE = ("Salto", "Queima", "Estilhaço")', 'SOMAM_METADE = ("Salto", "Estilhaço")', "cartas batem com a regra"),
    ("o limite de Melhorias sobe um em toda Classe", GER,
     "            lim[c] = int(mel)", "            lim[c] = int(mel) + 1", "cartas batem com a regra"),
    ("o Ampliar cobra um PE a mais", GER,
     '''IF({P("liberação")}=1,{math.ceil(4.5 * k)},{3 * k})&" PE"''', '''IF({P("liberação")}=1,{math.ceil(4.5 * k)},{3 * k + 1})&" PE"''',
     "cartas batem com a regra"),
    ("o Ampliar refaz a conta sem o teto de devolução", GER,
     "MIN({2 * k},{P('dL')}*{math.ceil(k / 2)}+{P('dM')}*{k},{gk})", "MIN({P('dL')}*{math.ceil(k / 2)}+{P('dM')}*{k},{gk})", "cartas batem com a regra"),
    ("a escada de alcance sobe um degrau a mais", GER,
     "return escada[min(len(escada) - 1, i + degraus)]", "return escada[min(len(escada) - 1, i + degraus + 1)]", "cartas batem com a regra"),
    ("na Classe 0 a Restrição Leve volta a devolver o dado (o livro reconstruído tirou a devolução)", GER,
     "-IF({zz(2, n)}<>\"\",1,0)'),", "-IF({zz(2, n)}<>\"\",1,0)+IF(AND({zz(2, n)}<>\"\",{zz(3, n)}<>\"\"),1,0)'),", "a Classe 0, linha por linha"),
    ("os espaços de feitiço esquecem os marcos", GER,
     '''"espaços do nível": f"=2+INT({H['nível']}/2)+{H['marcos']}"''', '''"espaços do nível": f"=2+INT({H['nível']}/2)"''', "o Orçamento"),
    ("o feitiço do Leque não entra no que cabe", GER,
     '''"cabem": f"={H['espaços']}+{H['escolhas de Leque']}-''', '''"cabem": f"={H['espaços']}-''', "o Orçamento"),
    ("o pacto permanente que concede espaço não soma", GER,
     '''"espaços": f"={H['espaços do nível']}+{H['espaços de pacto']}"''', '''"espaços": f"={H['espaços do nível']}"''', "o Orçamento"),
    ("a Regra Própria cobra a Classe Passiva inteira", GER,
     '''"espaços da regra própria": f"=MAX(0,{H['classe passiva da regra própria']}-1)"''',
     '''"espaços da regra própria": f"={H['classe passiva da regra própria']}"''', "o Orçamento"),
    ("o raio da Expansão incompleta não para em 7,5 m", GER,
     '''"=" + virgula(f"MIN({teto_inc},{raio}*{REF})")''', '''"=" + virgula(f"{raio}*{REF}")''', "as três linhas do Domínio"),
    ("o desconto da incompleta usa metade do refino", GER,
     '''f'="−"&{terco}&" PE"', "Não fecha", "Rola"]''', '''f'="−"&{meio}&" PE"', "Não fecha", "Rola"]''', "as três linhas do Domínio"),
    ("a Passiva do Leque aceita uma vaga a mais que as escolhas", GER,
     '''IF({j}>{H["escolhas de Leque"]},"{T_ERRO} Vaga","Grátis")''', '''IF({j}>{H["escolhas de Leque"]}+1,"{T_ERRO} Vaga","Grátis")''',
     "as doze cartas de Passiva"),
    ("a Técnica Máxima paga a montagem nos preços da Classe 1", GER,
     '''"=" + "+".join(f"IF({k}=0,0,INDEX({PRECOS},{H['maior classe']},{k}))" for k in tm_cod)''',
     '''"=" + "+".join(f"IF({k}=0,0,INDEX({PRECOS},1,{k}))" for k in tm_cod)''', "a Técnica Máxima"),
    ("a Família Fechada deixa de ser acusada na Forma", GER,
     '''_se(f'{P("x0")}=1', f'"Família Fechada: a Forma "&{forma}'),''', '''_se(f'{P("x0")}=2', f'"Família Fechada: a Forma "&{forma}'),''',
     "cartas batem com a regra"),
    ("duas Restrições de frequência passam sem aviso", GER,
     '''for i in range(1, N_RES + 1)) + ">1",''', '''for i in range(1, N_RES + 1)) + ">2",''', "cartas batem com a regra"),
    ("os pares que o livro proíbe deixam de ser cobrados", GER,
     '''"pares": [(p["a"], p["b"]) for p in DEC["A3_incompatibilidades"]["pares"]],''', '''"pares": [],''', "cartas batem com a regra"),
    ("as aptidões compráveis contam as duas de graça", GER,
     '''-{len([a for a in R['aptidoes'] if a['gratis'] and not a['bencao']])})",''', '''-0)",''', "as aptidões compradas"),
    ("o preenchimento para baixo para uma linha antes do fim", MOD,
     "aba.getRange(b[0], b[1], 1, n).copyTo(aba.getRange(b[0] + 1, b[1], b[2] - b[0], n));",
     "aba.getRange(b[0], b[1], 1, n).copyTo(aba.getRange(b[0] + 1, b[1], b[2] - b[0] - 1, n));", "fórmulas montadas são as da planilha gerada"),
    ("as cópias expandidas esquecem os valores da fileira", MOD,
     "if (dentro(t[0]) && !escritas[(t[0] + dl) + ',' + t[1]]) spec.vals.push([t[0] + dl, t[1]].concat(t.slice(2)));",
     "if (false) spec.vals.push([t[0] + dl, t[1]].concat(t.slice(2)));", "rótulos, textos e valores de fábrica"),
    ("a mesclagem que não veio na cópia não é refeita", MOD,
     "      mesclar(spec.merges.filter(naCopia));\n    }", "    }", "mescla uma a uma e a aba sai igual"),
    # 01/10/2026, o retorno do Mizuki depois de usar a aba no Sheets (B31). A caixa de seleção do Selo saiu da carta, e a
    # perturbação dela saiu daqui.
    ("o título de seção volta a ter uma caixa ao lado", GER,
     '''f.add("faixa", "D", lin, "T", lin + FX - 1,''', '''f.add("faixa", "D", lin, "H", lin + FX - 1,''', "vai de ponta a ponta"),
    ("o último pacto cola no fim da aba", GER, "RESPIRO = 2 ", "RESPIRO = 0 ", "duas linhas de respiro"),
    ("o nome da carta volta para a tinta do painel", GER,
     '''"nome":      [["Castoro", 11.0, OSSO, False, False], ACENTO,''', '''"nome":      [["Castoro", 11.0, OSSO, False, False], ALTO,''',
     "está na cor de título"),
    ("o estado da carta abre em minúscula", GER, '''NA_REGRA = "Na regra"''', '''NA_REGRA = "na regra"''', "abre em letra minúscula"),
    ("a proteção do cobrir-se abre em minúscula", GER, """f'="Proteção "&(FLOOR({REF}/3,1)+1)'""", """f'="proteção "&(FLOOR({REF}/3,1)+1)'""", "abre em letra minúscula"),
    ("a conta de uma caixa calculada fica na aba, onde o script não sabe devolver", GER,
     '''and ix._lc(coord)[0] >= G["saltos"]]''', '''and ix._lc(coord)[0] >= 99999]''', "só apontam para uma célula"),
    ("os grupos que nascem abertos ficam fechados", MOD,
     "lin.slice().sort(function (a, b) { return a[3] - b[3]; }).forEach(function (g) { if (!g[2]) aba.getRowGroup(g[0], g[3]).expand(); });",
     "", "nascem abertas as seções"),
    ("o salto aponta para a própria caixa, e não para a seção", COD,
     "'&range=' + l['alvo do salto'] + '\",' + nome", "'&range=' + l['caixa do salto'] + '\",' + nome", "saltos da linha 7"),
    # 02/10/2026, a aba nas quatro rotas de criação
    ("a rota olha a Técnica Marcial antes da sem energia", GER,
     'IF(N({_conta_da_ficha(layout, "sem energia")})=1,4,IF(N({_conta_da_ficha(layout, "técnica marcial")})=1,3,',
     'IF(N({_conta_da_ficha(layout, "técnica marcial")})=1,3,IF(N({_conta_da_ficha(layout, "sem energia")})=1,4,', "os títulos das seções"),
    ("o Sem Técnica perde as Passivas da Técnica Marcial", GER, "AND({ROTA}>=2,${L(cPa + 4)}{n}=1)", "AND({ROTA}>=3,${L(cPa + 4)}{n}=1)",
     "o menu de Passiva traz as da rota"),
    ("o Corpo Amaldiçoado compra a Extensão de Domínio", GER, "IF(OR({ap(6, n)}=1,AND({ROTA}=3,{ap(7, n)}=1)),",
     "IF(OR({ap(6, n)}=1,AND({ROTA}=9,{ap(7, n)}=1)),", "o menu de aptidão traz as aptidões da rota"),
    ("a Lâmina Longa acerta sempre com Força", GER, 'N({F_("atr_Destreza")})>N({F_("atr_Força")})),"Destreza","Força")',
     '1=0),"Destreza","Força")', "cada grupo de arma com o atributo"),
    ("a CD do grupo esquece a maestria", GER, "cd_de = lambda v: f'(8+{MAE}+{v}+{buff_cd})'", "cd_de = lambda v: f'(8+{v}+{buff_cd})'",
     "cada grupo de arma com o atributo"),
    ("o Domínio gasta espaço fora do Fundamento", GER, '"espaços no domínio": f"=IF({ROTA}<>1,0,', '"espaços no domínio": f"=IF({ROTA}<>9,0,',
     "o Domínio gasta"),
    ("o título das Bênçãos fica com o refino", GER, "texto = f'=UPPER({ROT(\"aptidões\")}&\" e \"&{ROT(\"escala\")})'",
     "texto = f'=UPPER({ROT(\"aptidões\")}&\" e Refino\")'", "os títulos das seções"),
    ("a ferramenta que só se carrega fere maldição", GER, '"Não fere maldição: só as Katas ferem","Fere maldição")',
     '"Fere maldição","Fere maldição")', "se o golpe simples fere maldição"),
    ("o Estímulo dá dois usos antes da Lapidação 10", GER, "\"usos do estímulo\": f'=IF({H[\"refino\"]}>=10,2,1)",
     "\"usos do estímulo\": f'=IF({H[\"refino\"]}>=1,2,1)", "a linha do Estímulo Muscular"),
    # (até 02/10/2026 este trocava só o >=3 por >=2, e não mudava nada: o Sem Técnica cai na semente antes de chegar lá)
    ("o menu da peça da rota mostra o equipamento no Sem Técnica", GER,
     'IF({ROTA}=2,IFERROR(INDEX({D.faixa("sementes", so=0)},{k + 1}),""),IF({ROTA}>=3,',
     'IF({ROTA}=9,IFERROR(INDEX({D.faixa("sementes", so=0)},{k + 1}),""),IF({ROTA}>=2,', "o menu da peça da rota"),
    ("o Selo da Técnica Marcial fica com o nome de sempre", GER,
     '"selo": ["Selo", "Selo", "Selo · ter o equipamento em uso", "Selo · ter o equipamento em uso"]',
     '"selo": ["Selo", "Selo", "Selo", "Selo"]', "a linha da rota diz a rota"),
    ("o salto cita o texto, e não a célula do nome", COD, "var nome = l['nome do salto'] ? String(l['nome do salto']) :",
     "var nome = false ? String(l['nome do salto']) :", "citam a célula do nome na DADOS_AM"),
    ("o gerador compacta uma fileira que não é igual ao molde", EMI,
     "if de_onde(t[0]) is None or list(por.get((t[0] - de_onde(t[0]), t[1]), [None, None])[2:]) != list(t[2:])]",
     "if de_onde(t[0]) is None]", None),          # o proprio gerador para: a copia expandida nao devolve a aba
    # 02/10/2026, o menu rápido da FICHA (a seção 8), que lê a Ficha Amaldiçoada
    ("o menu de feitiço não compacta: o feitiço sem nome deixa buraco", MEN,
     '''[[k + 1, (lambda n, k=k: f"=IFERROR(MATCH({k + 1},{FEIT('ordem')},0),0)")] +''', '''[[k + 1, (lambda n, k=k: f"={k + 1}")] +''',
     "sem buraco, com a Classe"),
    ("a carta de feitiço mostra como resolve no lugar do Como é", MEN,
     '''f.add("desc", x, r + 2, x + W - 1, r + 1 + alt, ref(lc, linha, k(6)))''', '''f.add("desc", x, r + 2, x + W - 1, r + 1 + alt, ref(lc, linha, k(5)))''',
     "como resolve e o Como é"),
    ("as cartas saem da direita para a esquerda", MEN, "POR, W, X = 3, 13, (4, 19, 34)", "POR, W, X = 3, 13, (34, 19, 4)", "na ordem de leitura"),
    ("a Passiva sem texto do jogador fica em branco, sem o do livro", MEN,
     '''IF({faz}<>"","Do livro: "&{faz},"")''', '''IF({faz}<>"","","")''', "o texto do jogador ou o do livro"),
    ("o menu de Passiva não compacta", MEN,
     '''(lambda n, k=k: f"=IFERROR(MATCH({k + 1},{PCOL(8)},0),0)")''', '''(lambda n, k=k: f"={k + 1}")''', "as Passivas no menu, sem buraco"),
    ("a rota sem Domínio mostra a carta do Domínio", MEN,
     '''f'=IF({ROTA}<>1,"Esta rota não tem Expansão de Domínio",''', '''f'=IF({ROTA}<>9,"Esta rota não tem Expansão de Domínio",''',
     "a carta do Domínio"),
    ("a Técnica Máxima sem nome mostra a Forma de fábrica", MEN,
     '''f'=IF({fa._A(G["tm_nome"], AM)}="","",{fa._A(G["tm_forma"], AM)}&"")',''', '''f'={fa._A(G["tm_forma"], AM)}&""',''',
     "traz o nome, o PE, a Forma e o Como é dela"),
    ("o título do menu fica com o nome do Fundamento em toda rota", MEN,
     '''("título", f'="MENU RÁPIDO · "&UPPER({R_("feitiços")})&", TALENTOS E "&UPPER({R_("aptidões")})'),''',
     '''("título", '="MENU RÁPIDO · FEITIÇOS, TALENTOS E APTIDÕES"'),''', "os títulos do menu"),
    ("o menu mostra o texto inteiro do livro, mesmo o que não cabe na caixa", GER,
     'TETO_RESUMO = {"passiva": 260, "aptidao": 300}', 'TETO_RESUMO = {"passiva": 260, "aptidao": 3000}', "o texto do jogador ou o do livro"),
    ("a Técnica Máxima antes do nível dela mostra \"— PE\"", MEN,
     'IF(ISNUMBER({fa._A(G["tm_pe"], AM)}),{fa._A(G["tm_pe"], AM)}&" PE",{fa._A(G["tm_pe"], AM)}&"")',
     '{fa._A(G["tm_pe"], AM)}&" PE"', "traz o nome, o PE, a Forma e o Como é dela"),
    # 02/10/2026, as Habilidades na seção 7 da FICHA (B34)
    ("a etiqueta da carta só abre um nível depois", HAB, """f'=IF({NIV}>={n},"Nível {n}","Abre no {n}")'""",
     """f'=IF({NIV}>{n},"Nível {n}","Abre no {n}")'""", "as etiquetas dizem o nível ou quando a carta abre"),
    ("o Caminho volta aos quatro degraus de antes do livro novo", HAB, "NIV_CAMINHO, NIV_TRILHA = (2, 7, 15, 23, 30), (2, 11, 19, 27)",
     "NIV_CAMINHO, NIV_TRILHA = (2, 7, 15, 30), (2, 11, 19, 27)", "níveis de entrega da Progressão"),
    ("o título da Trilha esquece a Trilha escolhida", HAB, """["Trilha", f'="TRILHA"&{escolha("trilha")}&"  ·  QUATRO ENTREGAS"']""",
     """["Trilha", '="TRILHA  ·  QUATRO ENTREGAS"']""", "os títulos dizem o Caminho e a Trilha"),
    # 05/10/2026, as cartas com o livro (B37)
    ("a carta cola na seguinte, sem a linha vazia entre elas", HAB,
     "                r += 1                          # uma linha vazia entre uma carta e outra", "                r += 0",
     "há uma linha vazia"),
    ("o texto do livro deixa de separar os parágrafos (o json fica velho)", "ficha-v01/extrair_habilidades.py",
     '''out += "\\n" if tipo == blocos[k - 1][0] and tipo in ("tabela", "item") else "\\n\\n"''', '''out += "\\n"''',
     "é o que o extrair_habilidades.py tira do manual.txt hoje"),
    ("a caixa do texto deixa de abrir e fechar", HAB, "            grupos.append([r + 1, r + CAIXA, False])", "            pass",
     "grupo de linhas que abre e fecha"),
    ("a medida da carta esquece uma coluna", HAB, '"largura": W * PX_COLUNA - RESPIRO_PX', '"largura": (W - 1) * PX_COLUNA - RESPIRO_PX',
     "a medida da carta no Habilidades.gs é a da planilha"),
    ("o menu de Trilha volta a ter o Batedor sem rota", "ficha-v01/ficha_automatica.py",
     'out += [(f"{t} · {r}", c) for r in hab["rotas"][t]] if t in hab["rotas"] else [(t, c)]', "out += [(t, c)]",
     "com o Batedor aberto nas três rotas"),
    ("a segunda habilidade da carta perde o nome (a Execução Preparada)", "ficha-v01/extrair_habilidades.py",
     'sub = [("titulo", m.group(1))] if m and m.group(1).lower() != nome.lower() and m.group(1) in _nomes(nome) else []',
     "sub = []", "mostra o nome de cada uma que o livro abre"),
    # 05/10/2026, o nome da técnica espelha a TÉCNICA DECLARADA da CARTEIRA ("Espelha a CARTEIRA")
    ("a caixa NOME DA TÉCNICA volta a ser escrita à mão", "ficha-v01/ficha_amaldicoada.py",
     """f.caixa("D", "H", t, "NOME DA TÉCNICA", f'={_A(campo_da_tecnica(layout), "CARTEIRA!")}&""', nota=NOTAS["nome_tecnica"])""",
     """f.caixa("D", "H", t, "NOME DA TÉCNICA", nota=NOTAS["nome_tecnica"])""", "NOME DA TÉCNICA espelha"),
    ("o script não sabe que o nome da técnica vem da CARTEIRA", "ficha-v01/ficha_amaldicoada.py",
     '"da_carteira": [G["nome_tecnica"]],', '"da_carteira": [],', "NOME DA TÉCNICA espelha"),
    ("o campo da técnica sai uma linha abaixo do da CARTEIRA", "ficha-v01/ficha_amaldicoada.py",
     "campo = _a1(col, lin + 1)", "campo = _a1(col, lin + 2)", None),
]
CONTRA = ("um comentário a mais no gerador", GER, "def _se(cond, texto):", "# comentario que nao muda nada\ndef _se(cond, texto):")


def copia():
    d = tempfile.mkdtemp(prefix="arnes-amaldicoada-")
    for nome in os.listdir(AQUI):
        if nome in FORA:
            continue
        de = os.path.join(AQUI, nome)
        if os.path.isdir(de):
            shutil.copytree(de, os.path.join(d, nome), ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy(de, os.path.join(d, nome))
    # o gerador copia o CSS do estudo da Ficha Pessoal? Não: só o estudo lê a pasta mockup, e a ficha não depende dela.
    return d


def roda(pasta):
    """gera a ficha na copia e roda a regressao; devolve (parou o gerador?, codigo, saida)"""
    g = subprocess.run([sys.executable, "ficha-v01/monta.py"], cwd=pasta, capture_output=True, text=True)
    if g.returncode:
        return True, g.returncode, (g.stdout + g.stderr)[-400:]
    r = subprocess.run([sys.executable, "regressao-amaldicoada.py"], cwd=pasta, capture_output=True, text=True,
                       env={**os.environ, "AMALDICOADA_SO": FICHAS})
    return False, r.returncode, r.stdout + r.stderr


def aplica(pasta, arquivo, certo, errado):
    caminho = os.path.join(pasta, arquivo)
    s = open(caminho, encoding="utf-8").read()
    if s.count(certo) != 1:
        raise SystemExit(f"o arnes esta velho: o trecho devia aparecer uma vez em {arquivo}, e aparece {s.count(certo)}:\n  {certo}")
    open(caminho, "w", encoding="utf-8").write(s.replace(certo, errado))
    return s


quais = [int(x) for x in sys.argv[1:]]
print("=" * 70)
print("PASSO 1 - a base passa NA COPIA?  (sem isso toda perturbacao e falso positivo)")
base = copia()
parou, cod, saida = roda(base)
print(f"  saida {cod}" + (" (o gerador parou)" if parou else ""))
assert not parou and cod == 0, "A BASE FALHA NA COPIA. O arnes inteiro seria falso positivo.\n" + saida[-1500:]

print("\nPASSO 2 - cada defeito plantado acende a checagem dele")
ruins = 0
for i, (desc, arq, certo, errado, checagem) in enumerate(PERTURBACOES, 1):
    if quais and i not in quais:
        continue
    original = aplica(base, arq, certo, errado)
    parou, cod, saida = roda(base)
    open(os.path.join(base, arq), "w", encoding="utf-8").write(original)
    falhas = [l.strip() for l in saida.split("\n") if "[FALHA]" in l]
    if checagem is None:
        acendeu = parou
        det = "o gerador parou" if parou else f"o gerador NAO parou (saida {cod})"
    else:
        acendeu = not parou and cod != 0 and any(checagem in l for l in falhas)
        det = "o gerador parou: " + saida[-200:].replace("\n", " ") if parou else f"{len(falhas)} checagem(ns)" + ("" if acendeu else " · " + "; ".join(l[:90] for l in falhas[:3]))
    ruins += not acendeu
    print(f"  [{'ACENDEU' if acendeu else 'PASSOU CALADA'}] {i:2d}. {desc:<62} -> {det}", flush=True)

print("\nPASSO 3 - o contra-teste: mudanca que nao muda a regra fica verde")
if not quais:
    desc, arq, certo, errado = CONTRA
    original = aplica(base, arq, certo, errado)
    parou, cod, saida = roda(base)
    open(os.path.join(base, arq), "w", encoding="utf-8").write(original)
    verde = not parou and cod == 0
    ruins += not verde
    print(f"  [{'FICOU VERDE' if verde else 'ACENDEU SEM MOTIVO'}] {desc} -> saida {cod}")
shutil.rmtree(base, ignore_errors=True)

print("\n" + "=" * 70)
if ruins:
    print(f">>> {ruins} PERTURBACAO(OES) NAO SE COMPORTARAM COMO DEVIAM.")
    sys.exit(1)
print(f">>> TUDO OK — {len(quais) or len(PERTURBACOES)} perturbacoes acendem a checagem certa" + ("" if quais else ", e o contra-teste fica verde") + ".")
