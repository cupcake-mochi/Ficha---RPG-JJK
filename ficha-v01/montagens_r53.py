"""Integra o núcleo R53 ao gerador e aos cartões; sem importar Excel no Google.

O editor guarda colunas independentes por Classe. Só a versão selecionada no
cartão alimenta a linha de cálculo. Nome/Classe continuam no cartão original.
Não migra personagens durante a geração; a migração é uma operação separada.
"""
import copy
import json
import re
import sys
from pathlib import Path
from openpyxl.utils import get_column_letter as L
from openpyxl.utils.cell import coordinate_to_tuple

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'r53'))
import modelo as M
import indice_ficha as ix

EDITOR='MONTAGENS'
DADOS='DADOS_R53'
CATALOGO='DADOS_R53_CATALOGO'
# Escolhas têm campos próprios; nenhum efeito é inferido da descrição do jogador.
CAMPOS=[
 ('preparada','Versão preparada','bool'),('forma','Forma','forma'),
 ('funcao1','Função 1','funcao'),('pontos1','Pontos · função 1','inteiro'),
 ('funcao2','Função 2','funcao'),('pontos2','Pontos · função 2','inteiro'),
 ('funcao3','Função 3','funcao'),('pontos3','Pontos · função 3','inteiro'),
 ('m1','Melhoria 1','melhoria'),('m2','Melhoria 2','melhoria'),('m3','Melhoria 3','melhoria'),('m4','Melhoria 4','melhoria'),
 ('r1','Restrição 1','restricao'),('r1_valida','Exigência 1 continua válida','bool'),
 ('r2','Restrição 2','restricao'),('r2_valida','Exigência 2 continua válida','bool'),
 ('controle','Reforço de Controle','controle'),('pessoal','Só pode afetar quem executa','bool'),
 ('permite_dano','Regra permite dano','bool'),('permite_cura','Regra permite cura','bool'),
 ('permite_vt','Regra permite vida temporária','bool'),('permite_alma','Regra trata diretamente da alma','bool'),
 ('origem_permissao','Permissão da Regra/definição','texto'),
 ('dest_dano','Destinatários do dano','texto'),('dest_cura','Destinatários da cura','texto'),('dest_vt','Destinatários da vida temporária','texto'),
 ('res_dano','Resolução do dano','resolucao'),('dependencias','Independência/dependências das parcelas','texto'),
 ('execucao','Execução da entidade','execucao'),('fragil_pago','Gasto interrompível de Frágil','inteiro'),
 ('migracao','Revisão do registro antigo','migracao'),
 ('tr_dano','Tipo de TR · dano','tr'),('tr_controle','Tipo de TR · Controle','tr')]
PASSO=len(CAMPOS)+5
FUNCOES={'Dano':('dano','p_dano'),'Cura':('cura','p_cura'),'PV temporários':('vt','p_vt')}
DEFAULTS_EDITOR={**M.DEFAULTS,**{f'funcao{i}':'' for i in range(1,4)},**{f'pontos{i}':0 for i in range(1,4)}}


def funcoes_selecionadas(campos,index,ncol):
    """Traduz três listas/quantidades para entradas tipadas do núcleo existente."""
    selecionado=lambda k:f'INDEX({ref(EDITOR,f"$B${campos[k]}:{L(ncol+1)}${campos[k]}")},1,{index})'
    out={}
    for label,(flag,points) in FUNCOES.items():
        testes=[f'{selecionado("funcao"+str(i))}="{label}"' for i in range(1,4)]
        out[flag]='=IFERROR(OR('+','.join(testes)+'),FALSE)'
        out[points]='=IFERROR(SUM('+','.join(f'IF({testes[i-1]},{selecionado("pontos"+str(i))},0)' for i in range(1,4))+'),0)'
    return out


def avisos_funcoes(campos,index,ncol):
    cel=lambda k:f'INDEX({ref(EDITOR,f"$B${campos[k]}:{L(ncol+1)}${campos[k]}")},1,{index})'
    repetidas=[f'AND({cel("funcao"+str(i))}<>"",{cel("funcao"+str(i))}={cel("funcao"+str(j))})' for i,j in [(1,2),(1,3),(2,3)]]
    soltos=[f'AND({cel("funcao"+str(i))}="",{cel("pontos"+str(i))}<>0)' for i in range(1,4)]
    return f'IFERROR(TEXTJOIN(" · ",TRUE,IF(OR({",".join(repetidas)}),"Função repetida: use uma linha por função",""),IF(OR({",".join(soltos)}),"Escolha a função dos pontos atribuídos","")),"")'



def ref(aba,a1): return "'"+aba.replace("'","''")+"'!"+a1

def folha(nome,linhas,colunas,oculta=False):
    return dict(nome=nome,estado='hidden' if oculta else 'visible',linhas=linhas,colunas=colunas,
        padrao=['Roboto',10,'#EEDFEA'],fundo_base='#1B131F' if not oculta else '#FFFFFF',grade=False,
        celulas=[],mescladas=[],menus=[],condicional=[],imagens=[],colunas_larg=[],linhas_alt=[],altura_padrao=21,
        grupos={'linhas':[],'colunas':[]},notas={},paleta_fixa=True,validacao_em_matriz=True)


def contextos(fam,inv):
    out=[];G=fam['G'];H=fam['H']
    def pessoal(id_,cel,modo,**extra):
        out.append(dict(id=id_,aba='FICHA AMALDIÇOADA',cel=copy.deepcopy(cel),modo=modo,
                        nivel=H['nível'],classe_maxima=H['maior classe'],dados_zero=H['classe 0 dados'],
                        cd=ref('FICHA AMALDIÇOADA',G['cd']),entidade=None,**extra))
    for rot,lib,n,cel in fam['lugares']:
        r,c=coordinate_to_tuple(cel['classe'])
        pessoal(('liberacao.' if lib else 'feitico.')+str(n),cel,'Liberação Máxima' if lib else 'Comum',linha_funcao=r+6,coluna=c)
    for i,cel in enumerate(fam['zero_c'],1):
        cel=copy.deepcopy(cel);cel['mel']=[cel['mel']];cel['res']=[cel['res']]
        pessoal('classe0.'+str(i),cel,'Classe 0')
    tm=dict(nome=G['tm_nome'],forma=G['tm_forma'],dano=G['tm_dano'],pe=G['tm_pe'],
            conta=G['tm_montagem'],como=L(4)+str(G['tm_como']),mel=fam.get('tm_mel',[]),res=[])
    pessoal('maxima.1',tm,'Técnica Máxima')
    for i,tipo,n,cel,titulo,abre in inv['cartas']:
        r,c=coordinate_to_tuple(cel['classe']); cf=inv['colf']
        source=lambda k:ref('DADOS_INVOC',L(cf[k])+str(i+2))
        out.append(dict(id=f'entidade.{i+1}.{tipo}.{n+1}',aba='INVOCAÇÕES',cel=copy.deepcopy(cel),
            modo='Básica' if tipo=='bas' else 'Entidade',extra=(tipo=='ext'),nivel=source('n'),classe_maxima=source('cl'),
            dados_zero=source('db'),cd=source('cd'),entidade=i,linha_funcao=r+4,coluna=c))
    for i,ficha in enumerate(inv['fichas_c']):
        source=lambda k:ref('DADOS_INVOC',L(inv['colf'][k])+str(i+2))
        for n,original in enumerate(ficha['lib']+[ficha['tm']]):
            cel=copy.deepcopy(original);maxima=n==len(ficha['lib'])
            cel['dano']=cel.pop('dados' if maxima else 'pontos');cel['mel']=[];cel['res']=[]
            cel.pop('r0');cel.pop('c0')
            requisito=f'AND({source("tipo")}="Maldição domada",{source("n")}>={17 if maxima else [10,20,30][n]})'
            out.append(dict(id=f'entidade.{i+1}.'+('maxima.1' if maxima else 'liberacao.'+str(n+1)),aba='INVOCAÇÕES',cel=cel,
                modo='Máxima de entidade' if maxima else 'Liberação de entidade',nivel=source('n'),classe_maxima=source('cl'),
                dados_zero=source('db'),cd=source('cd'),entidade=i,linha_funcao=original['r0']+5,coluna=original['c0'],requisito=requisito))
    for i,g in enumerate(out):
        g['linha']=i+2;g['editor']=5+i*PASSO
        g['classes']=[0] if g['modo'] in ['Classe 0','Básica'] else [None] if g['modo'] in ['Técnica Máxima','Máxima de entidade'] else list(range(3 if g['modo']=='Liberação de entidade' else 0 if g.get('extra') else 1,8))
        g['campos']={k:g['editor']+2+j for j,(k,_,_) in enumerate(CAMPOS)}
    return out


def aplica(layout,fam,inv,personagem):
    ctx=contextos(fam,inv)
    abas={a['nome']:a for a in layout['abas']}
    if any(n in abas for n in [EDITOR,DADOS,CATALOGO]):raise ValueError('R53 já aplicada')
    cells={n:{v[0]:v for v in a['celulas']} for n,a in abas.items()}
    am=abas['FICHA AMALDIÇOADA']; st=cells[am['nome']]
    styles={'rotulo':st['D52'][2],'entrada':st['D58'][2],'numero':st['E58'][2],
            'secao':st['E51'][2],'texto':st['E66'][2]}
    estilos_cartao=copy.deepcopy(styles)
    for k in ['rotulo','entrada','numero','secao','texto']:
        e=copy.deepcopy(layout['estilos'][styles[k]])
        e[3]=['left' if k in ['rotulo','texto'] else 'center','center',True,0]
        e[0]=['Oswald' if k=='secao' else 'Roboto',14 if k=='secao' else 10,'EEDFEA',k in ['rotulo','secao'],False]
        e[1]='49334F' if k=='secao' else '2F2034' if k=='rotulo' else '1B131F'
        if e not in layout['estilos']:layout['estilos'].append(e)
        styles[k]=layout['estilos'].index(e)
    editor=folha(EDITOR,5+len(ctx)*PASSO,9);editor['congeladas']=3
    editor['colunas_larg']=[[1,1,34],[2,9,20]]
    dados=folha(DADOS,len(ctx)+2,len(M.INPUTS)+len(M.ARVORE)+2,True)
    dados['abaixo']=True
    catalogo=folha(CATALOGO,len(M.CAT['opcoes'])+62,36,True)
    for a in [editor,dados,catalogo]:
        layout['abas'].append(a);abas[a['nome']]=a;cells[a['nome']]={}
    tr=dict(contextos=ctx,antes={},depois={},entradas=[],formulas={},editor_campos=CAMPOS)
    def put(nome,a1,value,style=None):
        old=cells[nome].get(a1)
        if nome not in [EDITOR,DADOS,CATALOGO] and (old[1] if old else None)!=value:
            tr['antes'].setdefault(nome,{}).setdefault(a1,old[1] if old else None)
            tr['depois'].setdefault(nome,{})[a1]=value
        if old is None:
            old=[a1,value,style];cells[nome][a1]=old;abas[nome]['celulas'].append(old)
        else:
            old[1]=value
            if style is not None:old[2]=style
    def box(r,c,value,style='entrada',end=None):
        a=L(c)+str(r);put(EDITOR,a,value,styles[style])
        if end:editor['mescladas'].append(a+':'+end)
    box(1,1,'MONTAGENS · R53','secao','H1')
    box(2,1,'Cada coluna guarda uma versão preparada. Selecione a Classe no cartão para usar a distribuição salva.','texto','H3')
    campos=M.INPUTS+list(M.ARVORE);col={k:L(i+1) for i,k in enumerate(campos)}
    col['identidade_ampliacao']=L(len(campos)+1)
    col['avisos_funcoes']=L(len(campos)+2)
    tr['colunas']=col
    for i,k in enumerate(campos,1):put(DADOS,L(i)+'1',k)
    put(DADOS,col['identidade_ampliacao']+'1','identidade_ampliacao')
    put(DADOS,col['avisos_funcoes']+'1','avisos_funcoes')
    tr['gid_editor']=f'B{len(ctx)+2}'
    put(DADOS,f'A{len(ctx)+2}','r53.editor.gid')
    put(DADOS,tr['gid_editor'],0)
    for i,k in enumerate(M.LOOKUP_FIELDS,1):put(CATALOGO,L(i)+'1',k)
    for r,p in enumerate(M.CAT['opcoes'],2):
        for c,k in enumerate(M.LOOKUP_FIELDS,1):put(CATALOGO,L(c)+str(r),p[k])
    # Cadastros próprios usam as tabelas B47 já validadas. BASE conserva
    # identidade/limites do livro; texto livre não vira automação nova.
    livro_fim=len(M.CAT['opcoes'])+1
    lookup_livro=ref(CATALOGO,f'$A$2:$O${livro_fim}')
    criterio=lambda e:'SUBSTITUTE(SUBSTITUTE(SUBSTITUTE('+e+',"~","~~"),"*","~*"),"?","~?")'
    lookup=lambda e,k,default:f'IFERROR(VLOOKUP({criterio(e)},{lookup_livro},{M.LOOKUP_FIELDS.index(k)+1},FALSE),{default})'
    custom_opcoes=[]
    for tipo,owner,name_col,base_col,weight_col,req_col in [
        ('melhorias','DADOS_MELHORIAS','O','X','Q','W'),
        ('restricoes','DADOS_RESTRICOES','M','N','O','P')]:
        nbook=sum(v['tipo']==tipo for v in M.CAT['opcoes'])
        for n in range(1,31):
            rowcat=livro_fim+len(custom_opcoes)+1;rr=nbook+n+1
            nome=ref(owner,name_col+str(rr));base=ref(owner,'E'+str(n+1))
            values=dict(rotulo=nome,nome=lookup(base,'nome','"Efeito Próprio"' if tipo=='melhorias' else json.dumps('custom.restricao.'+str(n))),
                tipo=json.dumps(tipo),familia=ref(owner,'P'+str(rr)) if tipo=='melhorias' else '""',
                peso=ref(owner,weight_col+str(rr)),degraus=lookup(base,'degraus','0'),repeticoes=lookup(base,'repeticoes','1'),
                classe_minima=lookup(base,'classe_minima','0'),tr=ref(owner,req_col+str(rr)) if tipo=='melhorias' else '0',
                frequencia=ref(owner,req_col+str(rr)) if tipo=='restricoes' else '0',id=json.dumps('custom.'+tipo+'.'+str(n)),
                proprio='1',cadastro_valido='1',rotulo_base=lookup(base,'rotulo_base',json.dumps('custom.'+tipo+'.'+str(n))),
                controle_compat=f'IF({ref(owner,"N"+str(n+1))}=TRUE,1,'+lookup(base,'controle_compat','0')+')' if tipo=='melhorias' else '0')
            for c,k in enumerate(M.LOOKUP_FIELDS,1):
                blank='""' if k in ['rotulo','nome','tipo','familia','id','rotulo_base'] else '0'
                put(CATALOGO,L(c)+str(rowcat),f'=IF({nome}="",{blank},{values[k]})')
            custom_opcoes.append(dict(tipo=tipo,row=rowcat))
    lookup_fim=livro_fim+len(custom_opcoes)
    tr['lookup_range']=ref(CATALOGO,f'$A$2:$O${lookup_fim}')
    # Listas auxiliares P:R, separadas dos metadados A:N.
    for c,tipo in [(16,'melhorias'),(17,'restricoes')]:
        valores=[p['rotulo'] for p in M.CAT['opcoes'] if p['tipo']==tipo]
        for r,v in enumerate(valores,2):put(CATALOGO,L(c)+str(r),v)
        for r,extra in enumerate([p for p in custom_opcoes if p['tipo']==tipo],len(valores)+2):
            put(CATALOGO,L(c)+str(r),'=A'+str(extra['row']))
        tr[tipo+'_menu']=ref(CATALOGO,f'${L(c)}$2:${L(c)}${len(valores)+31}')
    for r,v in enumerate(M.FORMAS,2):put(CATALOGO,'R'+str(r),v)
    import formas_custom
    tr['formas_range'],formas_rows=formas_custom.aplicar(personagem,lambda a,v:put(CATALOGO,a,v),catalogo,ref)
    for r,rr in enumerate(formas_rows,len(M.FORMAS)+2):put(CATALOGO,'R'+str(r),'=AL'+str(rr))
    # Estado das Famílias para cada contexto. Família própria desconhecida
    # fica Fechada; uma entidade usa suas nove escolhas, não a lista pessoal.
    put(CATALOGO,'W1','Família');put(CATALOGO,'X1','Personagem')
    for i in range(12):put(CATALOGO,L(25+i)+'1','Entidade '+str(i+1))
    for r in range(2,21):
        nome=ref('DADOS_CRIACAO','H'+str(r))
        put(CATALOGO,'W'+str(r),'='+nome)
        put(CATALOGO,'X'+str(r),f'=IF({nome}="","Fechada",'+ref('DADOS_CRIACAO','I'+str(r))+')')
        for i in range(12):
            fields=inv['colf'];own=[ref('DADOS_INVOC',L(fields['f'+str(j)])+str(i+2)) for j in range(9)]
            freecol=next(coordinate_to_tuple(a)[1] for a,v in cells['DADOS_INVOC'].items() if v[1]=='Família Livre efetiva 1')
            livres=[ref('DADOS_INVOC',L(freecol+j)+str(i+2)) for j in range(9)]
            test=lambda xs:'OR('+','.join(f'{rr}={nome}' for rr in xs)+')'
            put(CATALOGO,L(25+i)+str(r),f'=IF({nome}="","Fechada",IF({test(livres)},"Livre",IF({test(own)},"Normal","Fechada")))')
    tr['familias_range']=ref(CATALOGO,'$W$2:$AJ$20')
    menus={'forma':ref(CATALOGO,'$R$2:$R$'+str(len(M.FORMAS)+len(formas_rows)+1)),'melhoria':tr['melhorias_menu'],'restricao':tr['restricoes_menu'],
           'controle':'"Sem reforço,Dano limitado à Classe,Sem dano"',
           'funcao':'"Dano,Cura,PV temporários"',
           'tr':'"Físico,Vigor,Intelecto,Espírito"','resolucao':'"Ataque,TR,Automático"','execucao':'"Comandada,Resposta autônoma"',
           'migracao':'"Revisão necessária,Revisado"'}
    tr['menus_editor']=menus
    for g in ctx:
        row=g['linha'];start=g['editor'];ncol=len(g['classes']);cel=g['cel'];aba=g['aba']
        nome=ref(aba,cel['nome']);classes=g['classes']
        box(start,1,'='+json.dumps(g['id']+' · ',ensure_ascii=False)+'&'+nome,'secao','H'+str(start))
        box(start+1,1,'Classe preparada','rotulo')
        for j,c in enumerate(classes,2):
            letra=L(j);header=letra+str(start+1)
            box(start+1,j,('='+g['classe_maxima']) if c is None else c,'rotulo')
            for key,label,kind in CAMPOS:
                r=g['campos'][key];value=DEFAULTS_EDITOR[key]
                box(r,j,value,'texto' if kind=='texto' else 'entrada')
                if kind=='bool':editor['menus'].append(dict(onde=letra+str(r),tipo='bool',formula='',vazio_ok=True,mostra_seta=False))
                elif kind in menus:
                    editor['menus'].append(dict(onde=letra+str(r),tipo='list',formula=menus[kind],vazio_ok=True,mostra_seta=True,estrito=True))
                elif kind=='inteiro':
                    editor['menus'].append(dict(onde=letra+str(r),tipo='custom',formula=f'AND(ISNUMBER({letra}{r}),{letra}{r}>=0,INT({letra}{r})={letra}{r})',vazio_ok=False,mostra_seta=False))
                tr['entradas'].append((f'r53.{g["id"]}.classe.{c if c is not None else "maxima"}.{key}',letra+str(r),kind))
            # Editor de versão guarda dados literais, não referências à versão atual.
        for key,label,kind in CAMPOS:box(g['campos'][key],1,label,'rotulo')
        if len(classes)>1:editor['grupos']['linhas'].append([start+1,start+len(CAMPOS)+2,True])
        selected='0' if classes==[0] else g['classe_maxima'] if classes==[None] else ref(aba,cel['classe'])
        index='1' if ncol==1 else f'MATCH({selected},{ref(EDITOR,"$B$"+str(start+1)+":$"+L(1+ncol)+"$"+str(start+1))},0)'
        raw=dict(id=g['id'],nome='='+nome,classe='='+selected,modalidade=g['modo'],nivel='='+g['nivel'],
                 classe_maxima='='+g['classe_maxima'],dados_zero='='+g['dados_zero'],cd='='+g['cd'])
        for key,_,_ in CAMPOS:
            r=g['campos'][key];faixa=ref(EDITOR,f'$B${r}:${L(1+ncol)}${r}')
            default=DEFAULTS_EDITOR[key];lit='FALSE' if default is False else 'TRUE' if default is True else str(default) if isinstance(default,(int,float)) else json.dumps(default,ensure_ascii=False)
            raw[key]=f'=IFERROR(INDEX({faixa},1,{index}),{lit})'
        raw.update(funcoes_selecionadas(g['campos'],index,ncol))
        # Família/rota continuam calculadas nas tabelas existentes; autorizações
        # individuais da Regra vêm dos campos explícitos da versão.
        # Uma tabela calcula cada estado uma só vez. A referência depende do
        # ID da linha, permitindo copiar as contas entre contextos no Sheets.
        familia_coluna=f'IFERROR(VALUE(REGEXEXTRACT(A{row},"^entidade[.]([0-9]+)[.]"))+2,2)'
        for famnome in M.FAMILIAS:
            raw['fam_'+famnome]=f'=IFERROR(VLOOKUP("{famnome}",{tr["familias_range"]},{familia_coluna},FALSE),"Fechada")'
        if g.get('extra'):raw['modalidade']=f'=IF({selected}=0,"Básica","Entidade")'
        for k in M.INPUTS:put(DADOS,col[k]+str(row),raw.get(k,M.DEFAULTS[k]))
        ff=M.formulas(row,col,tr['lookup_range'],familias_range=tr['familias_range'],familias_coluna=familia_coluna,formas_range=tr['formas_range'])
        invariantes=[k for k,_,_ in CAMPOS if k not in {'preparada','pontos1','pontos2','pontos3','fragil_pago','migracao'}]
        prep=ref(EDITOR,f'$B${g["campos"]["preparada"]}:${L(1+ncol)}${g["campos"]["preparada"]}')
        mensagens=[]
        for k in invariantes:
            r=g['campos'][k];faixa=ref(EDITOR,f'$B${r}:${L(1+ncol)}${r}')
            teste=f'SUMPRODUCT(({prep}=TRUE)*({faixa}<>INDEX({faixa},1,MATCH(TRUE,{prep},0))))>0'
            mensagens.append(f'IF({teste},"{k}","")')
        identidade='=IFERROR(TEXTJOIN(" · ",TRUE,'+','.join(mensagens)+'),"")' if ncol>1 else '=""'
        put(DADOS,col['identidade_ampliacao']+str(row),identidade)
        aviso=avisos_funcoes(g['campos'],index,ncol)
        if g.get('requisito'):aviso='TEXTJOIN(" · ",TRUE,'+aviso+',IF('+g['requisito']+',"","Trunfo exige maldição domada com técnica própria e nível de aquisição"))'
        put(DADOS,col['avisos_funcoes']+str(row),'='+aviso)
        for k,v in ff.items():
            if k=='avisos':
                extra=col['identidade_ampliacao']+str(row)
                v='=TEXTJOIN(" · ",TRUE,'+v[1:]+','+col['avisos_funcoes']+str(row)+',IF('+extra+'<>"","Ampliação altera funções/peças/requisitos: "&'+extra+',""))'
            guarded=f'=IF({col["nome"]}{row}="",'+('FALSE' if k=='valida' else '""')+','+v[1:]+')'
            put(DADOS,col[k]+str(row),guarded)
        saida=lambda k:ref(DADOS,'$'+col[k]+'$'+str(row))
        # Saldo da Classe em uso: a soma reservada reduz imediatamente a sobra.
        for off,label in [(len(CAMPOS)+2,'Saldo após custos'),(len(CAMPOS)+3,'Restam para distribuir')]:
            box(start+off,1,label,'rotulo')
            for j in range(2,ncol+2):
                letra=L(j);header=letra+str(start+1)
                allocated='+'.join(letra+str(g['campos']['pontos'+str(i)]) for i in range(1,4))
                remainder=f'{saida("saldo")}-({allocated})'
                value=saida('saldo') if off==len(CAMPOS)+2 else f'IF({remainder}<0,"Excede "&ABS({remainder})&IF(ABS({remainder})=1," ponto"," pontos"),{remainder})'
                box(start+off,j,f'=IF(AND({nome}<>"",{selected}={header}),{value},"")')
        for i in range(1,4):
            editor['notas']['A'+str(g['campos']['funcao'+str(i)])]='Escolha na lista. Dano e Cura: 1 ponto = 1d8; PV temporários: 1 ponto = 3 PV. As outras funções vêm das Melhorias. Cada função variável ocupa uma linha; não repita a mesma opção.'
        if len(classes)>1:editor['grupos']['linhas'][-1][1]=start+len(CAMPOS)+3

        tr['formulas'][g['id']]={}
        def card(key,value):
            if key not in cel:return
            put(aba,cel[key],value)
            tr['formulas'][g['id']][cel[key]]=value
        active=f'{saida("nome")}<>""'
        card('forma','='+saida('forma'))
        for key,n in [('mel',4),('res',2)]:
            for j,a1 in enumerate(cel.get(key,[])):
                value='='+saida(('m' if key=='mel' else 'r')+str(j+1))
                put(aba,a1,value);tr['formulas'][g['id']][a1]=value
        card('pe',f'=IF({active},{saida("pe")}&" PE","")')
        card('dano',f'=IF({active},IF({saida("dano")},{saida("dano_resultado")},IF({saida("cura")},{saida("cura_d8")}&"d8 cura",IF({saida("vt")},{saida("vida_temporaria")}&" VT","Efeitos"))),"")')
        card('acao',f'=IF({active},{saida("acao")},"")')
        card('resolve',f'=IF({active},{saida("resolucao_dano")}&IF({saida("bonus_controle")}>0," · Controle CD "&{saida("cd_controle")},""),"")')
        card('alcance',f'=IF({active},TEXTJOIN(" · ",TRUE,{saida("alcance_ofensivo")},{saida("area")}),"")')
        card('conta',f'=IF({active},{saida("orcamento")}&" − base "&{saida("base_funcoes")}&" − Forma "&{saida("custo_forma")}&" − peças "&{saida("melhorias_pagas")}&" + devolução "&{saida("devolucao")}&" = "&{saida("saldo")}&" pontos","")')
        card('avisos',f'=IF({active},TEXTJOIN(" · ",TRUE,{saida("avisos")},{saida("efeitos")},IF({saida("dano")},"Dano: "&{saida("dest_dano")},""),IF({saida("cura")},"Cura: "&{saida("dest_cura")},""),IF({saida("vt")},"PV temporários: "&{saida("dest_vt")},""),{saida("dependencias")}),"")')
        card('estado',f'=IF({active},IF({saida("valida")},"VÁLIDO","REVISAR"),"")')
        gid=ref(DADOS,'$B$'+str(len(ctx)+2))
        card('ampliar',f'=IF({active},IF({gid}>0,HYPERLINK("#gid="&{gid}&"&range=A{start}","Editar funções e pontos ↗"),"Editar funções e pontos · MONTAGENS, linha {start}"),"")')
        for key,prefix in [('preco','pago_m'),('dev','retorno_r')]:
            for j,a1 in enumerate(cel.get(key,[])):
                piece=saida(('m' if key=='preco' else 'r')+str(j+1))
                value=f'=IF(AND({active},{piece}<>""),{saida(prefix+str(j+1))},"")'
                put(aba,a1,value);tr['formulas'][g['id']][a1]=value
        if 'linha_funcao' in g:
            r,c=g['linha_funcao'],g['coluna'];a1=L(c)+str(r)
            # Recortar somente a última linha da descrição; âncora e texto preservados.
            a=abas[aba];desc=cel['como'];merged=next((v for v in a['mescladas'] if v.startswith(desc+':')),None)
            if not merged:raise ValueError('Descrição sem mesclagem: '+aba+'!'+desc)
            first,end=merged.split(':');er,ec=coordinate_to_tuple(end)
            if er!=r:raise ValueError('Geometria da descrição mudou: '+merged)
            a['mescladas'][a['mescladas'].index(merged)]=first+':'+L(ec)+str(r-1)
            put(aba,a1,'Função',estilos_cartao['rotulo'])
            value=f'=IF({active},{saida("funcao")},"")';dst=L(c+1)+str(r)
            put(aba,dst,value,estilos_cartao['texto']);a['mescladas'].append(dst+':'+L(ec)+str(r))
            tr['formulas'][g['id']][dst]=value;g['funcao']=dst
            a['linhas_alt'].append([r,42])
            a.setdefault('notas',{})[dst]='Resumo calculado automaticamente. Use Editar funções e pontos para escolher Dano, Cura e PV temporários e distribuir pontos. O cartão mostra a versão da Classe selecionada.'
            for group in a.get('grupos',{}).get('linhas',[]):
                if group[1]==r and group[0]>=coordinate_to_tuple(desc)[0]-1:group[1]=r-1
        else:
            # Classe 0 compacta e TM já têm resultado dedicado.
            g['funcao']=cel['dano']
            card('dano',f'=IF({active},"Função: "&{saida("funcao")},"")')
        a=abas[aba];a.setdefault('notas',{})[cel['nome']]=f'R53: edite as versões em MONTAGENS, linha {start}. Cada Classe mantém a própria distribuição. Nome e Classe continuam neste cartão.'
        # Remover validações antigas dos campos que agora apresentam a versão salva.
        computed=set(tr['formulas'][g['id']]);menus_orig=[]
        for menu in a['menus']:
            # Desdobrar listas de âncoras e faixas de Melhorias/Restrições.
            locais=[]
            for token in menu['onde'].split():
                if ':' not in token:
                    if token not in computed:locais.append(token)
                else:
                    lft,rgt=token.split(':');r1,c1=coordinate_to_tuple(lft);r2,c2=coordinate_to_tuple(rgt)
                    if c1==c2:
                        locais.extend(L(c1)+str(rr) for rr in range(r1,r2+1) if L(c1)+str(rr) not in computed)
                    else:locais.append(token)
            if locais:
                novo=copy.deepcopy(menu);novo['onde']=' '.join(locais);menus_orig.append(novo)
        a['menus']=menus_orig
    tr['abas']=[EDITOR,DADOS,CATALOGO]
    return tr


def exporta(tr):
    """Contrato novo separado das chaves históricas; valores continuam textuais."""
    out=[['r53.montagem.esquema','2','','cabeçalho'],['r53.entrada.campos',json.dumps(M.INPUTS,ensure_ascii=False),'','cabeçalho']]
    for g in tr['contextos']:
        prefix='r53.'+g['id'];row=g['linha'];cols=tr['colunas']
        for key in ['classe','modalidade','forma','dano','cura','vt','p_dano','p_cura','p_vt','controle',
                    'dest_dano','dest_cura','dest_vt','res_dano','tr_dano','tr_controle','dependencias','execucao','origem_permissao',
                    'orcamento','base_funcoes','custo_forma','melhorias_pagas','devolucao','saldo','dano_d8','cura_d8',
                    'vida_temporaria','sem_uso','pe','cd_normal','cd_controle','funcao','avisos']:
            a1=ref(DADOS,cols[key]+str(row));out.append([prefix+'.'+key,f'={a1}&""',a1,'aviso' if key=='avisos' else 'entrada' if key in M.INPUTS else 'resultado'])
        faixa=ref(DADOS,'A'+str(row)+':'+L(len(M.INPUTS))+str(row))
        value=f'=IF({ref(DADOS,cols["nome"]+str(row))}<>"",'+json_faixa(faixa)+',"")'
        out.append([prefix+'.entrada',value,faixa,'entrada'])
    return out


def json_numero(a1):
    # TO_TEXT herda formatos como "Classe "0 da célula referenciada.
    # JSON precisa do número bruto, independentemente da paleta/formatação.
    return f'IF({a1}=INT({a1}),TEXT({a1},"0"),SUBSTITUTE(TEXT({a1},"0.###############"),",","."))'


def json_celula(a1,kind):
    """Serialização JSON nativa, inclusive aspas, barras e quebras de linha."""
    if kind=='bool':return f'IF({a1},"true","false")'
    if kind=='inteiro':return f'IF(ISNUMBER({a1}),{json_numero(a1)},"null")'
    t=a1+'&""'
    for char,after in [(92,'CHAR(92)&CHAR(92)'),(34,'CHAR(92)&CHAR(34)'),(10,'CHAR(92)&"n"'),(13,'CHAR(92)&"r"'),(9,'CHAR(92)&"t"')]:
        t=f'SUBSTITUTE({t},CHAR({char}),{after})'
    return 'CHAR(34)&'+t+'&CHAR(34)'


def json_faixa(faixa):
    quoted=json_celula('item','texto')
    item=f'IF(ISLOGICAL(item),IF(item,"true","false"),IF(ISNUMBER(item),{json_numero("item")},{quoted}))'
    return f'"["&TEXTJOIN(",",FALSE,MAP({faixa},LAMBDA(item,{item})))&"]"'


def exporta_versoes(tr):
    # Um array tipado e o esquema compartilhado preservam todos os campos,
    # sem repetir 31 nomes de chave em cada uma das Classes de cada cartão.
    out=[['r53.versao.campos',json.dumps(['classe']+[k for k,_,_ in CAMPOS],ensure_ascii=False),'','cabeçalho']]
    quoted=json_celula('item','texto')
    item=f'IF(ISLOGICAL(item),IF(item,"true","false"),IF(ISNUMBER(item),{json_numero("item")},{quoted}))'
    for g in tr['contextos']:
        for c,classe in enumerate(g['classes'],2):
            header=ref(EDITOR,L(c)+str(g['editor']+1))
            faixa=ref(EDITOR,L(c)+str(g['campos'][CAMPOS[0][0]])+':'+L(c)+str(g['campos'][CAMPOS[-1][0]]))
            preparada=ref(EDITOR,L(c)+str(g['campos']['preparada']))
            value=f'=IF({preparada},"["&{json_numero(header)}&","&TEXTJOIN(",",FALSE,MAP({faixa},LAMBDA(item,{item})))&"]","")'
            out.append([f'r53.{g["id"]}.versao.{classe if classe is not None else "maxima"}',value,header,'entrada'])
    return out


def finaliza(tr):
    """Acompanha a transformação final, sem deslocar o editor de versões."""
    import extensoes_custom as ex
    def celulas(value,owner):
        if isinstance(value,str) and re.fullmatch(r'[A-Z]+\d+',value):return ex.coord(owner,value)
        if isinstance(value,list):return [celulas(v,owner) for v in value]
        if isinstance(value,dict):return {k:celulas(v,owner) for k,v in value.items()}
        return value
    for g in tr['contextos']:
        g['cel']=celulas(g['cel'],g['aba'])
        g['funcao']=ex.coord(g['aba'],g['funcao'])
        if 'linha_funcao' in g:g['linha_funcao']=ex.linha(g['aba'],g['linha_funcao'])
        tr['formulas'][g['id']]={ex.coord(g['aba'],a):ex.formula(v,g['aba']) for a,v in tr['formulas'][g['id']].items()}
    for key in ['antes','depois']:
        tr[key]={aba:{ex.coord(aba,a1):ex.formula(v,aba) for a1,v in reg.items()} for aba,reg in tr[key].items()}
    tr['apresentacao_final']=True
    return tr
