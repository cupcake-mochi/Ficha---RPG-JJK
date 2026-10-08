# -*- coding: utf-8 -*-
"""O arnes da aba INVOCAÇÕES: planta um defeito de cada vez numa COPIA do repositorio, gera a ficha de novo e roda
o regressao-invocacoes.py. Cada defeito tem de acender a checagem dele. Um teste que passa de primeira so vale se
tambem reprova o que esta errado.

Cada rodada gera a ficha e recalcula dezenove planilhas no LibreOffice, e leva uns dois a tres minutos: por isso ele e
rodado a mao, e nao mora no rodar-tudo.sh. Nao rode junto com outro programa que use o LibreOffice.

    python3 arnes-invocacoes.py            # todas as perturbacoes
    python3 arnes-invocacoes.py 3 7        # so a terceira e a setima
"""
import os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FORA = {".git", "mockup", "__pycache__", "repos", "repo-conserto", ".claude"}
GER, AMA = "ficha-v01/ficha_invocacoes.py", "ficha-v01/ficha_amaldicoada.py"

# (o que e o defeito, arquivo, o trecho certo, o trecho errado, um pedaco do nome da checagem que tem de acender)
PERTURBACOES = [
    # --- os números da ficha
    ("o ataque da entidade esquece a maestria do invocador", GER,
     '''o["atq"] = f'=IF({P("va")}="","",{P("va")}+{MAE}+{P("us0")})\'''', '''o["atq"] = f'=IF({P("va")}="","",{P("va")}+{P("us0")})\'''',
     "ataque +4 e CD 12"),
    ("a CD da entidade parte de 10, e não de 8", GER,
     '''o["cd"] = f'=IF({P("va")}="","",8+{P("va")}+{MAE}+{P("us1")})\'''', '''o["cd"] = f'=IF({P("va")}="","",10+{P("va")}+{MAE}+{P("us1")})\'''',
     "ataque +4 e CD 12"),
    ("a Defesa esquece a parcela do atributo do invocador", GER,
     '''o["def"] = f'=10+{P("t1")}+{H["parcela da defesa"]}+{P("us2")}\'''', '''o["def"] = f'=10+{P("t1")}+{P("us2")}\'''', "ataque +4 e CD 12"),
    ("a vida por nível esquece a Constituição", GER,
     '''o["vida"] = f'=5+{P("t2")}+(3+{P("cri")}+{P("t2")})*({nn}-1)+{P("us3")}\'''',
     '''o["vida"] = f'=5+{P("t2")}+(3+{P("cri")})*({nn}-1)+{P("us3")}\'''', "ataque +4 e CD 12"),
    ("o corpo de criação deixa de ganhar 4 por nível", GER,
     '''o["cri"] = f'=IF({P("tipo")}="{CORPO_CRIACAO}",1,0)\'''', '''o["cri"] = f'=IF({P("tipo")}="{CORPO_CRIACAO}",0,0)\'''', "o corpo de criação de nível 5"),
    ("as perícias não crescem com a Inteligência", GER,
     '''o["nper"] = f'=4+INT({P("p3")}/2)\'''', '''o["nper"] = f'=4\'''', "cinco perícias"),
    ("o espaço de especial abre um nível antes", GER,
     '''o["esp"] = f"=INT((2+{nn}/2)/2)"''', '''o["esp"] = f"=INT((3+{nn}/2)/2)"''', "um espaço de especial, um talento"),
    ("o talento do marco não entra", GER, '''o["ntal"] = f'=1+{P("marc")}\'''', '''o["ntal"] = f'=1\'''', "e o segundo talento"),
    ("a domada de nível fixo passa a acompanhar o invocador", GER,
     '''MAX(1,MIN({NIV},IF({P("nfixo")}=0,{NIV},{P("nfixo")}))))\'''', '''{NIV})\'''', "a domada de nível 5 de um invocador de nível 10"),
    ("a reserva da domada esquece a Essência", GER,
     '''o["resmax"] = f'={nn}*(1+INT({P("p4")}/3))\'''', '''o["resmax"] = f'={nn}\'''', "20 PE de reserva"),
    # --- a entrada, o retorno e o talismã
    ("o talismã carregado não barateia a entrada", GER,
     '''MAX(1,CEILING({cl}/2,1)),{cl})\'''', '''{cl},{cl})\'''', "com o talismã carregado entra por 2 PE"),
    ("o retorno cobra os 2 × Classe cheios mesmo com o talismã carregado", GER,
     '''o["ret"] = f'={cl}+{P("ent")}\'''', '''o["ret"] = f'=2*{cl}\'''', "volta por mais 6 PE"),
    # --- o conjunto
    ("Múltiplas Invocações não dobra o limite de ativas", GER,
     '''"teto de ativas": f'=IF({H["trilha"]}="{MULTIPLAS}",4,2)\',''', '''"teto de ativas": f'=IF({H["trilha"]}="{MULTIPLAS}",2,2)\',''',
     "o limite de ativas vai a quatro"),
    ("a lista do conjunto esquece a vida da ficha", GER,
     '''{P("nome")}&" · nv "&{nn}&" · "&{P("atual")}&"/"&{P("vida")})\')''', '''{P("nome")}&" · nv "&{nn})\')''', "a lista traz a ficha no lugar dela"),
    # --- a mesa
    ("a vida atual volta a nascer em branco", GER,
     '''o["vida0"] = f'=IF({P("tem")}=0,"",{P("vida")})\'''', '''o["vida0"] = \'=""\'''', "a VIDA ATUAL nasce cheia"),
    ("a ficha vazia nasce com a vida máxima escrita", GER,
     '''o["vida0"] = f'=IF({P("tem")}=0,"",{P("vida")})\'''', '''o["vida0"] = f'={P("vida")}\'''', "a VIDA ATUAL nasce cheia"),
    ("o Volume guardado não entra na soma do equipamento", GER,
     '''"evol": f"=SUM({_A(g['eq_vol'][0], IV)}:{_A(g['eq_vol'][-1], IV)},{_A(g['guarda_vol'][0], IV)}:{_A(g['guarda_vol'][-1], IV)})",''',
     '''"evol": f"=SUM({_A(g['eq_vol'][0], IV)}:{_A(g['eq_vol'][-1], IV)})",''', "o equipamento soma o Volume"),
    ("o limite de Volume da entidade esquece a Força", GER,
     '''o["carga"] = f'=5+{P("t0")}\'''', '''o["carga"] = f'=5\'''', "o equipamento soma o Volume"),
    ("o equipamento acima do limite não acende", GER,
     '''o["d_equip"] = (f'=IF({P("evol")}>{P("carga")},"{T_ERRO} ","")''', '''o["d_equip"] = (f'=IF({P("evol")}>99,"{T_ERRO} ","")''', "o equipamento soma o Volume"),
    # --- as cartas
    ("a especial cobra 2 PE por Classe", GER,
     '''IF({Cc}=0,"Sem PE",3*{Cc}&" PE"))\'''', '''IF({Cc}=0,"Sem PE",2*{Cc}&" PE"))\'''', "Mordida precisa"),
    ("a Precisão deixa de somar 2 no ataque", GER,
     '''atq_total = f'({P("atk")}+2*IF({tem_m("Precisão")}>0,1,0))\'''', '''atq_total = f'({P("atk")}+0*IF({tem_m("Precisão")}>0,1,0))\'''', "Mordida precisa"),
    ("a devolução da Restrição deixa de parar em 2 × Classe", GER,
     '''o["dv"] = f"=MIN(2*{Cc},{P('dv0')})"''', '''o["dv"] = f"={P('dv0')}"''', "a devolução para em 2 × Classe"),
    ("a Restrição vira dado: o que ela devolve além do gasto não some", GER,
     '''o["usa"] = f"=MIN({P('dv')},{P('g')})"''', '''o["usa"] = f"={P('dv')}"''', "fichas sorteadas"),
    ("a básica com Melhoria não perde o dado", GER,
     '''MAX(0,{P('db')}-IF({P('nm')}>0,1,0))''', '''MAX(0,{P('db')})''', "fichas sorteadas"),
    ("o ataque com Condição ou Prende deixa de mostrar o TR (a D43 do livro)", GER,
     '''&IF({P("ptr")}>0," · TR"&IF({P("cdf")}="",""," CD "&{P("cdf")}),""),\'''', ''',\'''', "mostra também o TR e a CD"),
    # --- 08/10/2026 (B41): a Integridade da entidade com alma
    ("a Integridade da entidade usa a vida inteira, e não a metade", GER,
     '''o["imax"] = f'=IF({com},MAX(1,INT({P("vida")}/2)),"")\'''', '''o["imax"] = f'=IF({com},MAX(1,INT({P("vida")})),"")\'''',
     "a Integridade da entidade é metade da vida máxima"),
    ("a entidade sem alma ganha Integridade", GER,
     '''com = f'AND({P("tem")}=1,{P("alma")}<>"{SEM_ALMA}")\'''', '''com = f'AND({P("tem")}=1,{P("alma")}<>"outra coisa")\'''',
     "a entidade sem alma não tem Integridade"),
    ("o estágio 1 da entidade só começa na metade da Integridade", GER,
     '''IF({ia}<={im}*3/4,"{ESTAGIOS[1]}","{ESTAGIOS[0]}")''', '''IF({ia}<={im}*2/4,"{ESTAGIOS[1]}","{ESTAGIOS[0]}")''',
     "os estágios da entidade seguem o que falta"),
    ("a Integridade atual da entidade nasce em branco", GER,
     '''o["integ0"] = f'={P("imax")}\'''', '''o["integ0"] = \'=""\'''', "a Integridade da entidade é metade da vida máxima"),
    ("Prende deixa de ser peça que pede TR", AMA, 'PEDEM_TR = ("Prende", "Cerca")', 'PEDEM_TR = ("Cerca",)', "mostra também o TR e a CD"),
]

# o contra-teste: mudança que não muda regra nenhuma tem de ficar verde
CONTRA = ("um comentário a mais no gerador", GER, "N_COLUNAS, N_FILEIRAS = 2, 6", "N_COLUNAS, N_FILEIRAS = 2, 6  # contra-teste do arnes")


def copia():
    d = tempfile.mkdtemp(prefix="arnes-invocacoes-")
    for nome in os.listdir(AQUI):
        if nome in FORA:
            continue
        de = os.path.join(AQUI, nome)
        if os.path.isdir(de):
            shutil.copytree(de, os.path.join(d, nome), ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy(de, os.path.join(d, nome))
    return d


def roda(pasta):
    """gera a ficha na copia e roda a regressao; devolve (parou o gerador?, codigo, saida)"""
    g = subprocess.run([sys.executable, "ficha-v01/monta.py"], cwd=pasta, capture_output=True, text=True)
    if g.returncode:
        return True, g.returncode, (g.stdout + g.stderr)[-400:]
    r = subprocess.run([sys.executable, "regressao-invocacoes.py"], cwd=pasta, capture_output=True, text=True)
    return False, r.returncode, r.stdout + r.stderr


def aplica(pasta, arquivo, certo, errado):
    caminho = os.path.join(pasta, arquivo)
    s = open(caminho, encoding="utf-8").read()
    if s.count(certo) != 1:
        raise SystemExit(f"o arnes esta velho: o trecho devia aparecer uma vez em {arquivo}, e aparece {s.count(certo)}:\n  {certo}")
    open(caminho, "w", encoding="utf-8").write(s.replace(certo, errado))
    return s


if __name__ == "__main__":
    quais = [int(x) for x in sys.argv[1:]]
    # antes de gastar LibreOffice: todo trecho tem de existir uma vez só no arquivo de hoje
    for desc, arq, certo, _, _ in PERTURBACOES + [CONTRA + (None,)]:
        n = open(os.path.join(AQUI, arq), encoding="utf-8").read().count(certo)
        if n != 1:
            raise SystemExit(f"o arnes esta velho ({desc}): o trecho devia aparecer uma vez em {arq}, e aparece {n}:\n  {certo}")
    print("=" * 70)
    print("PASSO 1 - a base passa NA COPIA?  (sem isso toda perturbacao e falso positivo)")
    base = copia()
    parou, cod, saida = roda(base)
    print(f"  saida {cod}" + (" (o gerador parou)" if parou else ""), flush=True)
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
        acendeu = not parou and cod != 0 and any(checagem in l for l in falhas)
        det = ("o gerador parou: " + saida[-200:].replace("\n", " ") if parou else
               f"{len(falhas)} checagem(ns)" + ("" if acendeu else " · " + "; ".join(l[:90] for l in falhas[:3])))
        ruins += not acendeu
        print(f"  [{'ACENDEU' if acendeu else 'PASSOU CALADA'}] {i:2d}. {desc:<70} -> {det}", flush=True)

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
