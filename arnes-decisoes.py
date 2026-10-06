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
           "DECISOES-bloco-A.md", "PENDENCIAS.md", "manual.txt", "manual-temporario.md",
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
    # desde a v0.246 do sistema o manual escreve os tres vetos das Restricoes; o
    # `Rápido` + `Parado` continua legal, entao declarar ele como do manual e mentira
    d["A3_incompatibilidades"]["pares"].append(
        {"a": "Rápido", "b": "Parado", "fonte": "manual", "texto": "", "onde": ""})
perturba("par da ficha declarado como do manual", fonte_mentirosa, "o manual escreve mesmo esse par")

def peca_fantasma(d):
    d["A3_incompatibilidades"]["pares"].append(
        {"a": "Rápido", "b": "Canalizado", "fonte": "ficha", "texto": "", "onde": ""})
perturba("par que nomeia peca inexistente", peca_fantasma, "nomeia pecas que existem")

def fonte_inventada(d):
    d["A2_temporario"]["vida"]["fontes_no_manual"]["Casco de Ferro"] = "sei la"
perturba("fonte de vida temporaria inventada", fonte_inventada, "fontes de vida temporaria existem")

def energia_acumula(d):
    d["A2_temporario"]["energia"]["empilha"] = True
perturba("a A2 volta a deixar a energia acumular", energia_acumula, "nenhuma temporaria acumula")

def vida_sem_teto(d):
    d["A2_temporario"]["vida"]["teto"] = "sem teto"
perturba("a A2 tira o teto da vida temporaria", vida_sem_teto, "o teto e metade do maximo")

def fonte_de_energia_inventada(d):
    d["A2_temporario"]["energia"]["fontes_no_manual"]["Chama Eterna"] = "sei la"
perturba("fonte de energia temporaria inventada", fonte_de_energia_inventada, "fontes de energia temporaria existem")

# --- C1: o guarda que a v0.104 deixou morto -----------------------------
def c1_sem_declaracao(d):
    del d["C1_evocador"]["motivo_hoje"]
perturba("C1 sem declarar o estado dos motivos", c1_sem_declaracao,
         "declara o estado de hoje dos tres motivos")

# 04/10/2026: o Parrudo saiu do livro reconstruido, e o C1 passou a ler as Trilhas do Evocador e o Incursor no menu
def c1_sem_incursor(d):
    d["C1_evocador"]["caminhos_no_menu"].remove("Incursor")
perturba("C1 tirando o Incursor do menu", c1_sem_incursor, "o catalogo inteiro")

def c1_sem_dono_da_decisao(d):
    d["C1_evocador"]["motivo_hoje"]["estado"] = "fica fora e pronto"
perturba("C1 sem registrar de quem e a decisao", c1_sem_dono_da_decisao,
         "a decisao de voltar ao menu e do Mizuki")

def c1_sem_a_ficha(d):
    d["C1_evocador"]["motivo_hoje"]["ficha_da_invocacao"] = "nao existe ainda"
perturba("C1 dizendo que a ficha da invocacao nao existe", c1_sem_a_ficha,
         "aponta a ficha da invocacao como fechada")

# 14/09/2026: o Evocador voltou ao menu, e esconder ele de novo sem tirar do menu acende
def c1_oculto_e_no_menu(d):
    d["C1_evocador"]["caminho_oculto"] = "Evocador"
perturba("C1 escondendo um Caminho que esta no menu", c1_oculto_e_no_menu,
         "menu + oculto = o catalogo inteiro")

print()
print("=" * 70)
print("PASSO 2b - o OUTRO LADO: o livro muda, e a decisao tem de acender")

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

perturba_arquivo("o livro deixa o Evocador sem Trilhas",
                 "manual.txt",
                 "Escolha uma Trilha no nível 2: Invocação Principal, Parceria ou Múltiplas Invocações.",
                 "As Trilhas do Evocador estão em escrita.",
                 "as tres Trilhas do Evocador")
perturba_arquivo("o manual.txt perde a regra da energia temporaria",
                 "manual.txt",
                 "Energia temporária | Até metade dos PE máximos. É gasta antes dos PE comuns.",
                 "Energia temporária | Acumula sem teto.",
                 "regra da energia temporaria")
perturba_arquivo("o Rasga Escudo deixa de ignorar a vida temporaria",
                 "manual.txt",
                 "O dano ignora a vida temporária e uma barreira",
                 "O dano respeita a vida temporária e uma barreira",
                 "Rasga Escudo diz que o dano ignora")
perturba_arquivo("o livro volta a ter cinco Caminhos",
                 "manual.txt",
                 "Escolha um dos seis Caminhos",
                 "Escolha um dos cinco Caminhos",
                 "os Caminhos que o livro diz")
perturba_arquivo("o manual-temporario.md esquece que foi superado",
                 "manual-temporario.md",
                 "SUPERADO",
                 "PROPOSTO",
                 "se declara superado")

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
