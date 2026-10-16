# -*- coding: utf-8 -*-
"""Executa ficha-v01/monta.py com capacidades opcionalmente simuladas.

Uso (sempre num processo separado, chamado por comum.py):

    python rodar_gerador.py <raiz> <json de capacidades ou "{}"> <argumentos do monta.py...>

- "{}" = modo real: o gerador roda exatamente como está no SHA em teste.
- Um JSON {"modulo.CONSTANTE": valor} = simulação: troca só essas constantes antes
  de importar o monta.py. Isso NÃO é a redução do integrador; serve para expor
  endereços e quantidades que não acompanham as constantes.

Guarda: sem --exportar-analise/--exportar-pecas o gerador grava .gs e XLSX. Isso só é
aceito quando <raiz> não é o checkout de trabalho (worktree temporária).
"""
import json
import os
import runpy
import sys

raiz = os.path.abspath(sys.argv[1])
trocas = json.loads(sys.argv[2])
argumentos = sys.argv[3:]
checkout = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not any(a.startswith('--exportar-') for a in argumentos) and raiz == checkout:
    sys.exit('recusado: geração completa grava .gs/XLSX; use uma worktree temporária')

sys.path[:0] = [os.path.join(raiz, 'ficha-v01'), os.path.join(raiz, 'ficha'), raiz]
os.chdir(raiz)
ausentes = []
for alvo, valor in trocas.items():
    modulo, nome = alvo.rsplit('.', 1)
    m = __import__(modulo)
    if not hasattr(m, nome):
        ausentes.append(alvo)
        continue
    setattr(m, nome, valor)
if ausentes:
    # Depois da redução real os nomes podem mudar; simulação não deve fingir sucesso.
    sys.exit('constantes inexistentes neste SHA: ' + ', '.join(ausentes))
sys.argv = ['monta.py'] + argumentos
runpy.run_path(os.path.join(raiz, 'ficha-v01', 'monta.py'), run_name='__main__')
