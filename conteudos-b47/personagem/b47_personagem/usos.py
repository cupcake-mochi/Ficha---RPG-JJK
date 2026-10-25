"""Avisos de aquisição nas cartas existentes, sem interpretar descrições.

Os campos de aprendizado/concessão não existem como controles estruturados na
base. O integrador pode fornecer expressões em verificacoes; quando não há
fonte estruturada, a carta pede conferência manual e preserva o requisito.
"""
from openpyxl.utils import get_column_letter as L
import indice_ficha as ix
import ficha_amaldicoada as fa
from .planilha import intervalo,criterio,ref,q


def aplicar(layout,tr,livro,contexto):
    fam=contexto['fam'];plano=tr['plano']
    aba=ix._aba(layout,fa.DADOS_AM)
    cells={c[0]:c for c in aba['celulas']}
    start=aba['colunas']+2
    antes,depois=tr['antes'].setdefault(fa.DADOS_AM,{}),tr['depois'].setdefault(fa.DADOS_AM,{})
    def por(cel,value):
        old=cells.get(cel)
        if old and old[1]==value:return
        antes.setdefault(cel,old[1] if old else None);depois[cel]=value
        if old:old[1]=value
        else:
            record=[cel,value,None];cells[cel]=record;aba['celulas'].append(record)
    indices=ix.indice(layout)
    verificacoes=dict(contexto.get('verificacoes',{}))
    # A rota resolvida já incorpora as Origens custom: 1 é Fundamento/Técnica
    # Inata; 2 é Sem Técnica, 3 é Marcial e 4 é Marcial sem energia. Ritual
    # não precisa de uma confirmação manual incondicional nesse caso.
    verificacoes.setdefault('tecnica_inata',f'({fam["ROTA"]}=1)')
    nivel,refino=fam['H']['nível'],fam['H']['refino']
    avisos=[]
    t=plano.tabelas['aptidao']
    nomes=t['nomes']
    def lookup(k,n,default='""'):
        src=intervalo(t['aba'],t['colunas'][k],t['total'])
        return f'IFERROR(INDEX({src},MATCH({criterio(n)},{nomes},0)),{default})'
    headers=['aptidão escolhida','identidade herdada','grupo da aquisição','avisos de aquisição','escolhas consumidas']
    for i,h in enumerate(headers):por(L(start+i)+'1',h)
    for n,g in enumerate(fam['aptidoes_c'],1):
        r=n+1
        nome='$'+L(start)+str(r);ident='$'+L(start+1)+str(r);grupo='$'+L(start+2)+str(r)
        erro='$'+L(start+3)+str(r)
        por(L(start)+str(r),'='+fa._A(g['nome'],fa.AM)+'&""')
        por(L(start+1)+str(r),f'=IF({nome}="","",IF({lookup("identidade",nome)}="",{nome},{lookup("identidade",nome)}))')
        por(L(start+2)+str(r),f'=IF(LEFT({ident},16)="Aptidão Própria (","Aptidão Própria",IF(LEFT({ident},15)="Bênção Própria (","Bênção Própria",{ident}))')
        tipo=lookup('tipo',nome)
        ce=lookup('ce',nome,'0')
        minimo=lookup('refino_minimo',nome,'1')
        voto=verificacoes.get('voto_iniciante','FALSE')
        minimo=f'IF(AND({ident}="Domínio Simples",{voto},{minimo}=5),4,{minimo})'
        minimo=f'MAX({minimo},IF({tipo}="Bênção",IF({ce}=3,7,IF({ce}=2,4,1)),1))'
        concessao=verificacoes.get('concessoes',{})
        dispensa='OR(FALSE'+''.join(f',AND({ident}={q(k)},{v})' for k,v in concessao.items())+')'
        def falta(cond,msg):return f'IF(AND(NOT({dispensa}),{cond}),{q(msg)},"")'
        menu=intervalo(tr['catalogos']['aptidoes']['aba'],tr['catalogos']['aptidoes']['coluna']+5,t['total'])
        checks=[f'IF(COUNTIF({nomes},{criterio(nome)})=0,"Aptidão não cadastrada ou com erro","")',
            f'IF(COUNTIF({menu},{criterio(nome)})=0,"Rota/origem incompatível ou capacidade inicial automática","")',
            falta(f'{nivel}<{lookup("nivel_minimo",nome,"1")}', 'Nível mínimo não atendido'),
            falta(f'{refino}<{minimo}','Refino/Lapidação mínimo não atendido')]
        if r>2:
            prev='$'+L(start+2)+'$2:'+grupo
            checks.append(f'IF(COUNTIF({prev},{criterio(grupo)})>1,"Aptidão/Bênção repetida","")')
        for a in livro['aptidao']:
            cond=f'{ident}={q(a["identidade"])}'
            for pred in a.get('predecessoras',()):
                count='0' if r==2 else f'COUNTIF(${L(start+1)}$2:${L(start+1)}{r-1},{q(pred)})'
                checks.append(falta(f'AND({cond},{count}=0)','Exige aquisição anterior: '+pred))
            atributo=a.get('atributo')
            if atributo:
                campo=indices.get('atr_'+atributo[0])
                if campo: checks.append(falta(f'AND({cond},{ref("FICHA",campo)}<{atributo[1]})','Exige '+atributo[0]+' '+str(atributo[1])))
        # Requisitos alternativos e de história são campos estruturados apenas
        # quando fornecidos pelo contrato do integrador. Ausência pede conferência.
        especiais={
            'Cesta Oca de Vime':('cesta_permitida','Conferir Encarnado ou treino em História'),
            'Pétala':('petala_permitida','Conferir Descendente ou aprendizado de clã'),
            'Domínio Simples':('aprendeu_dominio_simples','Conferir aprendizado de Domínio Simples'),
            'Extensão de Domínio':('aprendeu_extensao','Conferir aprendizado de Extensão de Domínio'),
            'Ritual':('tecnica_inata','Conferir Técnica Inata'),
        }
        for identidade,(campo,msg) in especiais.items():
            ok=verificacoes.get(campo)
            checks.append(falta(f'AND({ident}={q(identidade)},NOT({ok}))' if ok else f'{ident}={q(identidade)}',msg))
        if 'Represália' in {a['nome'] for a in livro['aptidao']}:
            forca,destreza=indices.get('atr_Força'),indices.get('atr_Destreza')
            if forca and destreza:checks.append(falta(f'AND({ident}="Represália",MAX({ref("FICHA",forca)},{ref("FICHA",destreza)})<4)','Exige Força ou Destreza 4'))
        for k,expr in enumerate(checks):por(L(start+8+k)+str(r),'='+expr)
        faixa='$'+L(start+8)+str(r)+':$'+L(start+7+len(checks))+str(r)
        por(L(start+3)+str(r),f'=IF({nome}="","",TEXTJOIN(" · ",TRUE,{faixa}))')
        por(L(start+4)+str(r),f'=IF({nome}="",0,IF({lookup("escolha",nome)}="Gratuita",0,1))')
        avisos.append(dict(grupo='aptidao',n=n,fonte=ref(fa.DADOS_AM,erro)))
        # O requisito da carta já era texto; acrescenta avisos sem alterar o
        # nome, a CE, o efeito ou a entrada livre do jogador.
        c,first,last,width=fam['D'].T['carta_aptidao']
        cel=L(c+2)+str(first+n-1)
        original=cells[cel][1]
        por(cel,f'={original[1:]}&IF({erro}="",""," · ⚠ "&{erro})')
    start+=7
    for n,g in enumerate(fam['passivas_c'],1):
        r=n+1
        nome=fa._A(g['nome'],fa.AM)
        table=tr['catalogos']['passivas'];menu=intervalo(table['aba'],table['coluna']+5,table['ultimo']-1)
        talt=plano.tabelas['talento']
        nomes=talt['nomes']
        checks=[f'IF(COUNTIF({nomes},{criterio(nome)})=0,"Talento não cadastrado ou com erro","")',
                f'IF(COUNTIF({menu},{criterio(nome)})=0,"Talento incompatível com a rota","")']
        fonte=ref(fa.DADOS_AM,'$'+L(start)+str(r))
        por(L(start)+str(r),f'=IF({nome}="","",TEXTJOIN(" · ",TRUE,{",".join(checks)}))')
        # A carta já calcula nível, custo CE e abertura do Leque; preservá-los.
        c,first,last,width=fam['D'].T['carta_passiva']
        cel=L(c+5)+str(first+n-1);original=cells[cel][1]
        por(cel,f'={original[1:]}&IF({fonte}="",""," · ⚠ "&{fonte})')
        avisos.append(dict(grupo='talento',n=n,fonte=fonte))
    from openpyxl.utils.cell import coordinate_from_string,column_index_from_string
    aba['colunas']=max(column_index_from_string(coordinate_from_string(c)[0]) for c in cells)
    aba['linhas']=max(aba['linhas'],len(fam['aptidoes_c'])+1,len(fam['passivas_c'])+1)
    if aba.get('colunas_larg'):aba['colunas_larg'][0][1]=aba['colunas']
    tr['avisos_uso']=avisos
    return avisos
