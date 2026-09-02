# -*- coding: utf-8 -*-
"""Arnes de perturbacao do conferir-decisoes.py.

As tres regras do projeto, e nenhuma pode ser pulada:
  1. numa copia isolada, nunca nos arquivos reais
  2. a base tem que passar NA COPIA antes de perturbar
  3. cada perturbacao tem que MUDAR o arquivo de verdade antes de eu ler o resultado
"""
import json, os, shutil, subprocess, sys, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
PRECISA = ["conferir-decisoes.py", "decisoes-ficha.json", "catalogo-projeto-m.json",
           "DECISOES-bloco-A.md", "PENDENCIAS.md", "manual.txt",
           "capitulo-35-caminhos-e-trilhas.md"]

def roda(pasta):
    r = subprocess.run([sys.executable, "conferir-decisoes.py"], cwd=pasta,
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

def copia():
    d = tempfile.mkdtemp(prefix="arnes-decisoes-")
    for f in PRECISA:
        shutil.copy(os.path.join(AQUI, f), d)
    return d

print("=" * 70)
print("PASSO 1 - a base passa NA COPIA?  (sem isso toda perturbacao e falso positivo)")
base = copia()
cod, saida = roda(base)
print(f"  copia em {base}")
print(f"  codigo de saida {cod}  -> {'passa limpa' if cod == 0 else 'JA FALHA'}")
assert cod == 0, "A BASE FALHA NA COPIA. O arnes inteiro seria falso positivo.\n" + saida
shutil.rmtree(base)
print("  base limpa. pode perturbar.\n")

def perturba(nome, muda, agulha):
    d = copia()
    alvo = os.path.join(d, "decisoes-ficha.json")
    antes = open(alvo, encoding="utf-8").read()
    dados = json.loads(antes)
    muda(dados)
    json.dump(dados, open(alvo, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    depois = open(alvo, encoding="utf-8").read()
    if antes == depois:
        print(f"  [INUTIL] {nome:38} -> a perturbacao NAO mudou o arquivo")
        shutil.rmtree(d); return
    cod, saida = roda(d)
    achou = agulha in saida
    veredito = "ACENDEU" if (cod != 0 and achou) else ("acendeu outra" if cod != 0 else "NAO ACENDEU")
    print(f"  [{veredito:14}] {nome:38} -> saida {cod}")
    shutil.rmtree(d)

print("=" * 70)
print("PASSO 2 - cada perturbacao acende a checagem certa?")

def hex_errado(d):
    d["A5_acento"]["degraus"][1]["hex"] = "FF00FF"        # magenta, nao e o ambar
perturba("hex do ambar trocado", hex_errado, "escrito 6.76")

def contraste_errado(d):
    d["A5_acento"]["medido"]["sobre_o_painel"]["osso"] = 9.99
perturba("contraste do osso reescrito na mao", contraste_errado, "escrito 9.99")

def degrau_escuro(d):
    d["A5_acento"]["degraus"][0]["hex"] = "2A2540"        # quase o painel: some no fundo
perturba("degrau que nao le sobre o painel", degrau_escuro, "passa o minimo de 3.0")

def daltonismo_ruim(d):
    d["A5_acento"]["medido"]["osso_vs_ambar"]["deuteranopia"] = 1.10
perturba("dois degraus que viram a mesma cor", daltonismo_ruim, "pior caso de daltonismo")

def fonte_mentirosa(d):
    for p in d["A3_incompatibilidades"]["pares"]:
        if p["b"] == "Lento":
            p["fonte"] = "manual"                          # o manual NAO escreve esse par
perturba("par da ficha declarado como do manual", fonte_mentirosa, "o manual escreve mesmo esse par")

def peca_fantasma(d):
    d["A3_incompatibilidades"]["pares"].append(
        {"a": "Rápido", "b": "Canalizado", "fonte": "ficha", "texto": "", "onde": ""})
perturba("par que nomeia peca inexistente", peca_fantasma, "nomeia pecas que existem")

def fonte_inventada(d):
    d["A2_temporario"]["vida"]["fontes_no_manual"]["Casco de Ferro"] = "sei la"
perturba("fonte de vida temporaria inventada", fonte_inventada, "fontes de vida temporaria existem")

# --- C1: o guarda que a v0.104 deixou morto -----------------------------
def c1_sem_declaracao(d):
    del d["C1_evocador"]["motivo_hoje"]
perturba("C1 sem declarar o estado dos motivos", c1_sem_declaracao,
         "declara o estado de hoje dos tres motivos")

def c1_numero_errado(d):
    d["C1_evocador"]["motivo_hoje"]["numero_do_casco"] = (
        "FECHADO: o Casco virou Parrudo e vale 9 x a maestria")
perturba("C1 declarando um numero que nao e o do capitulo 35", c1_numero_errado,
         "o numero que o C1 declara e o mesmo")

def c1_sem_dono_da_decisao(d):
    d["C1_evocador"]["motivo_hoje"]["estado"] = "fica fora e pronto"
perturba("C1 sem registrar de quem e a decisao", c1_sem_dono_da_decisao,
         "a decisao de voltar ao menu e do Mizuki")

def c1_sem_a_ficha(d):
    d["C1_evocador"]["motivo_hoje"]["ficha_da_invocacao"] = "nao existe ainda"
perturba("C1 dizendo que a ficha da invocacao nao existe", c1_sem_a_ficha,
         "aponta a ficha da invocacao como fechada")

def c1_sem_o_porque(d):
    d["C1_evocador"]["motivo_hoje"]["por_que_a_checagem_velha_nao_servia"] = "sei la"
perturba("C1 sem explicar por que a checagem velha nao servia", c1_sem_o_porque,
         "por que a checagem velha nao servia")

print()
print("=" * 70)
print("PASSO 2b - e o OUTRO LADO do C1: o capitulo 35, que e o dono vivo")

def perturba_arquivo(nome, arquivo, de, para, agulha):
    d = copia()
    alvo = os.path.join(d, arquivo)
    antes = open(alvo, encoding="utf-8").read()
    depois = antes.replace(de, para, 1)
    if antes == depois:
        print(f"  [INUTIL] {nome:38} -> a troca NAO bateu no arquivo")
        shutil.rmtree(d); return
    open(alvo, "w", encoding="utf-8").write(depois)
    cod, saida = roda(d)
    achou = agulha in saida
    veredito = ("ACENDEU" if (cod != 0 and achou)
                else ("acendeu outra" if cod != 0 else "NAO ACENDEU"))
    print(f"  [{veredito:14}] {nome:38} -> saida {cod}")
    shutil.rmtree(d)

perturba_arquivo("o Parrudo perde o numero no capitulo 35",
                 "capitulo-35-caminhos-e-trilhas.md",
                 "equivalente a **`5 ×` a sua maestria**",
                 "e ninguem escreveu quanto",
                 "da um numero ao Parrudo")
perturba_arquivo("o Parrudo muda de numero no capitulo 35",
                 "capitulo-35-caminhos-e-trilhas.md",
                 "equivalente a **`5 ×` a sua maestria**",
                 "equivalente a **`7 ×` a sua maestria**",
                 "o numero que o C1 declara e o mesmo")
perturba_arquivo("o manual.txt foi re-extraido e perdeu a frase do Casco",
                 "manual.txt",
                 "Casco — as suas invocações têm mais vida.",
                 "Parrudo — as suas invocações têm mais vida, 5 × a sua maestria.",
                 "nunca podia acender")

print()
print("=" * 70)
print("PASSO 3 - contra-teste: uma mudanca INOCUA deixa tudo verde?")
print("  (se qualquer edicao acendesse, os vermelhos acima nao provariam nada)")
d = copia()
alvo = os.path.join(d, "decisoes-ficha.json")
dados = json.load(open(alvo, encoding="utf-8"))
dados["_meta"]["comentario"] = "uma linha que nao muda regra nenhuma"
json.dump(dados, open(alvo, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
cod, _ = roda(d)
print(f"  [{'CONTINUA VERDE' if cod == 0 else 'ACENDEU A TOA'}] comentario novo no _meta -> saida {cod}")
shutil.rmtree(d)
