"""Guardas da migração e recibos nativos; não depende de evidências privadas."""
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'r53'),str(ROOT/'r53/testes'),str(ROOT/'ficha-v01')]
from avisos_cartoes_r53 import formula_avisos_funcoes
from diagnosticos_funcoes import planejar, assinatura, formula_nativa
from revisao_mecanicas import conferir, cells


def import_aviso_requisito():
    import montagens_r53
    return montagens_r53.aviso_requisito


def fixture():
    g=dict(id='feitico.1',linha=2,editor=5,classes=[1,2,3,4,5,6,7],fixa=False,
        aba='FICHA AMALDIÇOADA',funcoes_diretas={'cura':'F71','vt':'G71'},
        portas={'cura':'\'DADOS_R53\'!$AS$2<>"Fechada"','vt':'\'DADOS_R53\'!$AS$2<>"Fechada"'},
        campos={'funcao2':11,'funcao3':13})
    guards=['B','C','H','I','J','K','L','M']
    model=dict(layout={'abas':[{'nome':'DADOS_R53','celulas':[['GA2','=""',0]]+[[c+'2','=0',0] for c in guards]}]},
        r53={'colunas':{'avisos_funcoes':'GA'},'contextos':[g]})
    snapshot={'sheets':[{'properties':{'title':'DADOS_R53','sheetId':123},'data':[
        {'startRow':1,'rowData':[{'values':[{'userEnteredValue':{'stringValue':'feitico.1'}}]}]},
        {'startRow':1,'startColumn':182,'rowData':[{'values':[{'userEnteredValue':{'formulaValue':'=""'}}]}]}]}]}
    values=snapshot['sheets'][0]['data'][0]['rowData'][0]['values']
    for i in range(2,14):values.append({'userEnteredValue':{'formulaValue':'=0'}} if chr(64+i) in guards else {})
    return g,model,snapshot


class DiagnosticosTest(unittest.TestCase):
    def test_canonicalizacao_nativa_so_reduz_intervalo_de_uma_celula(self):
        self.assertEqual(assinatura("=INDEX('MONTAGENS'!$B$11:$B$11,1,1)"),assinatura('=INDEX(MONTAGENS!B11;1;1)'))
        self.assertNotEqual(assinatura('=SUM(MONTAGENS!B11:C11)'),assinatura('=SUM(MONTAGENS!B11)'))
        self.assertEqual(formula_nativa('=IF(1.5>0,"a,b","")'),'=IF(1,5>0;"a,b";"")')

    def test_usa_funcao_salva_da_classe_ativa_e_entrada_preservada(self):
        g,_,_=fixture();f=formula_avisos_funcoes(g)
        self.assertIn('INDEX(\'MONTAGENS\'!$B$11:$H$11,1,MATCH(\'DADOS_R53\'!$C$2',f)
        self.assertIn('ISNUMBER(\'FICHA AMALDIÇOADA\'!F71)',f)
        self.assertNotIn('$I$2',f)  # o flag efetivo já foi bloqueado, não serve como intenção

    def test_modalidade_fixa_nao_exige_cabecalhos_e_preserva_trunfo(self):
        g,_,_=fixture();g.update(classes=[0],fixa=True,requisito='1=0')
        g['portas']['cura']='FALSE';f=formula_avisos_funcoes(g)
        self.assertNotIn('MATCH(',f);self.assertIn('F71=TRUE',f)
        self.assertIn('Trunfo exige',f);self.assertIn('Função indisponível nesta modalidade: cura',f)

    def test_requisito_usa_texto_configuravel_da_main(self):
        # R67/main: o texto do requisito vem de R.aviso_requisito (Liberação Máxima N), não do Trunfo fixo.
        g,_,_=fixture();g.update(requisito='X1>=20',aviso_requisito='Liberação Máxima 2: nível mínimo 20')
        g['portas']['cura']='FALSE';f=formula_avisos_funcoes(g)
        self.assertIn('IF(X1>=20,"","Liberação Máxima 2: nível mínimo 20")',f)
        self.assertNotIn('Trunfo exige',f)
        self.assertIn('Função indisponível nesta modalidade: cura',f)
        self.assertIn('Amparo Fechada: função de vida temporária salva indisponível',f)

    def test_sem_requisito_e_sem_porta_bloqueavel_fica_vazio(self):
        g,_,_=fixture();g['portas']={'dano':'TRUE','cura':'TRUE','vt':'TRUE'}
        self.assertEqual(formula_avisos_funcoes(g),'=""')
        g.update(requisito='1=1');self.assertEqual(formula_avisos_funcoes(g),'=IF(1=1,"","Trunfo exige maldição domada com técnica própria e nível de aquisição")')

    def test_defeito_plantado_formula_antiga_cala_cura_salva(self):
        # A fórmula da main antes desta mudança era só o requisito: com Amparo Fechada não dizia nada.
        g,_,_=fixture();f=formula_avisos_funcoes(g)
        self.assertIn('Amparo Fechada: função de cura salva indisponível',f)
        self.assertIn('INDEX(\'MONTAGENS\'!$B$11:$H$11',f)
        self.assertIn('INDEX(\'MONTAGENS\'!$B$13:$H$13',f)
        self.assertNotIn('Amparo Fechada',import_aviso_requisito()(g))

    def test_carta_extra_separa_classe_zero_da_amparo(self):
        g,_,_=fixture();amparo='\'DADOS_R53\'!$AS$2<>"Fechada"'
        g['portas']={'dano':'TRUE','cura':f"AND('DADOS_R53'!$C$2<>0,{amparo})",'vt':f"AND('DADOS_R53'!$C$2<>0,{amparo})"}
        f=formula_avisos_funcoes(g)
        self.assertIn(f'IF(NOT({amparo}),"Amparo Fechada: função de cura salva indisponível","Classe 0 (Básica): função de cura salva indisponível")',f)
        self.assertEqual(f.count('Classe 0 (Básica)'),2)

    def test_classe_ativa_pode_vir_da_coluna_do_modelo(self):
        g,_,_=fixture();f=formula_avisos_funcoes(g,"'DADOS_R53'!$C$2")
        self.assertIn("MATCH('DADOS_R53'!$C$2,",f)

    def test_migracao_so_ga_reversao_exata_repeticao_zero(self):
        _,m,s=fixture();p=planejar(m,s);self.assertEqual(len(p['pedidos']),1)
        u=p['pedidos'][0]['updateCells'];self.assertEqual(u['start'],dict(sheetId=123,rowIndex=1,columnIndex=182))
        self.assertEqual(u['fields'],'userEnteredValue')
        self.assertEqual(p['reversao'][0]['updateCells']['rows'][0]['values'][0]['userEnteredValue'],{'formulaValue':'=""'})
        s['sheets'][0]['data'][1]['rowData'][0]['values'][0]['userEnteredValue']=u['rows'][0]['values'][0]['userEnteredValue']
        p=planejar(m,s);self.assertEqual(p['pedidos'],[]);self.assertEqual(p['ja_atualizadas'],1)

    def test_alvo_vem_do_modelo_novo_com_embrulho(self):
        # Classe 0/Prática/trilha embrulham a GA na main: o alvo é a célula gerada, não a fórmula crua.
        g,m,s=fixture();wrapped='=TEXTJOIN(" · ",TRUE,'+formula_avisos_funcoes(g)[1:]+',"Revisar limite de Classe 0")'
        novo=copy.deepcopy(m);novo['layout']['abas'][0]['celulas'][0][1]=wrapped
        p=planejar(m,s,novo);new=p['pedidos'][0]['updateCells']['rows'][0]['values'][0]['userEnteredValue']['formulaValue']
        self.assertEqual(new,formula_nativa(wrapped));self.assertIn('Revisar limite de Classe 0',new)

    def test_recusa_id_formula_ou_leitura_incompleta(self):
        _,m,s=fixture()
        for kind in ['id','formula','ausente']:
            altered=copy.deepcopy(s)
            if kind=='id':altered['sheets'][0]['data'][0]['rowData'][0]['values'][0]['userEnteredValue']['stringValue']='outra'
            elif kind=='formula':altered['sheets'][0]['data'][1]['rowData'][0]['values'][0]['userEnteredValue']['formulaValue']='=42'
            else:altered['sheets'][0]['data'].pop()
            with self.subTest(kind=kind),self.assertRaises(ValueError):planejar(m,altered)

    def test_id_igual_nao_basta_se_endereco_da_entrada_mudou(self):
        _,m,s=fixture()
        s['sheets'][0]['data'][0]['rowData'][0]['values'][11]['userEnteredValue']['formulaValue']="='FICHA AMALDIÇOADA'!F379"
        with self.assertRaisesRegex(ValueError,'Layout/entrada divergente: L2'):planejar(m,s)

    def test_false_zero_e_erro_nao_viram_vazio_no_recibo(self):
        s={'sheets':[{'properties':{'title':'DADOS_R53'},'data':[{'rowData':[{'values':[
            {'effectiveValue':{'boolValue':False}}, {'effectiveValue':{'numberValue':0}},
            {'effectiveValue':{'errorValue':{'type':'N_A'}}}]}]}]}]}
        v=cells(s);self.assertIs(v['DADOS_R53!A1'],False);self.assertEqual(v['DADOS_R53!B1'],0)
        self.assertEqual(v['DADOS_R53!C1'],{'type':'N_A'})

    def test_recibo_ausente_nunca_aprova_uma_comparacao(self):
        p={'casos':[{'nome':'cura','esperado':{'cura_d8':2},'leituras':{'cura_d8':"'DADOS_R53'!DT2",'avisos':"'DADOS_R53'!FX2"}}]}
        self.assertEqual(len(conferir(p,{'sheets':[]})['falhas']),1)


if __name__=='__main__':unittest.main()
