# -*- coding: utf-8 -*-
"""O arnes da moldura da foto da CARTEIRA (03/10/2026): planta um defeito de cada vez numa COPIA do repositorio, gera a
ficha de novo e roda o conferir-ficha-xlsx.py. Cada defeito tem de acender a checagem da moldura.

A moldura saiu de dentro da caixa da foto, pedido do Mizuki, para o jogador inserir a imagem NA celula: a caixa fica
livre, com o convite e a nota, as retas viram borda na regua no anel em volta, e as duas quinas chanfradas sao imagem na
celula do canto, na regua exata. Ver ficha-v01/moldura_foto.py.

Cada rodada gera a ficha e confere, e leva perto de um minuto e meio: por isso ele e rodado a mao, e nao mora no
rodar-tudo.sh. Nao usa o LibreOffice.

    python3 arnes-moldura.py            # todas as perturbacoes
    python3 arnes-moldura.py 2 4        # so a segunda e a quarta
"""
import os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
FORA = {".git", "mockup", "__pycache__", "repos", "repo-conserto", ".claude"}
MF, EMI, MON, COD = "ficha-v01/moldura_foto.py", "ficha/emitir_gs.py", "ficha-v01/monta.py", "apps-script/Codigo.gs"
CHECA = "a foto entra na célula"

# (o que e o defeito, arquivo, o trecho certo, o trecho errado)
PERTURBACOES = [
    ("a moldura continua dentro da caixa da foto", MF,
     'aba["imagens"] = [i for i in aba["imagens"] if i["arquivo"] != ARTE_VELHA] + tr["cantos"]',
     'aba["imagens"] = aba["imagens"] + tr["cantos"]'),
    ("a quina de baixo fica sem o canto", MF, "for r, c in ((a1, b1), (a2, b2))]", "for r, c in ((a1, b1),)]"),
    ("o anel perde a reta da esquerda", MF, 'lados.setdefault((r, b1), {})["left"] = TRACO', "pass"),
    ("a reta de cima entra na quina chanfrada", MF, "for c in range(c1, b2 + 1):                  # em cima",
     "for c in range(b1, b2 + 1):                  # em cima"),
    ("a caixa da foto nasce sem o convite", MF, "celulas[canto] = (TEXTO, ", "celulas[canto] = (None, "),
    ("a caixa da foto nasce sem a nota de como inserir", MF, 'NOTA = "Clique na caixa e use Inserir › Imagem › Inserir imagem na célula."',
     'NOTA = "Clique na caixa."'),
    ("a CARTEIRA deixa de declarar a caixa da foto", MON, '"foto": a.get("foto")}', '"foto": None}'),
    ("o canto nasce na média da arte reduzida, e não na cor desenhada", EMI, "_png_de_uma_cor(img, desenho).save(", "_png_de_uma_cor(img).save("),
    ("o canto passa pelo piso de contraste da arte na troca", COD, "var ARTE_DA_BORDA_ = { 'carteira-canto': true };", "var ARTE_DA_BORDA_ = {};"),
]
CONTRA = ("um comentário a mais na limpeza", MF, "def desenha(tr):", "# comentario que nao muda nada\ndef desenha(tr):")


def copia():
    d = tempfile.mkdtemp(prefix="arnes-moldura-")
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
    """gera a ficha na copia e roda o conferidor; devolve (parou o gerador?, codigo, saida)"""
    g = subprocess.run([sys.executable, "ficha-v01/monta.py"], cwd=pasta, capture_output=True, text=True)
    if g.returncode:
        return True, g.returncode, (g.stdout + g.stderr)[-400:]
    r = subprocess.run([sys.executable, "conferir-ficha-xlsx.py"], cwd=pasta, capture_output=True, text=True)
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
print(f"  saida {cod}" + (" (o gerador parou)" if parou else ""), flush=True)
assert not parou and cod == 0, "A BASE FALHA NA COPIA. O arnes inteiro seria falso positivo.\n" + saida[-1500:]

print("\nPASSO 2 - cada defeito plantado acende a checagem da moldura")
ruins = 0
for i, (desc, arq, certo, errado) in enumerate(PERTURBACOES, 1):
    if quais and i not in quais:
        continue
    original = aplica(base, arq, certo, errado)
    parou, cod, saida = roda(base)
    open(os.path.join(base, arq), "w", encoding="utf-8").write(original)
    falhas = [l.strip() for l in saida.split("\n") if "[FALHA]" in l]
    acendeu = not parou and cod != 0 and any(CHECA in l for l in falhas)
    det = ("o gerador parou: " + saida[-200:].replace("\n", " ") if parou
           else f"{len(falhas)} checagem(ns)" + ("" if acendeu else " · " + "; ".join(l[:90] for l in falhas[:3])))
    ruins += not acendeu
    print(f"  [{'ACENDEU' if acendeu else 'PASSOU CALADA'}] {i:2d}. {desc:<64} -> {det}", flush=True)

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
print(f">>> TUDO OK — {len(PERTURBACOES) if not quais else len(quais)} perturbacoes acendem a checagem da moldura"
      + ("" if quais else ", e o contra-teste fica verde."))
