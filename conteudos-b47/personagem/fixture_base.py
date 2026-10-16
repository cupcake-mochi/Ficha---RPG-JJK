"""Monta só a fixture de memória, com guarda de escrita fora da entrega.

Reutiliza o prefixo canônico até antes de ANALISE. As duas chamadas guarda()
que regravariam JSON canônico são retiradas da AST da fixture, e as chamadas
de desenho de arte são desativadas pelo modo --exportar-analise já existente.
Não executa a geração de XLSX/GS nem salva o modelo de dezenas de MB.
"""
import ast
import contextlib
import io
import os
from pathlib import Path
import sys
from b47_personagem.fontes_livro import ROOT

ATIVA = False
AREA = Path(__file__).resolve().parent


def _auditar(event,args):
    if not ATIVA: return
    if event=='open':
        path,mode,flags=args
        escrita=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if escrita and not isinstance(path,int):
            p=Path(path).resolve()
            if not p.is_relative_to(AREA): raise PermissionError('Fixture recusou escrita: '+str(p))


sys.addaudithook(_auditar)


def montar():
    global ATIVA
    origem=ROOT/'ficha-v01/monta.py'
    arvore=ast.parse(origem.read_text(encoding='utf8'),filename=str(origem))
    prefixo=[]
    for node in arvore.body:
        if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='_AN' for x in node.targets): break
        # Continua utilizável depois da incorporação: a fixture reconstrói o
        # prefixo anterior à própria frente, para aplicar o módulo uma vez.
        if any(isinstance(x,ast.Name) and x.id in ('_PERSONAGEM','_ENTIDADES') for x in ast.walk(node)):continue
        if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and node.value.func.attr=='guarda': continue
        prefixo.append(node)
    if not any(isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_PECAS' for t in x.targets) for x in prefixo):
        raise ValueError('Prefixo canônico mudou; revisar fixture antes de continuar')
    arvore.body=prefixo
    scope={'__file__':str(origem),'__name__':'fixture_b47_memoria'}
    old_argv=sys.argv;old_bytecode=sys.dont_write_bytecode
    sys.argv=[str(origem),'--exportar-analise'];sys.dont_write_bytecode=True
    try:
        ATIVA=True
        with contextlib.redirect_stdout(io.StringIO()): exec(compile(arvore,str(origem),'exec'),scope)
    finally:
        ATIVA=False;sys.argv=old_argv;sys.dont_write_bytecode=old_bytecode
    return scope
