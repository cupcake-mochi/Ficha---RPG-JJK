# -*- coding: utf-8 -*-
"""Arnes de perturbacao do regressao-delta.js.

As tres regras do projeto, e nenhuma pode ser pulada:
  1. numa copia isolada, nunca nos arquivos reais
  2. a base tem que passar NA COPIA antes de perturbar
  3. cada perturbacao tem que MUDAR o arquivo de verdade antes de eu ler o resultado
"""
import json, os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
PRECISA = ["regressao-delta.js", "decisoes-ficha.json", "manual-temporario.md"]
NODE = shutil.which("node") or shutil.which("nodejs")


def roda(pasta):
    r = subprocess.run([NODE, "regressao-delta.js"], cwd=pasta,
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def copia():
    d = tempfile.mkdtemp(prefix="arnes-delta-")
    os.mkdir(os.path.join(d, "apps-script"))
    shutil.copy(os.path.join(AQUI, "apps-script", "Codigo.gs"),
                os.path.join(d, "apps-script"))
    for f in PRECISA:
        shutil.copy(os.path.join(AQUI, f), d)
    return d


if NODE is None:
    print("node nao existe nesta maquina: o arnes do delta nao roda aqui.")
    sys.exit(0)

print("=" * 70)
print("PASSO 1 - a base passa NA COPIA?  (sem isso toda perturbacao e falso positivo)")
base = copia()
cod, saida = roda(base)
print(f"  copia em {base}")
print(f"  codigo de saida {cod}  -> {'passa limpa' if cod == 0 else 'JA FALHA'}")
assert cod == 0, "A BASE FALHA NA COPIA. O arnes inteiro seria falso positivo.\n" + saida
shutil.rmtree(base)
print("  base limpa. pode perturbar.\n")

CONTA = {"acendeu": 0, "erros": []}


def julga(nome, cod, saida, agulha, espera_verde=False):
    achou = agulha in saida if agulha else True
    if espera_verde:
        bom = cod == 0
        veredito = "FICOU VERDE" if bom else "ACENDEU A ESMO"
    else:
        bom = cod != 0 and achou
        veredito = ("ACENDEU" if bom else
                    ("acendeu outra" if cod != 0 else "NAO ACENDEU"))
    print(f"  [{veredito:14}] {nome:44} -> saida {cod}")
    if bom:
        CONTA["acendeu"] += 1
    else:
        CONTA["erros"].append(nome)


def edita(nome, arquivo, antes_txt, depois_txt, agulha, espera_verde=False):
    d = copia()
    alvo = os.path.join(d, arquivo)
    antes = open(alvo, encoding="utf-8").read()
    if antes_txt not in antes:
        print(f"  [INUTIL] {nome:44} -> o trecho nao existe no arquivo")
        CONTA["erros"].append(nome); shutil.rmtree(d); return
    open(alvo, "w", encoding="utf-8").write(antes.replace(antes_txt, depois_txt))
    if open(alvo, encoding="utf-8").read() == antes:
        print(f"  [INUTIL] {nome:44} -> a perturbacao NAO mudou o arquivo")
        CONTA["erros"].append(nome); shutil.rmtree(d); return
    cod, saida = roda(d)
    julga(nome, cod, saida, agulha, espera_verde)
    shutil.rmtree(d)


def edita_json(nome, muda, agulha):
    d = copia()
    alvo = os.path.join(d, "decisoes-ficha.json")
    antes = open(alvo, encoding="utf-8").read()
    dados = json.loads(antes)
    muda(dados)
    json.dump(dados, open(alvo, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    if json.loads(open(alvo, encoding="utf-8").read()) == json.loads(antes):
        print(f"  [INUTIL] {nome:44} -> a perturbacao NAO mudou o arquivo")
        CONTA["erros"].append(nome); shutil.rmtree(d); return
    cod, saida = roda(d)
    julga(nome, cod, saida, agulha)
    shutil.rmtree(d)


GS = "apps-script/Codigo.gs"
NEG = """  if (passo < 0) {
    var comido = Math.min(temp, -passo);
    temp = temp - comido;
    novo = atual - (-passo - comido);
  } else {"""

print("=" * 70)
print("PASSO 2 - cada perturbacao acende a checagem certa?")

edita("a temporaria volta a nao ser consumida", GS, NEG,
      """  if (passo < 0) {
    novo = atual + passo;
  } else {""",
      "so 2 descem na vida")

edita("a temporaria absorve mas nao desce", GS,
      "    temp = temp - comido;\n", "",
      "a temporaria vai embora inteira")

edita("o ganho zera a temporaria", GS,
      "  } else {\n    novo = atual + passo;",
      "  } else {\n    temp = 0;\n    novo = atual + passo;",
      "ganho nao mexe na temporaria")

edita("o piso de zero cai", GS,
      "    atual: Math.max(0, max ? Math.min(novo, max) : novo),",
      "    atual: (max ? Math.min(novo, max) : novo),",
      "perda nao passa de zero")

edita("o teto do maximo cai", GS,
      "    atual: Math.max(0, max ? Math.min(novo, max) : novo),",
      "    atual: Math.max(0, novo),",
      "ganho nao passa do maximo")

edita("temporaria negativa deixa de ser presa em zero", GS,
      "  temp = Math.max(0, Number(temp) || 0);",
      "  temp = Number(temp) || 0;",
      "temporaria negativa e lida como zero")

edita("a funcao inteira desaparece do Codigo.gs", GS,
      "function aplicaPasso_(", "function aplicaPassoOutroNome_(",
      "aplicaPasso_ nao existe no Codigo.gs")

edita("o exemplo do manual muda de numero", "manual-temporario.md",
      "Ela fica com 18, não com 27", "Ela fica com 5, não com 27",
      "so 2 descem na vida")

edita("o exemplo do manual muda de forma", "manual-temporario.md",
      "Ela fica com 18, não com 27", "Ela termina com 18, e não com 27",
      "o exemplo do manual-temporario.md mudou de forma")

edita_json("a A2 desiste de gastar a vida temporaria primeiro",
           lambda d: d["A2_temporario"]["vida"].__setitem__(
               "gasta_antes_da_vida_normal", False),
           "A2 diz que a vida temporaria gasta antes da vida")

edita_json("a A2 desiste de gastar a energia temporaria primeiro",
           lambda d: d["A2_temporario"]["energia"].__setitem__(
               "gasta_antes_do_pe_normal", False),
           "A2 diz que a energia temporaria gasta antes do PE")

edita("mexida inocua no comentario", GS,
      "// o mestre precisa poder mexer", "// o mestre tem que poder mexer",
      None, espera_verde=True)

barra = "=" * 70
print("")
print(barra)
if CONTA["erros"]:
    print(f">>> {len(CONTA['erros'])} PERTURBACAO(OES) SEM VEREDITO:")
    for e in CONTA["erros"]:
        print("  · " + e)
    print(barra)
    sys.exit(1)
print(f">>> TUDO OK — {CONTA['acendeu']} perturbacoes acendem a checagem certa,")
print("    a funcao ausente falha alto, o exemplo reescrito acende,")
print("    e o inocuo fica verde.")
print(barra)
