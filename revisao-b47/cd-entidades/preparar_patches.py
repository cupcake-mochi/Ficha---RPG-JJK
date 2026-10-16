# -*- coding: utf-8 -*-
"""Refaz o patch 01 (entidades no gerador) por âncoras, numa worktree já preparada.

    python preparar_patches.py <worktree> <saida.patch>

A worktree deve estar na base desejada, com as outras séries já aplicadas se for o caso (por exemplo,
a série de personagem). O script copia o módulo, aplica as edições abaixo e grava `git diff` dos
cinco alvos. Cada âncora precisa aparecer uma única vez; senão o script para sem gravar nada.

Ordem adotada: entidades logo depois de custom_danos, no `aplica` e nas linhas ANALISE. Assim as linhas
ANALISE novas ficam antes de qualquer `_AN_FIM_PECAS` de outra frente e continuam nos PecasAnalise*.gs.
"""
import shutil
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
wt, saida = Path(sys.argv[1]), Path(sys.argv[2])

EDICOES = {
    'ficha-v01/monta.py': [
        ("_DANOS = custom_danos.aplica(LAYOUT, {'inv': _FIV, 'custom': _CUSTOM})\n",
         "_DANOS = custom_danos.aplica(LAYOUT, {'inv': _FIV, 'custom': _CUSTOM})\n"
         "# B47 C+D: Tipos e Talentos de entidade custom, depois do fim calculado da seção anterior.\n"
         "import entidades_custom\n"
         "_ENTIDADES = entidades_custom.aplica(LAYOUT, {'fam': _FAM, 'inv': _FIV, 'criacao': _CRIACAO})\n"),
        ("for _new in (_CONDICOES, _DANOS):", "for _new in (_CONDICOES, _DANOS, _ENTIDADES):"),
        ("_AN['linhas'].extend(custom_danos.exporta(_DANOS))\n",
         "_AN['linhas'].extend(custom_danos.exporta(_DANOS))\n_AN['linhas'].extend(entidades_custom.exporta(_ENTIDADES))\n"),
        ("                   'condicoes': _CONDICOES, 'danos': _DANOS},arquivo,ensure_ascii=False)",
         "                   'condicoes': _CONDICOES, 'danos': _DANOS,\n"
         "                   'entidades': {k: _ENTIDADES[k] for k in ('registros', 'catalogos', 'capacidades', 'inicio', 'fim')}},\n"
         "                  arquivo,ensure_ascii=False)"),
        ("""                "DanosPainel.gs": ("CONFIGURAÇÃO",1,16,_DANOS['inicio']-2,_DANOS['fim']),""",
         """                "DanosPainel.gs": ("CONFIGURAÇÃO",1,16,_DANOS['inicio']-2,_DANOS['fim']),
                "EntidadesPainel.gs": ("CONFIGURAÇÃO",1,16,_ENTIDADES['inicio']-2,_ENTIDADES['fim']),"""),
    ],
    'ficha/emitir_gs.py': [
        ("""             "Danos.gs": ("ABAS_DOS_DANOS", ("DADOS_DANOS",))}""",
         """             "Danos.gs": ("ABAS_DOS_DANOS", ("DADOS_DANOS",)),
             "Entidades.gs": ("ABAS_DAS_ENTIDADES", ("DADOS_ENTIDADES",))}"""),
        ("""                "DanosPainel.gs": "VALORES_DANOS_",\n""",
         """                "DanosPainel.gs": "VALORES_DANOS_",\n                "EntidadesPainel.gs": "VALORES_ENTIDADES_",\n"""),
    ],
    'ficha/modelo.gs.js': [
        ("'ANALISE',\n    'CONFIGURAÇÃO', 'DADOS_CONFIG'];", "'DADOS_ENTIDADES', 'ANALISE',\n    'CONFIGURAÇÃO', 'DADOS_CONFIG'];"),
        ("""  if (typeof VALORES_DANOS_ !== 'undefined' && VALORES_DANOS_) juntarValores_(VALORES_DANOS_);
  juntarContratosPecas_();""", """  if (typeof VALORES_DANOS_ !== 'undefined' && VALORES_DANOS_) juntarValores_(VALORES_DANOS_);
  if (typeof VALORES_ENTIDADES_ !== 'undefined' && VALORES_ENTIDADES_) juntarValores_(VALORES_ENTIDADES_);
  juntarContratosPecas_();"""),
        ("""if (typeof ABAS_DOS_DANOS !== 'undefined' && ABAS_DOS_DANOS) juntarAbas_(ABAS_DOS_DANOS);
""", """if (typeof ABAS_DOS_DANOS !== 'undefined' && ABAS_DOS_DANOS) juntarAbas_(ABAS_DOS_DANOS);
if (typeof ABAS_DAS_ENTIDADES !== 'undefined' && ABAS_DAS_ENTIDADES) juntarAbas_(ABAS_DAS_ENTIDADES);
"""),
        ("""if (typeof VALORES_DANOS_ !== 'undefined' && VALORES_DANOS_) juntarValores_(VALORES_DANOS_);
juntarContratosPecas_();""", """if (typeof VALORES_DANOS_ !== 'undefined' && VALORES_DANOS_) juntarValores_(VALORES_DANOS_);
if (typeof VALORES_ENTIDADES_ !== 'undefined' && VALORES_ENTIDADES_) juntarValores_(VALORES_ENTIDADES_);
juntarContratosPecas_();"""),
        ("""    throw new Error('Falta o Danos.gs: cole todos os arquivos antes de construir.');
  }""", """    throw new Error('Falta o Danos.gs: cole todos os arquivos antes de construir.');
  }
  if (typeof ABAS_DAS_ENTIDADES === 'undefined' || !ABAS_DAS_ENTIDADES) {
    throw new Error('Falta o Entidades.gs: cole todos os arquivos antes de construir.');
  }"""),
    ],
    'regressao-construir.js': [
        ("'Restricoes.gs', 'PecasPainel.gs', 'PecasAnalise1.gs']",
         "'Restricoes.gs', 'PecasPainel.gs', 'PecasAnalise1.gs', 'Entidades.gs', 'EntidadesPainel.gs']"),
    ],
}

textos = {}
for alvo, subs in EDICOES.items():
    s = (wt / alvo).read_text(encoding='utf-8')
    for a, b in subs:
        if s.count(a) != 1:
            sys.exit(f'âncora {s.count(a)}× em {alvo}: {a[:70]!r}')
        s = s.replace(a, b)
    textos[alvo] = s
# o estado de partida (com outras séries já aplicadas) vai ao índice: o diff fica só com estas edições
subprocess.run(['git', 'add', '--', *EDICOES], cwd=wt, check=True)
for alvo, s in textos.items():
    (wt / alvo).write_text(s, encoding='utf-8', newline='')
shutil.copyfile(AQUI / 'entidades_custom.py', wt / 'ficha-v01' / 'entidades_custom.py')
subprocess.run(['git', 'add', '-N', 'ficha-v01/entidades_custom.py'], cwd=wt, check=True)
diff = subprocess.run(['git', 'diff', '--', 'ficha-v01/entidades_custom.py', *EDICOES], cwd=wt, check=True,
                      capture_output=True, text=True).stdout
saida.parent.mkdir(parents=True, exist_ok=True)
saida.write_text(diff, encoding='utf-8', newline='')
print(f'{saida}: {diff.count(chr(10))} linhas')
