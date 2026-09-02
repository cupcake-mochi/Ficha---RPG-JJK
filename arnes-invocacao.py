# -*- coding: utf-8 -*-
"""Arnes de perturbacao do conferir-invocacao.py.

As tres regras do projeto, todas pagas com uma versao perdida:
  1. numa copia isolada, nunca nos arquivos reais
  2. a base tem de passar NA COPIA antes de perturbar -- copia mal montada faz
     toda perturbacao acender, e ai os vermelhos nao provam nada
  3. conferir que a perturbacao MUDOU o arquivo antes de ler o resultado --
     um sed que nao bate produz um "nao acendeu" falso
"""
import json, os, shutil, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
ARQS = ["invocacao.json", "capitulo-16-invocacoes.md",
        "capitulo-35-caminhos-e-trilhas.md", "conferir-invocacao.py",
        "manual.txt"]
falhas = []

def monta_copia():
    tmp = tempfile.mkdtemp(prefix="arnes-inv-")
    for a in ARQS:
        o = os.path.join(RAIZ, a)
        if os.path.exists(o):
            shutil.copy(o, os.path.join(tmp, a))
    os.makedirs(os.path.join(tmp, "ficha-invocacao"), exist_ok=True)
    for a in ("monta.py", "ficha-invocacao.xlsx"):
        o = os.path.join(RAIZ, "ficha-invocacao", a)
        if os.path.exists(o):
            shutil.copy(o, os.path.join(tmp, "ficha-invocacao", a))
    return tmp

def roda(tmp):
    r = subprocess.run([sys.executable, "conferir-invocacao.py"], cwd=tmp,
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

def edita(tmp, arquivo, de, para):
    """troca em TEXTO, e devolve se MUDOU alguma coisa. Sem isso a perturbacao
    pode nao ter acontecido e o verde parecer prova."""
    p = os.path.join(tmp, arquivo)
    antes = open(p, encoding="utf-8", errors="replace").read()
    depois = antes.replace(de, para, 1)
    if antes == depois:
        return False
    open(p, "w", encoding="utf-8", errors="replace").write(depois)
    return True

def edita_json(tmp, caminho, novo):
    """troca um valor no JSON PARSEADO, e devolve se mudou.

    E em cima do parse, e nao do texto, porque uma perturbacao escrita como
    string casa com a formatacao do arquivo -- e o dia em que alguem rodar um
    json.dump por cima, TODAS as trocas param de bater em silencio. Foi o que
    aconteceu aqui: sete perturbacoes viraram 'troca nao bateu' de uma vez.
    """
    p = os.path.join(tmp, "invocacao.json")
    d = json.load(open(p, encoding="utf-8"))
    no = d
    for k in caminho[:-1]:
        if k not in no:
            return False
        no = no[k]
    ultimo = caminho[-1]
    if novo is not REMOVE and ultimo not in no:
        no[ultimo] = novo          # ACRESCENTAR tambem e perturbacao valida
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        return True
    if ultimo not in no:
        return False
    if novo is REMOVE:
        del no[ultimo]
    else:
        if no[ultimo] == novo:
            return False
        no[ultimo] = novo
    json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return True

class REMOVE:
    """marcador: apaga a chave em vez de trocar o valor."""

# =====================================================================
print("=" * 74)
print("PASSO 1 — a base passa NA COPIA?")
print("=" * 74)
tmp0 = monta_copia()
cod, saida = roda(tmp0)
if cod != 0:
    print("  [ABORTA] a copia limpa ja reprova. Sem isso nenhuma perturbacao prova nada.")
    print(saida[-2000:])
    sys.exit(1)
n = saida.count("[OK]")
print(f"  [OK] a copia limpa passa, com {n} checagens verdes")
shutil.rmtree(tmp0, ignore_errors=True)

# =====================================================================
print()
print("=" * 74)
print("PASSO 2 — cada perturbacao acende a checagem certa?")
print("=" * 74)

PERTURBACOES = [
    # (nome, caminho no json OU ("texto", arquivo, de, para), valor novo, checagem esperada)
    ("preço de um Traço no json", ["traco", "Voo"], 9, "traco · Voo"),
    ("preço de um Comando no json", ["comando", "Interpor"], 6, "comando · Interpor"),
    ("preço no CAPÍTULO, o outro lado da comparação",
     ("texto", "capitulo-16-invocacoes.md", "| **8** | `Voo` |", "| **6** | `Voo` |"),
     None, "traco · Voo"),
    ("base da vida de um tipo", ["tipos", "técnica"], 4, "base do tipo"),
    ("multiplicador do corpo forte", ["vida", "multiplicador_corpo_forte"], 3.0,
     "corpo forte"),
    ("base do orçamento", ["orcamento", "base"], 10, "orcamento do nv"),
    ("passo do orçamento por marco", ["orcamento", "por_marco"], 3, "orcamento do nv"),
    ("um marco a menos na escada", ["progressao", "marcos"],
     [6, 10, 14, 18, 26, 30], "marcos do json"),
    ("multiplicador do Servo", ["trilhas", "Servo", "orcamento_multiplicador"], 2.0,
     "Servo no nv"),
    ("uma faixa do Investir", ["investir", "faixas"],
     [{"de": 2, "ate": 4, "uma": "1d6", "matilha": "2"},
      {"de": 5, "ate": 8, "uma": "4d6", "matilha": "1d6"},
      {"de": 9, "ate": 12, "uma": "7d6", "matilha": "2d6"},
      {"de": 13, "ate": 16, "uma": "8d6", "matilha": "3d6"},
      {"de": 17, "ate": 20, "uma": "10d6", "matilha": "4d6"},
      {"de": 21, "ate": 25, "uma": "13d6", "matilha": "5d6"},
      {"de": 26, "ate": 30, "uma": "15d6", "matilha": "6d6"}],
     "faixa 9-12"),
    ("a amarra", ["ficha_dela", "amarra"], 21, "amarra ="),
    ("o deslocamento", ["ficha_dela", "deslocamento"], 12, "deslocamento ="),
    ("o multiplicador da régua da morte", ["morte", "multiplicador_regua"], 4,
     "regua da morte"),
    ("quantos corpos a Matilha põe", ["trilhas", "Matilha", "corpos"], 4,
     "Matilha: 5 corpo"),
    ("qual corpo o Coro leva", ["trilhas", "Coro", "corpo"], "forte",
     "Coro: corpo cru"),
    ("uma entrada some do catálogo", ["traco", "Nado"], REMOVE,
     "o capitulo publica 13 entradas e o json tem as mesmas"),
    ("os pontos de uma montagem por Trilha",
     ["montagens_por_trilha", "Servo", "pontos"], 16, "Servo: 12 pontos"),
    ("o arranjo de uma montagem estoura os 9 pontos",
     ["montagens_por_trilha", "Servo", "arranjo"], [3, 3, 3, 1, 1],
     "o arranjo soma 9"),
    ("o multiplicador do Parrudo",
     ["sintonia", "rotas", "Parrudo", "multiplicador_maestria"], 3,
     "Parrudo: o numero do json"),
    ("o crítico da Presa",
     ["sintonia", "rotas", "Presa", "critico_a_partir_de"], 18,
     "Presa: o numero do json"),
    ("o bônus da Voz", ["sintonia", "rotas", "Voz", "bonus"], 2,
     "Voz: o numero do json"),
    ("o nível em que a Voz vira metade da maestria",
     ["sintonia", "rotas", "Voz", "vira_metade_da_maestria_no_nivel"], 9,
     "vira metade da maestria"),
    ("o Parrudo no CAPÍTULO 35, o outro lado",
     ("texto", "capitulo-35-caminhos-e-trilhas.md",
      "equivalente a **`5 ×` a sua maestria**",
      "equivalente a **`4 ×` a sua maestria**"),
     None, "Parrudo: o numero do json"),
    ("uma rota da Sintonia some", ["sintonia", "rotas", "Presa"], REMOVE,
     "o json tem as mesmas 3 rotas"),
    ("o Parrudo volta a ter dois donos",
     ["parrudo", "multiplicador_maestria"], 5, "virou ponteiro"),
    ("a pendência da Voz é apagada",
     ["sintonia", "rotas", "Voz", "PENDENTE"], REMOVE,
     "o json registra a pendencia da Voz"),
]

for nome, alvo, novo, esperado in PERTURBACOES:
    tmp = monta_copia()
    if isinstance(alvo, tuple):
        mudou = edita(tmp, alvo[1], alvo[2], alvo[3])
    elif novo is REMOVE or True:
        mudou = edita_json(tmp, alvo, novo)
    if not mudou:
        print(f"  [INVÁLIDA] {nome}  <- a troca nao bateu no arquivo; "
              f"o teste nao rodou")
        falhas.append(nome + " (troca nao bateu)")
        shutil.rmtree(tmp, ignore_errors=True)
        continue
    cod, saida = roda(tmp)
    acendeu = cod != 0
    a_certa = any(esperado in lin for lin in saida.split("\n")
                  if lin.strip().startswith("[FALHA]"))
    if acendeu and a_certa:
        print(f"  [ACENDE] {nome}")
    elif acendeu:
        print(f"  [ACENDE, MAS ERRADA] {nome}  <- esperava uma falha com "
              f"{esperado!r}, e as que vieram foram outras")
        falhas.append(nome + " (acendeu a checagem errada)")
    else:
        print(f"  [NÃO ACENDE] {nome}  <- perturbei e o validador continuou verde")
        falhas.append(nome)
    shutil.rmtree(tmp, ignore_errors=True)

# =====================================================================
print()
print("=" * 74)
print("PASSO 3 — o gerador com preço escrito na mão tem de acender")
print("=" * 74)
tmp = monta_copia()
p = os.path.join(tmp, "ficha-invocacao", "monta.py")
g = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(g + '\nATALHO = {"Voo": 8}\n')
cod, saida = roda(tmp)
a_certa = any("escrito dentro do gerador" in lin for lin in saida.split("\n")
              if lin.strip().startswith("[FALHA]"))
if cod != 0 and a_certa:
    print("  [ACENDE] um preço do catálogo escrito no código do gerador")
else:
    print("  [NÃO ACENDE] o preço escrito no gerador passou batido")
    falhas.append("preço escrito no gerador")
shutil.rmtree(tmp, ignore_errors=True)

# =====================================================================
print()
print("=" * 74)
print("PASSO 4 — sem cada capítulo, ele FALHA em vez de pular em silêncio")
print("=" * 74)
for arq, marca in [("capitulo-16-invocacoes.md", "nao confere NADA"),
                   ("capitulo-35-caminhos-e-trilhas.md", "Sintonia")]:
    tmp = monta_copia()
    os.remove(os.path.join(tmp, arq))
    cod, saida = roda(tmp)
    if cod != 0 and marca in saida:
        print(f"  [ACENDE] sem o {arq} ele sai vermelho e diz como regerar")
    else:
        print(f"  [NÃO ACENDE] sem o {arq} ele saiu {cod}, e devia falhar alto")
        falhas.append(f"{arq} ausente")
    shutil.rmtree(tmp, ignore_errors=True)

# =====================================================================
print()
print("=" * 74)
print("PASSO 5 — o guarda da divergência: se o manual.txt for re-extraído,")
print("           a checagem tem de mudar de estado em vez de ficar verde")
print("=" * 74)
tmp = monta_copia()
if edita(tmp, "manual.txt", "A ficha dela é derivada da sua",
         "A invocação tem os cinco atributos, e eles são dela"):
    cod, saida = roda(tmp)
    a_certa = any("ficha derivada" in lin for lin in saida.split("\n")
                  if lin.strip().startswith("[FALHA]"))
    if cod != 0 and a_certa:
        print("  [ACENDE] o manual.txt consertado faz o guarda mudar de estado")
    else:
        print("  [NÃO ACENDE] o guarda continuou verde com o manual.txt consertado")
        falhas.append("guarda da divergência")
else:
    print("  [INVÁLIDA] a troca nao bateu no manual.txt")
    falhas.append("guarda da divergência (troca nao bateu)")
shutil.rmtree(tmp, ignore_errors=True)

# =====================================================================
print()
print("=" * 74)
print("PASSO 6 — contra-teste: uma mudança INÓCUA deixa tudo verde?")
print("           (se qualquer edição acendesse, os vermelhos acima não provariam nada)")
print("=" * 74)
tmp = monta_copia()
d = json.load(open(os.path.join(tmp, "invocacao.json"), encoding="utf-8"))
d["_meta"]["comentario_novo"] = "isto nao muda regra nenhuma"
json.dump(d, open(os.path.join(tmp, "invocacao.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
cod, _ = roda(tmp)
if cod == 0:
    print("  [CONTINUA VERDE] comentário novo no _meta -> saída 0")
else:
    print("  [FALHA] uma mudança inócua acendeu o validador")
    falhas.append("contra-teste inócuo")
shutil.rmtree(tmp, ignore_errors=True)

# =====================================================================
print()
print("=" * 74)
if falhas:
    print(f">>> {len(falhas)} PROBLEMA(S) no arnês:")
    for f_ in falhas:
        print(f"    · {f_}")
    sys.exit(1)
print(f">>> TUDO OK — {len(PERTURBACOES)} perturbações acendem a checagem certa,")
print("    o preço escrito no código acende, o capítulo ausente falha alto,")
print("    o guarda da divergência muda de estado, e o inócuo fica verde.")
print("=" * 74)
