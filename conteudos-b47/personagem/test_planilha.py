"""Ensaios no modelo real em memória. Recálculo Calc/Sheets é separado."""
import json
from pathlib import Path
import unittest
from copy import deepcopy
from openpyxl.formula import Tokenizer
from openpyxl.utils.cell import range_boundaries,coordinate_from_string
from openpyxl.utils import get_column_letter as L
from b47_personagem.fontes_livro import carregar,ROOT
from b47_personagem.motor import CAMPOS
from b47_personagem.planilha import Contrato,emitir,exportar,criterio
from b47_personagem.consumidores import canonizar_comparacoes
from b47_personagem import aplica,exporta
from fixture_base import montar


class TestPlanilha(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print('Fixture real em memória, sem geração de arquivos canônicos',flush=True)
        cls.base=montar();cls.layout=cls.base['LAYOUT']
        print('Fixture pronta; adaptando os consumidores',flush=True)
        cls.antes={a['nome']:{c[0]:c[1] for c in a['celulas']} for a in cls.layout['abas']}
        cls.menus_antes={a['nome']:deepcopy(a.get('menus',[])) for a in cls.layout['abas']}
        cls.contexto=dict(fam=cls.base['_FAM'],inv=cls.base['_FIV'],criacao=cls.base['_CRIACAO'],pecas=cls.base['_PECAS'],
            capacidades={'forma':10,'aptidao':10,'talento':10},
            inicio=next(a['linhas'] for a in cls.layout['abas'] if a['nome']=='CONFIGURAÇÃO')+4,
            abas={'forma':'ENSAIO_FORMAS','aptidao':'ENSAIO_APTIDOES','talento':'ENSAIO_TALENTOS'})
        cls.tr=aplica(cls.layout,cls.contexto)
        cls.tabs={a['nome']:a for a in cls.layout['abas']}
        cls.cells={s:{c[0]:c[1] for c in a['celulas']} for s,a in cls.tabs.items()}
        print('Modelo adaptado; verificando fontes e fórmulas',flush=True)

    def test_manifesto_completo_das_escritas(self):
        for owner,cells in self.cells.items():
            for cel,value in cells.items():
                anterior=self.antes.get(owner,{}).get(cel)
                if value!=anterior:
                    self.assertEqual(self.tr['depois'].get(owner,{}).get(cel),value,owner+'!'+cel)

    def test_formulas_alteradas_no_nucleo_tambem_analisadas(self):
        for owner,changes in self.tr['depois'].items():
            for cel,v in changes.items():
                if not isinstance(v,str) or not v.startswith('='):continue
                tokens=Tokenizer(v).items
                stack=[]
                for token in tokens:
                    if token.subtype=='OPEN' and token.type in ('FUNC','PAREN','ARRAY'):stack.append(token.type)
                    elif token.subtype=='CLOSE' and token.type in ('FUNC','PAREN','ARRAY'):
                        self.assertTrue(stack,owner+'!'+cel);stack.pop()
                self.assertFalse(stack,owner+'!'+cel)
                self.assertLess(len(v),8192,owner+'!'+cel)

    def test_avisos_uso_atendem_cartas_existentes(self):
        self.assertEqual(len(self.tr['avisos_uso']),24)
        for item in self.tr['avisos_uso']:
            owner,cel=item['fonte'].rsplit('!',1)
            self.assertIn(cel.replace('$',''),self.cells[owner.strip("'")])

    def test_somente_tres_catalogos_adicionais(self):
        self.assertEqual(set(self.tabs)-set(self.antes),{'ENSAIO_FORMAS','ENSAIO_APTIDOES','ENSAIO_TALENTOS'})
        for nome in self.contexto['abas'].values():
            self.assertEqual(self.tabs[nome]['estado'],'hidden');self.assertTrue(self.tabs[nome]['paleta_fixa'])

    def test_primeira_ultima_e_exportacao_crua(self):
        out=exporta(self.tr);keys=[x[0] for x in out]
        self.assertEqual(len(keys),len(set(keys)))
        for grupo in CAMPOS:
            for n in (1,10):self.assertIn(f'custom.{grupo}.{n}.nome',keys)
        self.assertNotIn('formato.versao',keys)
        self.assertIn('custom.talento.10.categoria',keys)
        self.assertIn('custom.forma.10.classe_zero',keys)
        self.assertTrue(any('IF(ISBLANK(' in x[1] for x in out))

    def test_sem_sobreposicao_mesclas(self):
        used={}
        for region in self.tabs['CONFIGURAÇÃO']['mescladas']:
            c,r,cc,rr=range_boundaries(region)
            for row in range(r,rr+1):
                for col in range(c,cc+1):
                    self.assertNotIn((row,col),used,f'CONFIGURAÇÃO!{L(col)}{row}: {region} sobrepõe {used.get((row,col))}')
                    used[(row,col)]=region

    def test_editor_preserva_todos_os_campos_anteriores(self):
        for cel,v in self.antes['CONFIGURAÇÃO'].items():self.assertEqual(self.cells['CONFIGURAÇÃO'][cel],v,'CONFIGURAÇÃO!'+cel)

    def test_menus_reais_personagem_e_12_entidades(self):
        menus=[m for s in self.tabs.values() for m in s.get('menus',[]) if 'ENSAIO_FORMAS' in str(m.get('formula',''))]
        # O gerador guarda menus de blocos-modelo e copia validações junto com
        # as cartas. Contar objetos menus não conta os destinos materializados.
        fam=self.base['_FAM']
        self.assertEqual(len(fam['lugares'])+len(fam['zero_c'])+1,45)
        self.assertEqual(len(self.base['_FIV']['cartas']),156)
        self.assertTrue(menus)
        for owner,antes in self.menus_antes.items():
            depois=self.tabs[owner].get('menus',[])
            self.assertLessEqual(len(antes),len(depois),owner)
            for old,new in zip(antes,depois):
                self.assertEqual(old['onde'],new['onde'],(owner,old))
        inv=self.base['_FIV'];names=self.tr['catalogos']
        self.assertEqual(len([k for k in names if k.startswith('menu_entidade_')]),12)
        for g in inv['fichas_c']:self.assertEqual(len(g['fam']),9)

    def test_livro_vai_antes_de_dez_custom(self):
        p=self.tr['plano']
        for grupo,t in p.tabelas.items():
            self.assertEqual(t['total'],t['livro']+10)
            self.assertEqual(t['primeiro_custom'],t['livro']+2)

    def test_resumos_do_livro_no_menu_rapido_preservados(self):
        for original,bridge in [('aptidoes','aptidoes'),('passivas','passivas')]:
            meta=self.tr['catalogos'][bridge]
            for row,item in enumerate(self.base['_FAM']['R'][original],2):
                self.assertEqual(self.cells[meta['aba']][L(meta['coluna']+meta['largura']-1)+str(row)],item['resumo'])

    def test_vazios_herdados_nao_viram_zero(self):
        # BASE do registro publicado é vazia. Uma fórmula de texto vazio
        # conserva seu tipo ao ser buscada por INDEX no Sheets.
        for t in self.tr['plano'].tabelas.values():
            for row in range(2,t['livro']+2):
                self.assertEqual(self.cells[t['aba']][L(t['colunas']['base'])+str(row)],'=""')
        for group,field,neutral in [('forma','peso','0'),('forma','exige_tr','FALSE'),('talento','ce','0')]:
            t=self.tr['plano'].tabelas[group]
            for row in range(t['primeiro_custom'],t['total']+2):
                self.assertTrue(self.cells[t['aba']][L(t['colunas'][field])+str(row)].endswith(','+neutral+')'))

    def test_tabelas_distintas_3_e_4_faixas(self):
        names=self.tr['catalogos'];total=self.tr['plano'].tabelas['forma']['total']
        self.assertEqual(names['alcance_personagem']['ultimo']-1,total*3)
        self.assertEqual(names['alcance_entidade']['ultimo']-1,total*4)

    def test_celulas_e_formulas_sem_erro_sintatico(self):
        for nome in self.contexto['abas'].values():
            for cel,v in self.cells[nome].items():
                if isinstance(v,str) and v.startswith('='):
                    self.assertNotIn('#REF!',v,nome+'!'+cel)
                    tokens=Tokenizer(v).items
                    pilha=[]
                    for t in tokens:
                        if t.subtype=='OPEN' and t.type in ('FUNC','PAREN','ARRAY'):pilha.append(t)
                        elif t.subtype=='CLOSE' and t.type in ('FUNC','PAREN','ARRAY'):
                            self.assertTrue(pilha,(nome,cel,v));pilha.pop()
                    self.assertFalse(pilha,(nome,cel,v))

    def test_identidade_nao_altera_texto_exibido(self):
        f='=IF($F2="Cone","A Forma "&$F2&" é Cone","")'
        g=canonizar_comparacoes(f,'$F2','$ZZ2',{'Cone'})
        self.assertEqual(g,'=IF($ZZ2="Cone","A Forma "&$F2&" é Cone","")')

    def test_canonizacao_atinge_as_cartas_reais(self):
        for owner,meta,table in [('DADOS_AM',self.base['_FAM'],'feit'),('DADOS_INVOC',self.base['_FIV'],'cartas')]:
            r=meta['D'].T[table][1]
            formula=self.cells[owner][L(meta['col']['erros'])+str(r)]
            self.assertIn('Forma não cadastrada ou com erro',formula,owner)
            self.assertIn('ENSAIO_FORMAS',formula,owner)
            self.assertIn('Restrição repetida, contando a embutida',formula,owner)

    def test_buscas_literais_reais(self):
        meta=self.base['_FAM'];r=meta['D'].T['feit'][1]
        cel=L(meta['col']['lf'])+str(r)
        self.assertIn('SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(',self.cells['DADOS_AM'][cel],'DADOS_AM!'+cel)

    def test_contador_pagas_nao_conta_gratuitas(self):
        rr=self.base['_FAM']['H']['aptidões anotadas'];cel=rr.rsplit('!',1)[1].replace('$','')
        v=self.cells['DADOS_AM'][cel]
        self.assertIn('1-VLOOKUP',v,'DADOS_AM!'+cel)
        self.assertEqual(v.count('1-VLOOKUP'),12)

    def test_altura_textos_compartilhada_e_limpeza(self):
        novos=[g for g in self.tabs['CONFIGURAÇÃO']['esticam'] if any(str(c).endswith(str(self.tr['registros'][0]['r']+6+23+1)) for c in g['gatilhos'])]
        for g in self.tabs['CONFIGURAÇÃO']['esticam']:
            if any(c in {r['campos']['efeito'] for r in self.tr['registros']} for c in g['gatilhos']):
                self.assertEqual(g['minima'],25);self.assertEqual(len(g['textos']),2)

    def test_fontes_saida_tem_coordenadas_reais(self):
        for g in self.tr['registros']:
            for k,cel in g['campos'].items():self.assertIn(cel,self.cells['CONFIGURAÇÃO'],(g['grupo'],g['n'],k))

    def test_menus_sem_catalogo_repetido_por_uso(self):
        p=self.tr['plano']
        self.assertEqual(len(p.tabelas),3)
        self.assertEqual(len(self.tr['registros']),30)
        self.assertEqual(len(self.tr['contrato'].fontes['forma']),10)

    def test_colisoes_de_exportacao_rejeitadas(self):
        with self.assertRaises(ValueError):exportar(self.tr['plano'],lambda *args:'a mesma chave')

    def test_aplicacao_repetida_recusada(self):
        from b47_personagem.consumidores import aplicar
        with self.assertRaisesRegex(ValueError,'já existe'):
            aplicar(self.layout,self.tr['plano'],self.tr['catalogos'],self.base['_FAM'],self.base['_FIV'],self.tr['contrato'])

    def test_formulas_tamanho_medido(self):
        maiores=[];medidas={}
        for nome in self.contexto['abas'].values():
            cells=self.cells[nome]
            encoded=json.dumps(cells,ensure_ascii=False,separators=(',',':')).encode()
            maior=max(((len(v),cel) for cel,v in cells.items() if isinstance(v,str) and v.startswith('=')),default=(0,''))
            medidas[nome]=dict(celulas=len(cells),bytes_json=len(encoded),maior_formula=maior[0],celula=maior[1])
            self.assertLess(maior[0],8192,nome+'!'+maior[1])
        print('MEDIDAS '+json.dumps(medidas,ensure_ascii=False),flush=True)
        self.__class__.medidas=medidas

    def test_transporte_complementar_deriva_das_celulas(self):
        from b47_personagem.transporte import suplementos,complementos,fatiar_colunas
        out=suplementos(self.layout,self.tr)
        fragmentos=[x for x in out if x.startswith('PersonagemFormas')]
        self.assertGreater(len(fragmentos),1)
        self.assertEqual(len(out),len(complementos(out)))
        cells=self.cells[self.contexto['abas']['forma']]
        partes=fatiar_colunas(cells)
        self.assertTrue(all(tamanho<240001 for _,_,tamanho in partes))
        from openpyxl.utils import column_index_from_string
        for cel in cells:
            col=column_index_from_string(coordinate_from_string(cel)[0])
            self.assertEqual(sum(a<=col<=b for a,b,_ in partes),1,cel)
        print('TRANSPORTE '+json.dumps(partes),flush=True)


if __name__=='__main__':unittest.main(verbosity=2)
