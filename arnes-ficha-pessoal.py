# -*- coding: utf-8 -*-
"""O arnes das contas da FICHA PESSOAL: planta um defeito de cada vez numa COPIA do repositorio, gera a ficha de novo
e roda o regressao-ficha-pessoal.py. Cada defeito tem de acender a checagem dele.

Nasceu em 01/10/2026 com o B30 (o aviso embaixo da mao e a nota das propriedades da arma), e so cobre essas contas: o
que o Codigo.gs faz pela aba e do arnes-pessoal.py. Cada rodada gera a ficha e recalcula 22 planilhas no LibreOffice,
e leva uns quatro minutos (55 minutos ao todo em 01/10/2026, com a maquina ocupada): por isso ele e rodado a mao, e nao
mora no rodar-tudo.sh.

    python3 arnes-ficha-pessoal.py            # todas as perturbacoes
    python3 arnes-ficha-pessoal.py 3 7        # so a terceira e a setima
"""
import os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FORA = {".git", "mockup", "__pycache__", "repos", "repo-conserto", ".claude"}
GER = "ficha-v01/ficha_pessoal.py"

# (o que e o defeito, arquivo, o trecho certo, o trecho errado, um pedaco do nome da checagem que tem de acender)
PERTURBACOES = [
    ("a mão principal não avisa quando não há arma guardada", GER,
     '''{H["guardados para a principal"]}=0," · {T_GUARDE_P}"''', '''{H["guardados para a principal"]}<0," · {T_GUARDE_P}"''', "de fábrica: as"),
    ("o escudo guardado conta como arma para a mão principal", GER,
     '''--({eq_cat}<>"Escudo"))')''', '''--({eq_cat}<>"Nada"))')''', "só o escudo guardado: as"),
    ("a arma de duas mãos guardada conta para a mão secundária", GER,
     '''+({eq_mao}=1))>0))')''', '''+({eq_mao}>=1))>0))')''', "só arma de duas mãos guardada: as"),
    ("a mão secundária não avisa quando não há nada guardado para ela", GER,
     '''IF({H["guardados para a secundária"]}=0,"{T_GUARDE_S}","Mão livre")''', '''IF({H["guardados para a secundária"]}<0,"{T_GUARDE_S}","Mão livre")''',
     "de fábrica: as"),
    ("o Alcance casa com o Longo Alcance na nota da arma", GER,
     '''tem = f'ISNUMBER(SEARCH(" · "&{n_}&" · "," · "&{props}&" · "))\'''', '''tem = f'ISNUMBER(SEARCH({n_},{props}))\'''', "nota · Metralhadora Pesada: as"),
    ("a Munição perde o número da arma", GER, '''if nome == MUNICAO else''', '''if nome == "nada" else''', "nota · Metralhadora Pesada: as"),
    ("o Longo Alcance perde as faixas da arma", GER, '''if nome == LONGO_ALCANCE else''', '''if nome == "nada" else''', "nota · Metralhadora Pesada: as"),
    ("a arma de duas mãos não ganha a linha das Duas mãos", GER,
     '''f'{H["mão da principal"]}=2') + "))"),''', '''"FALSE") + "))"),''', "nota · Metralhadora Pesada: as"),
    ("o escudo na mão secundária fica sem a nota do livro", GER,
     '''IF({esc}=1,{S}&CHAR(10)&"{R["texto_do_escudo"]}",''', '''IF({esc}=2,{S}&CHAR(10)&"{R["texto_do_escudo"]}",''', "Kaori: as"),
    ("o Soco fica sem a nota do livro", GER,
     '''"{SOCO}"&CHAR(10)&"{R["texto_do_soco"]}"''', '''"{SOCO}"''', "de fábrica: as"),
    ("a nota da arma vai para a caixa de escolha, e não para a linha de baixo", GER,
     '''"arma da principal": G["det_principal"],''', '''"arma da principal": G["principal"],''', "a nota da arma mora na linha embaixo"),
    ("a arma com Alcance fica sem os 3 m", GER, '''if nome == ALCANCE else "")''', '''if nome == "nada" else "")''', "nota · Chicote: as"),
    ("a frase do catálogo fica na nota das Duas mãos", GER,
     '''            faz = faz[:-len(corte)]''', '''            faz = faz[:]''', "nota · Metralhadora Pesada: as"),
    # 08/10/2026 (B42): o Buff/Debuff do limite de carga
    ("o limite de carga esquece o Buff/Debuff", GER,
     '''+{f_}+N({_A(G["carga_buff"], FP)})')''', '''+{f_}')''', "carga com buff: as"),
    ("o Buff/Debuff negativo não tira do limite de carga", GER,
     '''+{f_}+N({_A(G["carga_buff"], FP)})')''', '''+{f_}+MAX(0,N({_A(G["carga_buff"], FP)}))')''', "carga com debuff: as"),
]
CONTRA = ("um comentário a mais no gerador", GER, "def geometria(R):", "# comentario que nao muda nada\ndef geometria(R):")


def copia():
    d = tempfile.mkdtemp(prefix="arnes-ficha-pessoal-")
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
    r = subprocess.run([sys.executable, "regressao-ficha-pessoal.py"], cwd=pasta, capture_output=True, text=True)
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
    acendeu = not parou and cod != 0 and any(checagem in l for l in falhas)
    det = "o gerador parou: " + saida[-200:].replace("\n", " ") if parou else f"{len(falhas)} checagem(ns)" + ("" if acendeu else " · " + "; ".join(l[:90] for l in falhas[:3]))
    ruins += not acendeu
    print(f"  [{'ACENDEU' if acendeu else 'PASSOU CALADA'}] {i:2d}. {desc:<66} -> {det}", flush=True)

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

print()
print("=" * 70)
if ruins:
    print(f">>> {ruins} PERTURBACAO(OES) NAO SE COMPORTARAM COMO DEVIAM.")
    sys.exit(1)
print(f">>> TUDO OK — {len(quais) or len(PERTURBACOES)} perturbacoes acendem a checagem certa.")
