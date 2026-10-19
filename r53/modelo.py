"""Montagem R53: entradas, resultados e validações sem ler prosa livre.

As fórmulas e o avaliador de diagnóstico usam a mesma árvore. Catálogo vem dos
IDs da publicação; permissões da Regra/definição são escolhas explícitas.
"""
import json
from pathlib import Path
from formulas import X,x,ref,f,IF,AND,OR,SUM,MIN,MAX,UP,INT,JOIN,LOOK,FAMILY,FORM,evaluate,native

RAIZ=Path(__file__).resolve().parents[1]
CAT=json.loads((RAIZ/'r53/catalogo.json').read_text())
OPCOES={v['rotulo']:v for v in CAT['opcoes']}
FAMILIAS=['Alcance','Controle','Auxiliares','Marca','Castigo','Amparo','Área','Mira','Tempo']
TRS=['Físico','Vigor','Intelecto','Espírito']
FORMAS=['Projétil','Toque','Explosão','Aura','Cone','Linha']
LOOKUP_FIELDS=['rotulo','nome','tipo','familia','peso','degraus','repeticoes','classe_minima','tr','frequencia','id','proprio','cadastro_valido','controle_compat','rotulo_base']
INPUTS=['id','nome','classe','modalidade','nivel','preparada','forma','dano','cura','vt','p_dano','p_cura','p_vt',
        'pessoal','controle','m1','m2','m3','m4','r1','r2','permite_dano','permite_cura','permite_vt','permite_alma',
        'dest_dano','dest_cura','dest_vt','res_dano','dependencias','execucao','r1_valida','r2_valida','fragil_pago','cd',
        'origem_permissao','migracao','classe_maxima','dados_zero']+['fam_'+n for n in FAMILIAS]+['tr_dano','tr_controle']
DEFAULTS=dict(id='',nome='',classe=1,modalidade='Comum',nivel=1,preparada=False,forma='Projétil',
              tr_dano='',tr_controle='',dano=False,cura=False,vt=False,p_dano=0,p_cura=0,p_vt=0,pessoal=False,controle='Sem reforço',
              permite_dano=False,permite_cura=False,permite_vt=False,permite_alma=False,
              dest_dano='',dest_cura='',dest_vt='',res_dano='Ataque',dependencias='',execucao='Comandada',
              r1_valida=False,r2_valida=False,fragil_pago=0,cd=0,origem_permissao='',migracao='',classe_maxima=7,dados_zero=2,
              **{k:'' for k in ['m1','m2','m3','m4','r1','r2']},**{'fam_'+n:'Normal' for n in FAMILIAS})


def arvore(registro_livre=False):
    out={}
    def add(k,e): out[k]=x(e);return ref(k)
    c=ref('classe'); modo=ref('modalidade'); nivel=ref('nivel'); rawforma=ref('forma')
    publicada=OR(*[rawforma.eq(n) for n in FORMAS]);propria=FORM(rawforma,'rotulo').ne('')
    forma=add('forma_base',IF(publicada,rawforma,FORM(rawforma,'base')))
    entidade=add('entidade',OR(*[modo.eq(n) for n in ['Entidade','Básica','Liberação de entidade','Máxima de entidade']]))
    zero=add('zero',OR(modo.eq('Classe 0'),modo.eq('Básica'),AND(entidade,c.eq(0))))
    tm=add('tm',OR(modo.eq('Técnica Máxima'),modo.eq('Máxima de entidade')));lib=add('lib',OR(modo.eq('Liberação Máxima'),modo.eq('Liberação de entidade')))
    dados_maxima=IF(entidade,IF(nivel.ge(26),26,IF(nivel.ge(21),22,19)),IF(nivel.ge(26),32,IF(nivel.ge(21),28,24)))
    comum=add('comum',AND(zero.eq(False),tm.eq(False),lib.eq(False)))
    area=add('coletiva',OR(*[forma.eq(n) for n in FORMAS[2:]],FORM(rawforma,'coletiva')))
    l=add('leve',UP(c/2));m=add('media',c);p=add('pesada',UP(c*1.5))
    desc=add('desconto_livre',IF(entidade,MAX(1,INT(c/2)),UP(c/2)))
    maxmel=add('limite_melhorias',IF(zero,1,IF(tm,4,IF(c.le(2),2,IF(c.le(4),3,4)))))
    maxres=add('limite_restricoes',IF(tm,0,IF(zero,1,2)))
    orc=add('orcamento',IF(zero,ref('dados_zero'),IF(tm,IF(nivel.ge(26),16,IF(nivel.ge(21),12,8)),
                IF(entidade,IF(c.eq(1),2,IF(c.eq(2),4,IF(c.eq(3),6,IF(c.eq(4),9,IF(c.eq(5),11,IF(c.eq(6),13,16)))))),3*c))))
    contagens={}
    def conta(tipo,nome,n):
        key=(tipo,nome)
        if key not in contagens:
            contagens[key]=add('contagem_'+str(len(contagens)+1),SUM([IF(ref('nome_'+tipo+str(i)).eq(nome),1,0) for i in range(1,n+1)]))
        return contagens[key]
    def npeca(nome): return conta('m',nome,4)
    def nres(nome): return conta('r',nome,2)
    def peso(v): return IF(v.eq(1),l,IF(v.eq(2),m,IF(v.eq(3),p,0)))
    def estado(fam): return IF(FAMILY(fam).eq('Fechada'),1,0)
    def livre(fam): return IF(FAMILY(fam).eq('Livre'),1,0)
    for tipo,n in [('m',4),('r',2)]:
        for i in range(1,n+1):
            entrada=ref(tipo+str(i));fam=add('familia_'+tipo+str(i),LOOK(entrada,'familia'))
            add('nome_'+tipo+str(i),LOOK(entrada,'nome'))
            w=add('peso_'+tipo+str(i),LOOK(entrada,'peso'))
            add('fechada_'+tipo+str(i),estado(fam))
            if tipo=='m':
                add('pago_'+tipo+str(i),IF(entrada.eq(''),0,IF(zero,1,MAX(1,peso(w)-IF(livre(fam).gt(0),desc,0)))))
            else:
                qr=ref('nome_'+tipo+str(i)).eq('Queima-Roupa')
                valido=ref(tipo+str(i)+'_valida')
                valor=IF(qr,IF(forma.eq('Projétil'),m,l),peso(w))
                # Exigências já obrigatórias não financiam a própria montagem.
                bloqueada=OR(tm,AND(lib,OR(ref('nome_'+tipo+str(i)).eq('Atrasar'),ref('nome_'+tipo+str(i)).eq('Parado'))))
                valor=IF(ref('nome_'+tipo+str(i)).eq('Frágil'),MIN(l,MAX(0,ref('fragil_pago'))),valor)
                add('retorno_'+tipo+str(i),IF(OR(entrada.eq(''),valido.eq(False),bloqueada),0,IF(zero,1,valor)))
    qtdm=add('quantidade_melhorias',SUM([IF(ref('m'+str(i)).ne(''),1,0) for i in range(1,5)]))
    qtdr=add('quantidade_restricoes',SUM([IF(ref('r'+str(i)).ne(''),1,0) for i in range(1,3)]))
    aux=OR(npeca('Guarda').gt(0),npeca('Impulso').gt(0),npeca('Firmeza').gt(0))
    base=add('base_funcoes',IF(zero,0,IF(OR(ref('cura'),AND(area,OR(ref('vt'),aux))),m,IF(ref('vt'),l,0))))
    cf=add('custo_forma',IF(zero,0,IF(propria,peso(FORM(rawforma,'peso')),IF(forma.eq('Explosão'),m,IF(OR(forma.eq('Aura'),forma.eq('Cone'),forma.eq('Linha')),l,0)))))
    pago=add('melhorias_pagas',SUM([ref('pago_m'+str(i)) for i in range(1,5)]))
    toque=add('retorno_toque',IF(AND(forma.eq('Toque'),zero.eq(False),tm.eq(False),ref('pessoal').eq(False)),l,0))
    devolucao=add('devolucao',MIN(SUM([ref('retorno_r1'),ref('retorno_r2'),toque]),pago,IF(zero,1,2*c)))
    saldo=add('saldo',orc-base-cf-pago+devolucao)
    semdano=add('controle_sem_dano',AND(comum,ref('controle').eq('Sem dano')))
    limdano=add('controle_limitado',AND(comum,ref('controle').eq('Dano limitado à Classe')))
    efeitosctrl=OR(npeca('Condição').gt(0),npeca('Prende').gt(0),npeca('Cerca').gt(0),*[AND(LOOK(ref('m'+str(i)),'controle_compat').gt(0),LOOK(ref('m'+str(i)),'tr').gt(0)) for i in range(1,5)])
    ctrl=OR(*[ref('familia_m'+str(i)).eq('Controle') for i in range(1,5)])
    pc=add('cura_efetiva_pontos',IF(OR(semdano,zero,ref('cura').eq(False)),0,
            IF(tm,dados_maxima,MAX(0,MIN(ref('p_cura'),IF(area,MAX(0,orc-p),IF(entidade,MAX(0,orc-m),2*c)))))))
    pv=add('vt_efetiva_pontos',IF(OR(semdano,zero,tm,ref('vt').eq(False)),0,MAX(0,MIN(ref('p_vt'),IF(area,MAX(0,orc-p),IF(entidade,MAX(0,orc-l),MAX(0,saldo)))))))
    dp=add('dano_inicial',IF(OR(semdano,ref('dano').eq(False)),0,IF(zero,MAX(0,saldo),IF(tm,
            dados_maxima,MAX(0,MIN(ref('p_dano'),IF(limdano,c,4*c)))+IF(lib,c,0)))))
    # Teto global inclui cada secundário uma vez, nunca multiplicado por criaturas na área.
    # O fator de Remate só aumenta o dano inicial. A busca é limitada a no máximo 28d8 comuns.
    candidates=[]
    for n in range(0,29):
        total=n*IF(npeca('Remate').gt(0),1.25,1)*IF(npeca('Quebra Coisa').gt(0),2,1)+int(n/2)*(npeca('Salto')+npeca('Queima')+npeca('Estilhaço'))
        candidates.append(IF(AND(x(n).le(dp),total.le(4*c)),n,0))
    dc=add('dano_teto',IF(OR(zero,tm),dp,MAX(*candidates)))
    dano=add('dano_d8',IF(npeca('Toca a Alma').gt(0),INT(dc/2),dc))
    dado=add('dado_dano',IF(AND(entidade,zero),'d6','d8'))
    add('dano_resultado',dano.cat(dado))
    cura=add('cura_d8',pc)
    vt=add('vida_temporaria',3*pv)
    sobra=add('sem_uso',IF(OR(semdano,tm),MAX(0,saldo),MAX(0,saldo-IF(zero,IF(ref('dano'),saldo,0),MAX(0,dc-IF(lib,c,0)))-pc-pv)))
    pe=add('pe',IF(zero,0,IF(tm,5*c,IF(lib,UP(4.5*c),3*c)))+IF(nres('Sobrecusto').gt(0),2*c,0))
    bonus=add('bonus_controle',IF(AND(semdano,efeitosctrl),2,0))
    precisao=add('bonus_precisao',IF(npeca('Precisão').gt(0),2,0))
    cdnormal=add('cd_normal',ref('cd')+precisao)
    add('cd_controle',cdnormal+bonus)
    reduzida=add('classe_efeito',IF(AND(entidade,zero.eq(False)),MAX(1,c-1),c))
    add('beneficiarios_fixos',IF(area,c+1,1+npeca('Mais Um')))
    add('tiros',IF(npeca('Rajada').gt(0),MIN(dano,IF(entidade,reduzida,c)+1),1))
    add('fura_rd',IF(npeca('Fura').gt(0),2*IF(entidade,reduzida,c),0))
    add('anteparo_pv',IF(npeca('Anteparo').gt(0),10*IF(entidade,reduzida,c),0))
    longe=add('degraus_alcance',SUM([IF(ref('nome_m'+str(i)).eq('Longe'),LOOK(ref('m'+str(i)),'degraus'),0) for i in range(1,5)]))
    maior=add('degraus_area',SUM([IF(ref('nome_m'+str(i)).eq('Maior'),LOOK(ref('m'+str(i)),'degraus'),0) for i in range(1,5)]))
    qr=add('queima_roupa',nres('Queima-Roupa').gt(0))
    def degrau(indice, valores):
        result=x(valores[-1])
        for i in reversed(range(len(valores)-1)): result=IF(indice.le(i),valores[i],result)
        return result
    distancia=['1,5 m','9 m','18 m','36 m','90 m','visão a olho nu']
    origem=add('alcance_ofensivo',IF(forma.eq('Toque'),'1,5 m',IF(forma.eq('Aura'),'Em quem executa',
            IF(qr,IF(forma.eq('Projétil'),'1,5 m','Em quem executa'),degrau(IF(zero,1,IF(c.ge(6),3,2))+longe,distancia)))))
    add('alcance_beneficio',IF(forma.eq('Projétil'),IF(qr,'1,5 m',IF(AND(zero,longe.eq(0)),'4,5 m',
        degrau(IF(zero,0,IF(c.ge(6),2,1))+longe,distancia))),origem))
    classe_area=IF(entidade,reduzida,c)
    raio=degrau(IF(classe_area.ge(6),1,0)+maior,['3 m','4,5 m','6 m','9 m','15 m'])
    cone=IF(AND(zero,maior.eq(0)),'3 m',degrau(IF(zero,maior-1,IF(classe_area.ge(6),1,0)+maior),['4,5 m','9 m','18 m','30 m','60 m']))
    linha=degrau(IF(zero,0,IF(classe_area.ge(6),2,1))+maior,['9 × 1,5 m','18 × 1,5 m','30 × 1,5 m','60 × 1,5 m','60 × 3 m','60 × 4,5 m'])
    add('area',IF(OR(forma.eq('Explosão'),forma.eq('Aura')),x('Raio ').cat(raio),IF(forma.eq('Cone'),x('Cone ').cat(cone),IF(forma.eq('Linha'),x('Linha ').cat(linha),''))))
    # Formas próprias conservam os dois componentes e suas escadas já validadas.
    from formas_custom import CAMPOS as FORMA_CAMPOS
    faixa=IF(entidade,IF(zero,3,IF(c.le(5),4,IF(c.eq(6),5,6))),IF(zero,0,IF(c.le(5),1,2)))
    def medida(d,grau):
        offset=12*faixa+MIN(5,grau)
        return IF(FORM(rawforma,'p1_dimensao').eq(d),FORM(rawforma,'medida_0',offset),IF(FORM(rawforma,'p2_dimensao').eq(d),FORM(rawforma,'medida_0',offset+6),''))
    for k in ['alcance_ofensivo','alcance_beneficio']:
        out[k]=IF(AND(propria,forma.ne('Toque'),forma.ne('Aura'),qr.eq(False)),medida('alcance',longe),out[k])
    out['area']=IF(propria,medida('area',maior),out['area'])
    add('resolucao_dano',IF(npeca('Inescapável').gt(0),'Automático (sem crítico)',IF(ref('res_dano').eq('TR'),x('TR ').cat(ref('tr_dano')).cat(' · CD ').cat(ref('cd_normal')).cat(IF(tm,' · sucesso: 3/4 do dano',' · sucesso: metade do dano')),ref('res_dano'))))
    add('resolucao_cura','Automática em aliado disposto; independente do ataque, salvo dependência registrada')
    add('resolucao_vt','Automática em aliado disposto; não soma reservas; conferir teto geral')
    def efeito(i):
        nome=ref('nome_m'+str(i)); rot=ref('m'+str(i))
        def escolhe(n,valor,alternativa): return IF(nome.eq(n),valor,alternativa)
        valor=rot
        for n,t in [('Guarda','+2 Defesa até o fim do próximo turno do alvo'),
                    ('Impulso','vantagem no próximo ataque até o fim do próximo turno do alvo'),
                    ('Firmeza','vantagem no próximo teste da categoria até o começo do próximo turno de quem conjurou'),
                    ('Prende','TR inicial e de saída; Padrão/Bônus/Movimento para tentar escapar'),
                    ('Cerca','TR; termina se quem conjurou causar dano ao alvo'),
                    ('Condição','TR mesmo após acerto; Pesada permite TR de saída no fim dos turnos'),
                    ('Salto','um secundário por conjuração; metade da parcela inicial destinada à origem'),
                    ('Estilhaço','um secundário por conjuração; metade da parcela inicial destinada à origem'),
                    ('Queima','metade da parcela inicial do alvo, uma vez; não repete outras peças'),
                    ('Gesto','duas mãos livres e fala audível'),
                    ('Quebra Coisa','dobre apenas o dano inicial contra objetos/barreiras; multiplicador incluído no teto da montagem'),
                    ('Remate','+25% no dano inicial; esse aumento já conta no teto da montagem'),
                    ('Acúmulo','+1d8 no segundo uso, +2d8 no terceiro e +3d8 a partir do quarto contra o alvo acompanhado; crescimento pode ultrapassar o teto, sem replicar dados por tiro')]:
            valor=escolhe(n,rot.cat(': '+t),valor)
        valor=escolhe('Fura',rot.cat(': ignora até ').cat(ref('fura_rd')).cat(' RD'),valor)
        valor=escolhe('Anteparo',rot.cat(': ').cat(ref('anteparo_pv')).cat(' PV, 1 minuto, sem TR'),valor)
        valor=escolhe('Levanta',rot.cat(': ').cat(5*IF(entidade,reduzida,c)).cat(' de vida; encerra Morrendo; um aliado ainda Morrendo, uma vez por cena entre todos os feitiços; não revive mortos'),valor)
        valor=escolhe('Remenda',rot.cat(': ').cat(5*IF(entidade,reduzida,c)).cat(' Integridade; uma vez por alvo por cena'),valor)
        valor=escolhe('Sugar',rot.cat(': quarto do dano elegível, teto ').cat(5*IF(entidade,reduzida,c)).cat('; depende de causar dano'),valor)
        curto=OR(*[nome.eq(n) for n in ['Condição','Prende','Cerca','Terreno']],LOOK(rot,'controle_compat').gt(0))
        prolongado=npeca('Concentrada / Duradoura').gt(0)
        valor=IF(AND(OR(limdano,semdano),curto,prolongado.eq(False)),valor.cat(' · +1 rodada no prazo curto; conserva o término e as saídas'),valor)
        valor=IF(AND(semdano,LOOK(rot,'controle_compat').gt(0),LOOK(rot,'tr').gt(0)),valor.cat(' · TR próprio e saídas: CD ').cat(ref('cd_controle')),valor)
        return IF(rot.eq(''),'',valor)
    add('efeitos',JOIN(*[efeito(i) for i in range(1,5)],
        IF(AND(entidade,npeca('Segura').gt(0)),'Segura: pague comando, básica e custos agora; resolva no próximo turno sem novo pagamento',''),
        IF(AND(entidade,npeca('Armado').gt(0)),'Armado: pague comando, básica e custos ao armar; gatilho resolve sem nova básica, comando ou coletiva; uma especial pendente',''),
        IF(AND(entidade,nres('Atrasar').gt(0)),'Atrasar: sua Padrão normal + básica; a entidade não se desloca voluntariamente nesse turno',''),
        IF(AND(entidade,nres('Carregar').gt(0)),'Carregar: sua Padrão normal + básica e PE agora; outra básica no próximo turno, sem novo comando ou PE; dano nela exige TR Espírito',''),
        IF(tm,'Máxima: uma vez por cena; repetição após 3 rodadas somente com permissão do mestre; sair/voltar não renova',''),
        IF(lib,IF(nres('Sem Volta').gt(0),'Liberação: escolha Sangue (4 × Classe na vida) ou Peso; Vazio repete Sem Volta','Liberação: escolha Vazio, Sangue (4 × Classe na vida) ou Peso a cada uso; o preço não devolve pontos'),''),
        IF(npeca('Concentrada / Duradoura').gt(0),'Prazo prolongado: use o menor prazo aplicável da tabela; sem rodada adicional de Controle, sem repetir dano ou usos consumidos','')))
    add('acao',IF(entidade,IF(zero,'Atuação básica da entidade',IF(OR(tm,lib),'Sua Ação Completa + uma básica da entidade',IF(nres('Carregar').gt(0),'Sua Padrão normal + básica agora; outra básica no próximo turno',IF(npeca('Reação').gt(0),'Comunique o comando no gatilho + Reação coletiva; sem básica ou sua Reação',IF(npeca('Rápido').gt(0),'Sua Ação Bônus + uma básica da entidade','Sua Ação Padrão + uma básica da entidade'))))),IF(OR(tm,lib,nres('Atrasar').gt(0)),'Ação Completa',IF(npeca('Reação').gt(0),'Reação',IF(npeca('Rápido').gt(0),'Ação Bônus','Ação Padrão')))))
    add('funcao',JOIN(IF(ref('dano'),x('Dano ').cat(ref('dano_resultado')),''),IF(ref('cura'),x('Cura ').cat(cura).cat('d8'),''),
        IF(ref('vt'),x('Vida temporária ').cat(vt).cat(' pontos'),''),
        IF(AND(ref('dano').eq(False),ref('cura').eq(False),ref('vt').eq(False),qtdm.eq(0)),'Utilidade definida na Regra; sem resultado variável',''),
        IF(npeca('Guarda').gt(0),'Guarda (+2 Defesa)',''),IF(npeca('Impulso').gt(0),'Impulso (vantagem no próximo ataque)',''),
        *[IF(ref('nome_m'+str(i)).eq('Firmeza'),ref('m'+str(i)),'') for i in range(1,5)],
        IF(semdano,'Controle sem dano; saldo descartado',''),
        IF(npeca('Prende').gt(0),'Prende: TR próprio',''),IF(npeca('Anteparo').gt(0),x('Anteparo ').cat(ref('anteparo_pv')).cat(' PV'),''),
        *[IF(OR(*[ref('nome_m'+str(i)).eq(n) for n in ['Guarda','Impulso','Firmeza','Prende','Anteparo','Longe','Maior','Precisão','Fura','Rápido','Reação','Concentrada / Duradoura','Mais Um','Rajada']]),'',ref('m'+str(i))) for i in range(1,5)],
        IF(AND(sobra.gt(0),semdano.eq(False)),x('Saldo sem uso ').cat(sobra).cat(IF(sobra.eq(1),' ponto',' pontos')),'')))
    erros=[]
    def err(c,t):
        # A interface direta guarda a adjudicação na descrição. Só os avisos
        # que exigiam campos textuais separados são dispensados nessa rota.
        if registro_livre and (t.startswith(('A Regra/definição','Registre destinatários','Registre a permissão','Registre independência','Escolha o tipo do TR','TR da aplicação','Sem Volta exige','Rajada exige','Tudo ou Nada exige'))):return
        erros.append(IF(c,t,''))
    err(OR(publicada,propria).eq(False),'Forma não publicada: cadastrar ou revisar antes do uso')
    err(AND(propria,FAMILY(FORM(rawforma,'familia')).eq('Fechada')),'Família Fechada: Forma própria indisponível')
    err(AND(propria,zero,FORM(rawforma,'classe_0').eq(False)),'Forma própria não permite Classe0')
    err(AND(propria,FORM(rawforma,'restricao_embutida').ne('')),'Forma própria com Restrição embutida: conferir a conversão para as exigências R53 antes do uso')
    err(ref('preparada').eq(False),'Versão não preparada')
    err(AND(zero.eq(False),OR(c.lt(1),c.gt(7),c.gt(ref('classe_maxima')))),'Classe indisponível')
    err(AND(zero,c.ne(0)),'Básica/Classe 0 usa Classe 0')
    err(AND(tm,nivel.lt(17)),'Técnica Máxima: nível mínimo 17')
    err(AND(lib,c.lt(3)),'Liberação Máxima: Classe mínima 3')
    err(OR(*[ref('p_'+n).ne(INT(ref('p_'+n))) for n in ['dano','cura','vt']],*[ref('p_'+n).lt(0) for n in ['dano','cura','vt']]),'Distribua pontos inteiros não negativos')
    err(AND(zero.eq(False),tm.eq(False),semdano.eq(False),SUM([ref('p_dano'),ref('p_cura'),ref('p_vt')]).gt(saldo)),'Distribuição excede o saldo')
    err(AND(saldo.lt(0)),'Orçamento excedido')
    err(qtdm.gt(maxmel),'Limite de Melhorias excedido');err(qtdr.gt(maxres),'Limite de Restrições excedido')
    err(AND(OR(ref('cura'),ref('vt')),ref('fam_Amparo').eq('Fechada')),'Amparo Fechada: cura direta/vida temporária indisponíveis')
    err(AND(OR(area,npeca('Mais Um').gt(0)),ref('fam_Área').eq('Fechada')),'Área Fechada: Forma de área/Mais Um indisponíveis')
    # Uma área exclusivamente pessoal pode existir, mas nunca ganha devolução de Toque/Queima-Roupa.
    for n,perm in [('dano','permite_dano'),('cura','permite_cura'),('vt','permite_vt')]:
        err(AND(ref(n),ref(perm).eq(False)),'A Regra/definição não autoriza '+n)
        err(AND(ref(n),ref('dest_'+n).eq('')),'Registre destinatários de '+n)
        err(AND(ref(n).eq(False),ref('p_'+n).gt(0)),'Pontos atribuídos à função não escolhida: '+n)
        err(AND(ref(n),zero.eq(False),tm.eq(False),semdano.eq(False),ref('p_'+n).lt(1)),'Reserve ao menos um ponto: '+n)
    err(ref('origem_permissao').eq(''),'Registre a permissão da Regra/definição')
    err(AND(zero,OR(ref('cura'),ref('vt'),AND(area,ref('dano').eq(False)))),'Classe 0: sem cura, vida temporária ou benefícios coletivos')
    err(AND(lib,ref('cura')),'Liberação Máxima não serve para cura')
    err(AND(tm,OR(ref('vt'),AND(ref('dano'),ref('cura')))),'Máxima escolhe dano, cura ou aplicação sem dano')
    err(AND(area,tm.eq(False),(pc+pv).gt(MAX(0,orc-p))),'Cura e vida temporária excedem juntas o teto coletivo')
    err(AND(OR(semdano,limdano),ctrl.eq(False)),'Reforço exige Melhoria de Controle')
    err(AND(ref('controle').ne('Sem reforço'),comum.eq(False)),'Esta modalidade não recebe reforço de Controle')
    err(AND(semdano,OR(ref('dano'),ref('cura'),ref('vt'),SUM([ref('p_dano'),ref('p_cura'),ref('p_vt')]).gt(0))),'Sem dano descarta todo o saldo, incluindo cura e vida temporária')
    err(AND(OR(forma.eq('Toque'),forma.eq('Aura')),npeca('Longe').gt(0)),'Toque/Aura não aceita Longe')
    err(AND(nres('Queima-Roupa').gt(0),OR(forma.eq('Toque'),forma.eq('Aura'),ref('pessoal'))),'Queima-Roupa incompatível com Forma/pessoal')
    err(AND(nres('Queima-Roupa').gt(0),npeca('Longe').gt(0)),'Queima-Roupa conserva proximidade: não aceita Longe')
    err(AND(npeca('Maior').gt(0),area.eq(False)),'Maior exige Forma de área')
    err(AND(nres('Barulho').gt(0),nres('Assinatura').gt(0)),'Barulho e Assinatura: escolha uma exposição')
    err((nres('Recuo')+nres('Fraqueza')+nres('Peso Morto')).gt(1),'Recuo, Fraqueza e Peso Morto não se combinam')
    err(AND(npeca('Terreno').gt(0),area.eq(False)),'Terreno exige Forma de área')
    err(AND(npeca('Mais Um').gt(0),area),'Mais Um acrescenta destinatários individuais, não áreas')
    err(AND(nres('Sem Volta').gt(0),ref('res_dano').eq('Automático')),'Sem Volta exige possibilidade de falha completa')
    err(AND(ref('dano'),ref('res_dano').eq('TR'),OR(*[ref('tr_dano').eq(n) for n in TRS]).eq(False)),'Escolha o tipo do TR de dano')
    err(AND(efeitosctrl,OR(*[ref('tr_controle').eq(n) for n in TRS]).eq(False)),'Escolha o tipo do TR de Controle')
    err(AND(efeitosctrl,ref('dano'),ref('res_dano').eq('TR'),ref('tr_dano').ne(ref('tr_controle'))),'TR da aplicação: mesmo tipo para dano e Controle; CDs podem diferir')
    err(AND(nres('Atrasar').gt(0),nres('Parado').gt(0)),'Atrasar e Parado repetem impedimento')
    err(AND(nres('Atrasar').gt(0),npeca('Rápido').gt(0)),'Atrasar e Rápido incompatíveis')
    err(AND(npeca('Reação').gt(0),OR(npeca('Rápido').gt(0),npeca('Armado').gt(0),nres('Atrasar').gt(0),nres('Parado').gt(0))),'Reação incompatível com Rápido/Armado/Atrasar/Parado')
    err(AND(npeca('Armado').gt(0),nres('Carregar').gt(0)),'Armado e Carregar incompatíveis')
    err(AND(OR(*[ref('m'+str(i)).eq('Concentrada') for i in range(1,5)]),OR(*[ref('m'+str(i)).eq('Duradoura') for i in range(1,5)])),'Escolha Concentrada ou Duradoura')
    err(AND(ref('dano'),OR(ref('cura'),ref('vt')),ref('dependencias').eq('')),'Registre independência ou dependência das parcelas da mescla')
    err(AND(npeca('Fica').gt(0),OR(area.eq(False),ref('dano').eq(False))),'Fica exige área de dano')
    err(AND(npeca('Rajada').gt(0),OR(area,ref('res_dano').ne('Ataque'),ref('dano').eq(False))),'Rajada exige alvo individual com ataque e dados')
    err(AND(nres('Tudo ou Nada').gt(0),OR(ref('dano').eq(False),ref('res_dano').ne('TR'))),'Tudo ou Nada exige dano por TR')
    err(AND(nres('Frágil').gt(0),ref('fragil_pago').le(0)),'Frágil exige Melhorias interrompíveis pagas')
    err(ref('fragil_pago').gt(pago),'Frágil: gasto interrompível não pode exceder o gasto real')
    err(SUM([LOOK(ref('r'+str(i)),'frequencia') for i in [1,2]]).gt(1),'Uma Vez/Condicional/Aquecer: um grupo de frequência')
    err(AND(npeca('Toca a Alma').gt(0),OR(c.lt(3),False if registro_livre else ref('permite_alma').eq(False),lib)),'Toca a Alma exige Classe 3, Regra de alma e não aceita Liberação')
    err(AND(npeca('Inescapável').gt(0),OR(forma.ne('Projétil'),ref('dano').eq(False),qtdm.gt(1),qtdr.gt(0),tm,lib)),'Inescapável: só Projétil de dano, única Melhoria, sem Restrições ou máximas')
    err(AND(tm,OR(*[npeca(n).gt(0) for n in ['Salto','Queima','Estilhaço','Acúmulo','Remate','Fica','Inescapável','Armado','Segura']])),'Peça não permitida na Técnica Máxima')
    err(AND(npeca('Remate').gt(0),nres('Aquecer').gt(0)),'Remate não combina com Aquecer')
    err(AND(npeca('Passo').gt(0),OR(nres('Atrasar').gt(0),nres('Parado').gt(0))),'Passo impedido por Atrasar/Parado')
    for i in range(1,5):
        v=ref('m'+str(i));w=ref('peso_m'+str(i));nome=ref('nome_m'+str(i))
        err(AND(v.ne(''),LOOK(v,'tipo').ne('melhorias')),'Melhoria não reconhecida: posição '+str(i))
        err(ref('fechada_m'+str(i)).gt(0),'Família Fechada: Melhoria '+str(i))
        err(c.lt(LOOK(v,'classe_minima')),'Classe insuficiente: Melhoria '+str(i))
        err(AND(zero,v.ne(''),w.ne(1)),'Classe 0 aceita somente Melhoria Leve')
        variantes_repetiveis=OR(*[nome.eq(n) for n in ['Condição','Firmeza','Longe','Maior','Mais Um','Efeito Próprio']])
        qtd_nome=SUM([IF(nome.eq(ref('nome_m'+str(j))),1,0) for j in range(1,5)])
        qtd_opcao=SUM([IF(LOOK(v,'rotulo_base').eq(LOOK(ref('m'+str(j)),'rotulo_base')),1,0) for j in range(1,5)])
        err(AND(v.ne(''),IF(variantes_repetiveis,qtd_opcao,qtd_nome).gt(LOOK(v,'repeticoes'))),'Compra repetida sem permissão: Melhoria '+str(i))
        err(AND(entidade,OR(zero,ref('execucao').ne('Comandada')),nome.eq('Condição'),w.ge(2)),'Condição Média/Pesada exige especial comandada')
        err(AND(OR(*[nome.eq(n) for n in ['Condição','Prende','Cerca']]),LOOK(v,'tr').le(0)),'A base do livro exige TR: Melhoria '+str(i))
        err(AND(v.ne(''),LOOK(v,'cadastro_valido').le(0)),'Efeito Próprio/cadastro: registrar Família, preço e limites antes do uso')
        err(AND(LOOK(v,'proprio').gt(0),ref('familia_m'+str(i)).eq('Controle'),ref('controle').ne('Sem reforço'),LOOK(v,'controle_compat').le(0)),'Controle próprio: registrar compatibilidade de duração, TR e saída antes do reforço')
    err(SUM([IF(AND(ref('nome_m'+str(i)).eq('Condição'),ref('peso_m'+str(i)).eq(3)),1,0) for i in range(1,5)]).gt(1),'Só uma Condição Pesada por aplicação')
    for i in [1,2]:
        v=ref('r'+str(i));nome=ref('nome_r'+str(i))
        err(AND(v.ne(''),LOOK(v,'tipo').ne('restricoes')),'Restrição não reconhecida: posição '+str(i))
        err(AND(v.ne(''),ref('r'+str(i)+'_valida').eq(False)),'Confirme exigência válida: Restrição '+str(i))
        err(AND(zero,v.ne(''),OR(ref('peso_r'+str(i)).ne(1),AND(nome.eq('Queima-Roupa'),forma.eq('Projétil')))),'Classe 0 aceita somente Restrição Leve válida')
    err(AND(ref('r1').ne(''),ref('nome_r1').eq(ref('nome_r2'))),'Não repetir o mesmo impedimento')
    err(ref('migracao').eq('Revisão necessária'),'Registro antigo exige revisão antes do uso')
    avisos=add('avisos',JOIN(*erros))
    add('valida',avisos.eq(''))
    return out

ARVORE=arvore()


def calcular(entradas,catalogo_extra=None,familias_custom=None,formas_custom=None):
    env={**DEFAULTS,**entradas,'_familias':familias_custom or {},'_formas':formas_custom or {}}
    opcoes={**OPCOES,**(catalogo_extra or {})}
    for k,expr in ARVORE.items(): env[k]=evaluate(expr,env,opcoes)
    return env


def formulas(linha, colunas, lookup_range, separator=',',familias_range=None,familias_coluna=2,formas_range=None,registro_livre=False,saidas=None):
    refs={k:colunas[k]+str(linha) for k in INPUTS+list(ARVORE)}
    if formas_range:
        from formas_custom import CAMPOS as FC
        refs.update(__formas_range__=formas_range,__formas_campos__=FC)
    if familias_range:refs.update(__familias_range__=familias_range,__familias_col__=str(familias_coluna))
    return {k:'='+native(expr,refs,lookup_range,LOOKUP_FIELDS,separator) for k,expr in (arvore(True) if registro_livre else ARVORE).items() if saidas is None or k in saidas}
