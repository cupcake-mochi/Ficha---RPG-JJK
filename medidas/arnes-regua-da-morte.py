# -*- coding: utf-8 -*-
"""Arnes de perturbacao para o SS12 do conferir-invocacoes.py do JJK---Project.

⚠ ELE NAO RODA DAQUI: ele perturba arquivos do OUTRO repositorio, e o caminho
esta em ORIG logo abaixo. Ele mora aqui porque o container da sessao que o
escreveu era descartavel, e porque o JJK---Project nao tem convencao de arnes
commitado — as perturbacoes de la sao registradas em prosa na peca. Se for
adotar, a casa dele e `sistema/03-mecanica/` de la.

As dez perturbacoes que ele roda cobrem a regra da morte por corpo: a regua
deixando de ser a vida maxima, a clausula de area sumindo, um golpe comum
passando a destruir, o maximo da expressao de dado mentindo, a linha do
critico sumindo, o corpo do Coro voltando para a formula crua, e quatro que
perturbam SO o livro — que e o buraco que a v0.178 registrou saindo verde.

Tres regras da skill, e cada uma ja custou uma versao ao projeto:
  1. numa COPIA isolada, nunca nos arquivos reais;
  2. a base tem de passar NA COPIA antes de perturbar;
  3. a perturbacao tem de MUDAR o arquivo — senao o "nao acendeu" e falso.
"""
import os, shutil, subprocess, sys, tempfile

ORIG = '/home/user/jjk---project/sistema'
PECA = '03-mecanica/15-invocacoes.md'
VALI = '03-mecanica/conferir-invocacoes.py'
LIVRO = '05-material/livro/manual/60-invocacoes.md'

def monta():
    d = tempfile.mkdtemp(prefix='arnes-')
    shutil.copytree(ORIG, os.path.join(d, 'sistema'), symlinks=True,
                    ignore=shutil.ignore_patterns('*.pdf', '*.png', '*.jpg',
                                                  'node_modules'))
    return os.path.join(d, 'sistema')

def roda(base):
    r = subprocess.run([sys.executable, os.path.basename(VALI)],
                       cwd=os.path.join(base, '03-mecanica'),
                       capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr

PERTURBACOES = [
    ('a regua deixa de ser a vida maxima', PECA,
     'A régua da morte é a vida máxima daquele corpo',
     'A régua da morte é `5 ×` a vida que a fórmula do tipo dá'),
    ('some a clausula de area', PECA,
     '> **Área não é golpe único: ela derruba, e nunca destrói.**\n', ''),
    ('um golpe COMUM passa a destruir', PECA,
     '| `Ronda` | `6d8 + 28` | `76` | cai | cai |',
     '| `Ronda` | `6d8 + 28` | `76` | destrói | cai |'),
    ('o maximo da expressao mente', PECA,
     '| `Dupla`, o maior golpe da tabela | `8d12 + 57` | `153` |',
     '| `Dupla`, o maior golpe da tabela | `8d12 + 57` | `160` |'),
    ('some a linha do critico', PECA,
     '| **crítico de `Dupla`** | `16d12 + 57` | `249` | **destrói** | **destrói** |\n', ''),
    ('o corpo do Coro volta para a formula crua', PECA,
     '| **`Coro`** | atacar e comandar na mesma rodada | o da ficha | **`2 ×` a fórmula do tipo** |',
     '| **`Coro`** | atacar e comandar na mesma rodada | o da ficha | `h`, a fórmula crua |'),
    ('SO o livro volta para a regua velha', LIVRO,
     '> **A régua da morte é a vida máxima daquele corpo.**',
     '> **A régua da morte é `5 ×` a vida que a fórmula do tipo dá.**'),
    ('SO o livro perde a clausula de area', LIVRO,
     '> **Área nunca destrói.** Ela derruba como qualquer dano, e só.\n', ''),
    ('a regua da Carranca desgarra da vida', LIVRO,
     '| **régua da morte** | `55` — a vida máxima dela |',
     '| **régua da morte** | `165` — a vida máxima dela |'),
    ('a metade do exemplo do Kaito mente', LIVRO,
     'que não passa de `27`, que é metade da régua',
     'que não passa de `30`, que é metade da régua'),
]

base = monta()
code, saida = roda(base)
print(f'BASE na copia: saida={code}  ' + ('OK' if code == 0 else '>>> A BASE JA FALHA, PARE'))
if code != 0:
    print(saida[-2000:]); sys.exit(1)
shutil.rmtree(os.path.dirname(base))

print()
acendeu = 0
for nome, arq, velho, novo in PERTURBACOES:
    base = monta()
    p = os.path.join(base, arq)
    antes = open(p, encoding='utf-8').read()
    depois = antes.replace(velho, novo, 1)
    if antes == depois:
        print(f'  {nome:<44} SED NAO BATEU — resultado invalido')
        shutil.rmtree(os.path.dirname(base)); continue
    open(p, 'w', encoding='utf-8').write(depois)
    code, saida = roda(base)
    ok = code != 0
    acendeu += ok
    marca = 'acendeu' if ok else '>>> NAO ACENDEU'
    linhas = [l.strip() for l in saida.splitlines() if l.strip().startswith('- [')]
    print(f'  {nome:<44} {marca}')
    for l in linhas[:2]:
        print(f'      {l}')
    shutil.rmtree(os.path.dirname(base))

print(f'\n{acendeu} de {len(PERTURBACOES)} perturbacoes acenderam.')
