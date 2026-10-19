"""Fachada preferida pelo contrato comum revisão 1.

Uso só pelo integrador: aplica(layout, contexto) / exporta(transformacao).
Módulo isolado não significa integração na ficha nem aplicação nativa.
"""
from copy import deepcopy
from pathlib import Path
import json
from openpyxl.utils import get_column_letter as L
from openpyxl.utils.cell import range_boundaries
import indice_ficha as ix
import ficha_amaldicoada as fa
import ficha_invocacoes as iv
from .fontes_livro import carregar, ROOT, FAIXAS
from .motor import CAMPOS, LEGADO_FORMA
from .planilha import Contrato, emitir, exportar, ref, intervalo, opcoes_campos
from .consumidores import Ambiente, pontes, aplicar


def chave_contrato(grupo,n,campo,aviso):
    if aviso: return f'aviso.custom.{grupo}.{n}'
    campo={'ce':'categoria','classe_0':'classe_zero'}.get(campo,campo)
    return f'custom.{grupo}.{n}.{campo}'


def aplica(layout,contexto):
    obrigatorios={'fam','inv','criacao','pecas','capacidades','inicio','abas'}
    if not obrigatorios<=set(contexto):
        raise ValueError('Contexto incompleto: '+', '.join(sorted(obrigatorios-set(contexto))))
    fam,inv,criacao,pecas=(contexto[k] for k in ('fam','inv','criacao','pecas'))
    livro=carregar()
    desenho=desenhar(layout,contexto['inicio'],contexto['capacidades'])
    c=Contrato({k:contexto['capacidades'][k] for k in CAMPOS},desenho['fontes'],contexto['abas'],
               criacao['catalogo_familias'],pecas['catalogos']['restricao'])
    p=emitir(livro,c)
    # A matriz de nove Famílias é explicitamente fornecida pelo metadata da
    # invocação, sem inventar nove cadastros por consumidor.
    fams=[[fa._A(g['fam'][k],iv.IV) for k in range(9)] for g in inv['fichas_c']]
    family_table=criacao['catalogo_familias']
    a1,a2=family_table.rsplit('!',1)[1].replace('$','').split(':')
    from openpyxl.utils.cell import coordinate_from_string,column_index_from_string
    col,row=coordinate_from_string(a1)
    endrow=coordinate_from_string(a2)[1]
    state_table=intervalo(family_table.rsplit('!',1)[0].strip("'"),column_index_from_string(col),endrow-row+1,4,primeiro=row)
    ambiente=Ambiente(state_table,fam['ROTA'],contexto.get('bloqueia_extensao',fam['ROTA']+'=3'),fams)
    bridges=pontes(p,livro,c,ambiente)
    tr=aplicar(layout,p,bridges,fam,inv,c)
    tr.update(inicio=desenho['inicio'],fim=desenho['fim'],registros=desenho['registros'],
              catalogos=bridges,plano=p,contrato=c,desenho=desenho,contexto=contexto)
    from .usos import aplicar as avisos_uso
    avisos_uso(layout,tr,livro,contexto)
    for aba,celulas in desenho['antes'].items():
        for cel,v in celulas.items(): tr['antes'].setdefault(aba,{}).setdefault(cel,v)
    for aba,celulas in desenho['depois'].items(): tr['depois'].setdefault(aba,{}).update(celulas)
    cfg=ix._aba(layout,'CONFIGURAÇÃO')
    warnings={(a['grupo'],a['vaga']):a['fonte'] for a in p.avisos}
    for g in desenho['registros']:
        fonte=warnings[(g['grupo'],g['n'])]
        valor=f'=IF({fonte}="","","⚠ "&{fonte})'
        cfg['celulas'].append([g['aviso'],valor,desenho['estilos']['nota']])
        tr['antes'].setdefault('CONFIGURAÇÃO',{}).setdefault(g['aviso'],None)
        tr['depois'].setdefault('CONFIGURAÇÃO',{})[g['aviso']]=valor
    opcoes_aux={}
    def auxiliar(aba,key,values):
        if (aba,key) in opcoes_aux:return opcoes_aux[(aba,key)]
        sheet=ix._aba(layout,aba);coluna=sheet['colunas']+1
        for r,v in enumerate(values,2):
            cel=L(coluna)+str(r)
            sheet['celulas'].append([cel,v,None])
            tr['antes'].setdefault(aba,{}).setdefault(cel,None)
            tr['depois'].setdefault(aba,{})[cel]=v
        sheet['colunas']=coluna;sheet['linhas']=max(sheet['linhas'],len(values)+1)
        result=intervalo(aba,coluna,len(values));opcoes_aux[(aba,key)]=result
        return result
    for item in p.validacoes:
        coord=item['fonte'].rsplit('!',1)[1].replace('$','')
        # Uma lista por catálogo/campo, compartilhada pelos dez cartões.
        grupo=next(g for g,fontes in c.fontes.items() if any(item['fonte'] in f.values() for f in fontes))
        key=next(k for f in c.fontes[grupo] for k,v in f.items() if v==item['fonte'])
        source=auxiliar(c.abas[grupo],key,item['opcoes'])
        cfg['menus'].append(dict(onde=coord,tipo='list',formula=source,
                                 vazio_ok=True,mostra_seta=True,estrito=True))
        cfg.setdefault('menus_estritos',[]).append(coord)
    # Família e Restrição são catálogos vivos; não congelar nomes custom.
    for g in desenho['registros']:
        if g['grupo']=='forma':
            for campo,source in [('familia',criacao['catalogo_familias'])]:
                # A opção Nenhuma é acrescentada em auxiliar, junto da lista
                # fornecida; nunca altera o catálogo do livro.
                fim=range_boundaries(source.rsplit('!',1)[-1])[3] if campo=='familia' else pecas['limites']['DADOS_RESTRICOES']['total']+1
                rows=['Nenhuma']+[f'=IFERROR(INDEX({source},{r}),"")' for r in range(1,fim)]
                menu_source=auxiliar(c.abas['forma'],campo,rows)
                cfg['menus'].append(dict(onde=g['campos'][campo],tipo='list',formula=menu_source,
                                        vazio_ok=True,mostra_seta=True,estrito=True))
    # Former shape/function fields are kept in hidden storage for migration and
    # old exports. They are no longer editable gates of a R53 shape.
    sheet=ix._aba(layout,c.abas['forma']);first=sheet['colunas']+1
    tr['legados_forma']=[]
    for j,k in enumerate(LEGADO_FORMA):
        head=L(first+j)+'1';sheet['celulas'].append([head,'legado.'+k,None])
        for g in desenho['registros']:
            if g['grupo']!='forma':continue
            row=g['n']+1;dest=L(first+j)+str(row);old=c.fontes['forma'][g['n']-1][k];new=ref(c.abas['forma'],'$'+L(first+j)+'$'+str(row))
            sheet['celulas'].append([dest,None,None]);raw=L(list(CAMPOS['forma']).index(k)+1)+str(row)
            value=f'=IF(ISBLANK({new}),"",{new})'
            next(x for x in sheet['celulas'] if x[0]==raw)[1]=value;p.celulas[c.abas['forma']][raw]=value
            tr['depois'].setdefault(c.abas['forma'],{})[raw]=value
            c.fontes['forma'][g['n']-1][k]=new
            next(x for x in p.entradas if x['grupo']=='forma' and x['vaga']==g['n'] and x['campo']==k)['fonte']=new
            tr['legados_forma'].append(dict(vaga=g['n'],campo=k,antes=old,depois=new))
    sheet['colunas']=first+len(LEGADO_FORMA)-1
    tr['entradas']=[(x[0],x[2].rsplit('!',1)[1],x[0].endswith('.mestre_viu')) for x in exportar(p,chave_contrato) if x[3]=='configuração' and not any(x[0].startswith('custom.forma.') and x[0].endswith('.'+k) for k in LEGADO_FORMA)]
    return tr


def exporta(tr):
    out=exportar(tr['plano'],chave_contrato)
    callback=tr['contexto'].get('chave_aviso_uso')
    if callback:
        for item in tr.get('avisos_uso',[]):
            f=item['fonte']
            out.append([callback(item['grupo'],item['n']),'='+f+'&""',f.replace('$',''),'aviso'])
    if len({x[0] for x in out})!=len(out):raise ValueError('Chaves de uso colidem com o contrato de cadastro')
    return out


ROTULOS={'tipo':'TIPO','nome':'NOME','base':'BASE DO LIVRO','mestre_viu':'MESTRE VIU',
         'familia':'FAMÍLIA','peso':'PESO','resolucao':'RESOLUÇÃO','resultado':'RESULTADO',
         'exige_tr':'EXIGE TR','classe_0':'CLASSE 0','restricao_embutida':'RESTRIÇÃO EMBUTIDA',
         'ce':'CATEGORIA DE EFEITO','nivel_minimo':'NÍVEL MÍNIMO','refino_minimo':'REFINO / LAPIDAÇÃO',
         'escolha':'ESCOLHA','rota':'ROTA','alcance_escada':'ESCADA DE ALCANCE','area_escada':'ESCADA DE ÁREA'}


def desenhar(layout,inicio,capacidades):
    """Cartões no molde B:G/J:O aprovado, depois do fim informado.

    A organização definitiva de D continua com o integrador. Nenhum controle
    anterior é deslocado. Os campos de alcance/área refinam o quadro aprovado.
    """
    config=ix._aba(layout,'CONFIGURAÇÃO')
    if type(inicio) is not int or inicio<=config['linhas']:
        raise ValueError('Início deve vir depois do fim real de CONFIGURAÇÃO')
    styles={v[0]:v[2] for v in config['celulas']}
    st=dict(secao=styles['B9'],rotulo=styles['B10'],entrada=styles['C11'],caixa=styles['B11'],nota=styles['B5'])
    texto=deepcopy(layout['estilos'][st['entrada']]);texto[3]=['left','top',True,0]
    if texto not in layout['estilos']: layout['estilos'].append(texto)
    st['texto']=layout['estilos'].index(texto)
    tr=dict(inicio=inicio,antes={},depois={},fontes={},registros=[],estilos=st)
    usadas={x[0] for x in config['celulas']}
    def box(r,c,value=None,ec=None,er=None,kind='entrada',nota=None):
        cel=L(c)+str(r)
        if cel in usadas: raise ValueError('Área ocupada: CONFIGURAÇÃO!'+cel)
        usadas.add(cel)
        config['celulas'].append([cel,value,st[kind]])
        config.setdefault('notas',{})[cel]=nota or 'Em branco herda a base escolhida. Sem base, preencha os campos próprios. Texto não é automação.'
        if (ec and ec!=c) or (er and er!=r): config['mescladas'].append(cel+':'+L(ec or c)+str(er or r))
        tr['antes'].setdefault('CONFIGURAÇÃO',{})[cel]=None
        tr['depois'].setdefault('CONFIGURAÇÃO',{})[cel]=value
        return cel
    row=inicio
    titulos={'forma':'FORMAS CUSTOM','aptidao':'APTIDÕES / BÊNÇÃOS CUSTOM','talento':'TALENTOS CUSTOM'}
    for grupo,campos in CAMPOS.items():
        cap=capacidades[grupo]
        if type(cap) is not int or not 1<=cap<=30: raise ValueError('Capacidade inválida: '+grupo)
        box(row,2,titulos[grupo],ec=15,kind='secao'); row+=3
        anteriores=[k for k in campos if k not in ('tipo','nome','mestre_viu','requisitos','efeito')]
        escalares=[k for k in anteriores if not(grupo=='forma' and k in LEGADO_FORMA)]
        altura=8+len(anteriores)+14
        tr['fontes'][grupo]=[]
        for n in range(1,cap+1):
            r=row+(n-1)//2*altura;c=2 if n%2 else 10
            box(r,c,titulos[grupo].replace(' CUSTOM','')+' · '+str(n),ec=c+5,kind='secao')
            box(r+1,c,'TIPO',ec=c+3,kind='rotulo')
            coords={'tipo':box(r+2,c,None if grupo=='aptidao' else ('Forma' if grupo=='forma' else 'Talento'),ec=c+3)}
            box(r+1,c+4,'MESTRE VIU',ec=c+5,kind='rotulo')
            coords['mestre_viu']=box(r+2,c+4,False,ec=c+5,kind='caixa',nota='Lembrete. Aprovação pertence ao bot no chat.')
            box(r+3,c,'NOME',ec=c+5,kind='rotulo');coords['nome']=box(r+4,c,ec=c+5)
            for offset,k in enumerate(escalares,5):
                label=ROTULOS.get(k)
                if label is None:
                    d,resto=k.split('_',1)
                    contexto,faixa=resto.split('_',1)
                    label=('ALC' if d=='alcance' else 'ÁREA')+' · '+('P' if contexto=='personagem' else 'E')+' · '+faixa.replace('classes_','').replace('classe_','').replace('_',' ')
                box(r+offset,c,label,ec=c+2,kind='rotulo')
                coords[k]=box(r+offset,c+3,ec=c+5)
            # Keep former sources in metadata until aplica() redirects them to
            # technical storage. No obsolete input or label is drawn.
            if grupo=='forma':
                for k in LEGADO_FORMA:coords[k]=L(c+3)+str(r+5+anteriores.index(k))
            texts=[]
            for offset,k in [(6+len(escalares),'requisitos'),(12+len(escalares),'efeito')]:
                box(r+offset,c,k.upper(),ec=c+5,kind='rotulo')
                coords[k]=box(r+offset+1,c,er=r+offset+4+(4 if grupo=='forma' and k=='efeito' else 0),ec=c+5,kind='texto')
                texts.append([k,r+offset+1])
            aviso=L(c)+str(r+altura-3)
            # Reservar a mescla e a nota; a fórmula é inserida após emitir.
            config['mescladas'].append(aviso+':'+L(c+5)+str(r+altura-2))
            config.setdefault('notas',{})[aviso]='Avisos do cadastro. Inválidos permanecem exportados e saem dos menus.'
            tr['registros'].append(dict(grupo=grupo,n=n,r=r,c=c,campos=coords,aviso=aviso,textos=texts))
            tr['fontes'][grupo].append({k:ref('CONFIGURAÇÃO','$'+coordinate(coords[k])) for k in campos})
        for n in range(0,cap,2):
            pair=[g for g in tr['registros'] if g['grupo']==grupo and g['n'] in (n+1,n+2)]
            for k in ('requisitos','efeito'):
                textos=[]
                for g in pair:
                    largura=sum(next((w for lo,hi,w in config['colunas_larg'] if lo<=c<=hi),4)*8-1 for c in range(g['c'],g['c']+6))-12
                    rr=next(r for key,r in g['textos'] if key==k)
                    textos.append([largura,[g['campos'][k]],rr,8 if grupo=='forma' and k=='efeito' else 4,0])
                config.setdefault('esticam',[]).append(dict(gatilhos=[g['campos'][k] for g in pair],aba='CONFIGURAÇÃO',minima=25,textos=textos))
        row+=((cap+1)//2)*altura+3
    tr['fim']=row-1
    config['linhas_alt'] += [[r,18.75] for r in range(inicio,tr['fim']+1)]
    config['linhas']=tr['fim']
    return tr


def coordinate(cel):
    from openpyxl.utils.cell import coordinate_from_string
    col,row=coordinate_from_string(cel)
    return col+'$'+str(row)
