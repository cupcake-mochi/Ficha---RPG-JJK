"""Extrator R53 por IDs publicados; falhas são reunidas antes de escrever.

Não extrai permissões da prosa do jogador. Opções fixas do livro são desdobradas
sem aumentar a contagem das 61 entradas. Requer apenas a biblioteca padrão.
"""
from pathlib import Path
import hashlib
import json
import re

RAIZ = Path(__file__).resolve().parents[1]
FONTE = RAIZ / 'referencias-r53' / 'BLOCOS-R53.json'
PESOS = {'Leve': 1, 'Média': 2, 'Pesada': 3}
TRS=['Físico','Vigor','Intelecto','Espírito']


def extrair():
    blocos = json.loads(FONTE.read_text())
    erros, entradas, opcoes = [], {'melhorias': [], 'restricoes': []}, []
    condicoes = {nome: peso for sec,peso in [('dano--leves','Leve'),('dano--medias','Média'),('dano--pesadas','Pesada')] for nome in re.findall(r'^### (.+)$', blocos[sec], re.M) if nome not in {'Remoção','Testes de saída'}}
    if len(condicoes) != 13: erros.append('condições compráveis: esperado 13, recebido '+str(len(condicoes)))
    for tipo, prefixo, campo in [('melhorias', 'catalogo--melhoria-', 'Preço'),
                                ('restricoes', 'catalogo--restricao-', 'Devolução')]:
        for id_, texto in blocos.items():
            if not id_.startswith(prefixo):
                continue
            titulo = re.match(r'^## (.+)', texto)
            if not titulo:
                erros.append(id_ + ': título'); continue
            nome = titulo[1]
            familia = re.search(r'\*\*Família: (.+?)\.\*\*', texto)
            preco = re.search(r'\*\*' + campo + r': (.+?)\.\*\*', texto)
            if tipo == 'melhorias' and not familia:
                erros.append(id_ + ': Família')
            especiais = {'Longe', 'Maior', 'Condição', 'Concentrada / Duradoura', 'Efeito Próprio', 'Queima-Roupa'}
            if not preco and nome not in {'Longe', 'Maior'}:
                erros.append(id_ + ': ' + campo)
            fam = familia[1] if familia else ''
            bruto = preco[1] if preco else 'modalidades'
            entrada = dict(id=id_, nome=nome, familia=fam, preco_publicado=bruto, texto=texto)
            entradas[tipo].append(entrada)
            variantes = []
            if nome in {'Longe', 'Maior'}:
                linhas = re.findall(r'^\| (Um degrau|Três degraus) \| (Leve|Média|Pesada) \|', texto, re.M)
                if len(linhas) != 2: erros.append(id_ + ': duas modalidades')
                variantes = [(nome + ' · ' + mod.lower(), peso, 1 if mod == 'Um degrau' else 3,
                              2 if mod == 'Um degrau' else 1) for mod, peso in linhas]
            elif nome == 'Terreno':
                variantes=[(nome+' · '+v,'Leve',0,1) for v in ['terreno difícil','obscurecimento denso']]
            elif nome == 'Desarma o Feitiço':
                variantes=[(nome+' · '+v,'Média',0,1) for v in ['efeito contínuo','barreira','item','Selo']]
            elif nome == 'Abre Ferida':
                variantes=[(nome+' · TR '+v,'Leve',0,1) for v in TRS]
            elif nome == 'Recuo':
                variantes=[(nome+' · '+cond,peso,0,1) for cond,peso in condicoes.items() if peso!='Pesada']
            elif nome == 'Fraqueza':
                variantes=[(nome+' · TR '+v,'Leve' if v in ['Vigor','Intelecto'] else 'Média',0,1) for v in TRS]
            elif nome == 'Firmeza':
                variantes = [(nome + ' · ' + mod, 'Leve', 0, 1) for mod in ['perícia', 'ofício', 'TR']]
            elif nome == 'Concentrada / Duradoura':
                variantes = [('Concentrada', 'Leve', 0, 1), ('Duradoura', 'Média', 0, 1)]
            elif nome == 'Condição':
                variantes = [('Condição · ' + cond, peso, 0, 1) for cond, peso in condicoes.items()]
            elif nome == 'Efeito Próprio':
                # A Família e os limites próprios serão lidos do cadastro aprovado, nunca inferidos do nome.
                variantes = [(nome + ' · ' + peso, peso, 0, 1) for peso in PESOS]
            elif nome == 'Queima-Roupa':
                variantes = [(nome, 'Leve', 0, 1)]  # Média em Projétil: cálculo contextual.
            elif 'Leve ou Média' in bruto:
                variantes = [(nome + ' · ' + peso, peso, 0, 1) for peso in ['Leve', 'Média']]
            else:
                peso = bruto.split(',')[0]
                if peso not in PESOS:
                    erros.append(id_ + ': preço não representado: ' + bruto); continue
                variantes = [(nome, peso, 0, 2 if nome == 'Mais Um' else 1)]
            for rotulo, peso, degraus, repeticoes in variantes:
                opcoes.append(dict(rotulo=rotulo, nome=nome, tipo=tipo, familia=fam,
                                   peso=PESOS[peso], degraus=degraus, repeticoes=repeticoes,
                                   classe_minima=3 if nome == 'Toca a Alma' else 0,
                                   tr=int(nome in {'Condição', 'Prende', 'Cerca'}),
                                   frequencia=int(nome in {'Uma Vez', 'Condicional', 'Aquecer'}),
                                   id=id_,rotulo_base=rotulo,proprio=0,cadastro_valido=int(nome!='Efeito Próprio'),
                                   controle_compat=int(nome in {'Condição','Prende','Cerca','Terreno'})))
    for tipo, n in [('melhorias',61),('restricoes',19)]:
        if len(entradas[tipo]) != n: erros.append(f'{tipo}: {len(entradas[tipo])}, esperado {n}')
    if erros:
        raise ValueError('Padrões R53 ausentes ou sem representação:\n' + '\n'.join(erros))
    return dict(edicao='R53', esquema=2, fonte_sha256=hashlib.sha256(FONTE.read_bytes()).hexdigest(),
                **entradas, opcoes=opcoes,
                fontes={k:v for k,v in blocos.items() if k.startswith(('fundamento--','construcao--entidades-'))})


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(); p.add_argument('--confere', action='store_true'); a=p.parse_args()
    destino=RAIZ/'r53/catalogo.json'
    conteudo=json.dumps(extrair(), ensure_ascii=False, indent=2)+'\n'
    if a.confere:
        if destino.read_text() != conteudo: raise SystemExit('r53/catalogo.json desatualizado')
    else: destino.write_text(conteudo)
    print('R53: 61 Melhorias, 19 Restrições; opções fixas e fontes conferidas.')
