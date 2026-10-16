"""Oráculos focais independentes de Calc; não provam recálculo nativo."""
import unittest
from copy import deepcopy
from b47_personagem.fontes_livro import carregar, FAIXAS
from b47_personagem.motor import compilar, forma, aptidoes, talentos, Contexto, menu, subir

CAP={'forma':10,'aptidao':10,'talento':10}


def nova_forma(nome='Nova *?~',**kw):
    raw=dict(tipo='Forma',nome=nome,peso=1,resolucao='TR, metade',resultado=0,
             exige_tr=True,classe_0=False,alcance_escada='alcance',area_escada='raio')
    for c,faixas in FAIXAS.items():
        for f in faixas:
            raw[f'alcance_{c}_{f}']='18 m'
            raw[f'area_{c}_{f}']='3 m'
    raw.update(kw)
    return raw


class TestMotor(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.livro=carregar()

    def cat(self,**raw): return compilar(self.livro,raw,CAP)

    def test_vazios_e_defaults_nao_cobram(self):
        c=self.cat(forma=[dict(tipo='Forma',mestre_viu=False)],talento=[dict(tipo='Talento')])
        self.assertTrue(all(not any(v) for v in c.avisos.values()))
        self.assertEqual(len(c.pools['forma']),10)

    def test_parcial_preservado_e_exportavel(self):
        c=self.cat(forma=[dict(efeito='Texto sem nome')])
        self.assertIn('NOME precisa ser texto sem espaços nas pontas',c.avisos['forma'][0])
        self.assertEqual(c.crus['forma'][0]['efeito'],'Texto sem nome')

    def test_primeira_ultima_compartilhadas(self):
        c=self.cat(forma=[nova_forma('Primeira')]+[{}]*8+[nova_forma('Última')])
        self.assertFalse(c.avisos['forma'][0]);self.assertFalse(c.avisos['forma'][9])
        for n in ('Primeira','Última'):
            self.assertIn(n,menu(c,'forma'));self.assertIn(n,menu(c,'forma',familias_abertas=[]))

    def test_primeira_ultima_aptidao_talento(self):
        for grupo,base in [('aptidao','Projetar Energia'),('talento','Leitura')]:
            c=self.cat(**{grupo:[dict(nome='Primeira *?~',base=base)]+[{}]*8+[dict(nome='Última *?~',base=base)]})
            self.assertFalse(c.avisos[grupo][0]);self.assertFalse(c.avisos[grupo][9])
            self.assertIn('Última *?~',menu(c,grupo,Contexto(escolhas=2,espacos=2)))

    def test_todas_bases_aptidoes_e_talentos(self):
        for grupo in ('aptidao','talento'):
            for base in self.livro[grupo]:
                c=self.cat(**{grupo:[dict(nome='Alias *?~',base=base['nome'])]})
                self.assertFalse(c.avisos[grupo][0],(grupo,base['nome'],c.avisos[grupo][0]))
                got=c.obter(grupo,'Alias *?~')
                for campo in ('efeito','requisitos','identidade','ce'):
                    self.assertEqual(got[campo],base[campo],(grupo,base['nome'],campo))

    def test_duplicatas_e_limpeza_aptidao_talento(self):
        for grupo,base in [('aptidao','Projetar Energia'),('talento','Leitura')]:
            c=self.cat(**{grupo:[dict(nome='Literal *?~',base=base),dict(nome='literal *?~',base=base)]})
            self.assertTrue(c.avisos[grupo][0]);self.assertTrue(c.avisos[grupo][1])
            self.assertIsNone(c.obter(grupo,'Literal *?~'))
            limpo=self.cat(**{grupo:[{},{}]})
            self.assertFalse(limpo.avisos[grupo][0]);self.assertIsNone(limpo.obter(grupo,'Literal *?~'))

    def test_comprimento_sem_base_usa_alcance_e_area(self):
        c=self.cat(forma=[nova_forma(area_escada='comprimento',area_entidade_classes_1_a_5='4,5 m')])
        self.assertEqual(forma(c,'Nova *?~','entidade',3,longe=1)['componentes'][1],' · área 9 m')

    def test_restricao_custom_embutida_reutilizavel(self):
        rs={'Assinatura?':dict(nome='Assinatura',rotulo='Assinatura?',devolve=1,frequencia=0)}
        c=compilar(self.livro,{'forma':[dict(nome='Contato',base='Toque',restricao_embutida='Assinatura?')]},CAP,restricoes=rs)
        for ctx in FAIXAS:
            self.assertEqual(forma(c,'Contato',ctx,3,melhorias=2)['utilizada'],2)

    def test_base_todas_formas_preserva_tabelas_reais(self):
        import ficha_amaldicoada as fa
        import ficha_invocacoes as iv
        regras={'personagem':fa.regras(),'entidade':iv.regras()}
        for item in self.livro['forma']:
            c=self.cat(forma=[dict(nome='Alias '+item['nome'],base=item['nome'])])
            self.assertFalse(c.avisos['forma'][0],(item['nome'],c.avisos['forma'][0]))
            for ctx,faixas in FAIXAS.items():
                for classe in range(8):
                    faixa=0 if classe==0 else 1 if classe<=5 else 2 if ctx=='personagem' or classe==6 else 3
                    for degrau in range(6):
                        got=forma(c,'Alias '+item['nome'],ctx,classe,longe=degrau,maior=degrau)
                        linhas=[x for x in regras[ctx]['alcance'] if x[0].startswith(item['nome']+' · ')]
                        g1=item['partes'][0]['grau']
                        g2=item['partes'][1]['grau'] if len(item['partes'])>1 else 0
                        graus=lambda g:min(5,(0,degrau,degrau,2*degrau)[g])
                        exp=linhas[faixa][1+graus(g1)]+linhas[faixa][7+graus(g2)]
                        # A tabela canônica capitaliza só a primeira parte.
                        obt=got['alcance'];obt=obt[:1].upper()+obt[1:]
                        self.assertEqual(obt,exp,(item['nome'],ctx,classe,degrau))

    def test_entidade_classe6_area_mantem_faixa_propria(self):
        c=self.cat(forma=[dict(nome='Estouro',base='Explosão')])
        self.assertEqual(forma(c,'Estouro','personagem',6)['alcance'],'raio 4,5 m, a 36 m')
        self.assertEqual(forma(c,'Estouro','entidade',6)['alcance'],'raio 3 m, a 36 m')
        self.assertEqual(forma(c,'Estouro','entidade',7)['alcance'],'raio 4,5 m, a 36 m')

    def test_alcance_area_independentes(self):
        c=self.cat(forma=[nova_forma()])
        self.assertEqual(forma(c,'Nova *?~','personagem',3,longe=1)['alcance'],'36 m · área 3 m')
        self.assertEqual(forma(c,'Nova *?~','entidade',3,maior=1)['alcance'],'18 m · área 4,5 m')

    def test_base_de_um_componente_aceita_outra_dimensao(self):
        raw=dict(nome='Projétil com área',base='Projétil',area_escada='raio')
        for c,fs in FAIXAS.items():
            for f in fs:raw[f'area_{c}_{f}']='3 m'
        c=self.cat(forma=[raw])
        self.assertFalse(c.avisos['forma'][0])
        self.assertEqual(forma(c,'Projétil com área','entidade',3,maior=1)['alcance'],'18 m, um alvo · área 4,5 m')

    def test_selecao_case_insensitive_literais(self):
        c=self.cat(forma=[dict(nome='Literal *?~',base='Toque')])
        self.assertFalse(forma(c,'literal *?~','entidade',1)['avisos'])

    def test_sem_base_nao_herda_identidade(self):
        c=self.cat(forma=[nova_forma()])
        self.assertEqual(c.obter('forma','Nova *?~')['identidade'],'')

    def test_sem_base_nao_concede_classe0(self):
        c=self.cat(forma=[nova_forma()])
        self.assertNotIn('Nova *?~',menu(c,'forma',classe=0))
        self.assertTrue(forma(c,'Nova *?~','entidade',0)['avisos'])

    def test_zero_nao_false_sao_explicitos(self):
        c=self.cat(forma=[dict(nome='Nova',base='Explosão',peso=0,resultado=0,exige_tr=False,classe_0=False)])
        f=c.obter('forma','Nova')
        self.assertFalse(f['exige_tr']);self.assertFalse(f['classe_0']);self.assertEqual(f['peso'],0)

    def test_familia_nenhuma_remove_heranca(self):
        c=self.cat(forma=[dict(nome='Área sem família',base='Explosão',familia='Nenhuma')])
        self.assertIn('Área sem família',menu(c,'forma',familias_abertas=[]))

    def test_familia_custom_aberta_por_entidade(self):
        c=compilar(self.livro,{'forma':[nova_forma(familia='Eco?*~')]},CAP,familias=['Eco?*~'])
        self.assertIn('Nova *?~',menu(c,'forma',familias_abertas=['Eco?*~']))
        self.assertNotIn('Nova *?~',menu(c,'forma',familias_abertas=['Outra']))

    def test_forma_livre_desconto_so_personagem(self):
        c=self.cat(forma=[dict(nome='Nova',base='Cura')])
        self.assertEqual(forma(c,'Nova','personagem',3,livre=True)['custo'],1)
        self.assertEqual(forma(c,'Nova','entidade',3,livre=True)['custo'],3)

    def test_embutida_nao_paga_forma(self):
        c=self.cat(forma=[dict(nome='Contato',base='Toque')])
        r=forma(c,'Contato','personagem',3,melhorias=0)
        self.assertEqual((r['devolucao'],r['utilizada'],r['perdida']),(3,0,3))

    def test_embutida_leve_limites_frequencia(self):
        c=self.cat(forma=[dict(nome='Contato',base='Toque',restricao_embutida='Uma Vez')])
        r=forma(c,'Contato','entidade',3,melhorias=1,restricoes=['Condicional (Leve)','Gesto'])
        self.assertTrue(any('frequência' in x for x in r['avisos']))
        self.assertTrue(any('duas Restrições' in x for x in r['avisos']))
        self.assertEqual(r['utilizada'],1)

    def test_cone_renomeado_preserva_incompatibilidade(self):
        c=self.cat(forma=[dict(nome='Cone?*~',base='Cone')])
        self.assertTrue(any('Cone/Linha' in x for x in forma(c,'Cone?*~','entidade',3,restricoes=['Corpo a Corpo'])['avisos']))

    def test_curingas_literais_e_duplicatas(self):
        c=self.cat(forma=[dict(nome='X*?~',base='Toque'),dict(nome='Xabc',base='Toque')])
        self.assertEqual(c.obter('forma','X*?~')['nome'],'X*?~')
        c=self.cat(forma=[dict(nome='X*?~',base='Toque'),dict(nome='x*?~',base='Toque')])
        self.assertIsNone(c.obter('forma','X*?~'));self.assertTrue(c.avisos['forma'][1])

    def test_colisao_livro(self):
        c=self.cat(forma=[dict(nome='toque',base='Toque')])
        self.assertTrue(c.avisos['forma'][0]);self.assertEqual(len(c.pools['forma']),10)

    def test_tipo_incorreto_exclui(self):
        for grupo,base in [('forma','Toque'),('aptidao','Projetar Energia'),('talento','Leitura')]:
            c=self.cat(**{grupo:[dict(nome='Errado',base=base,tipo='Arma')]})
            self.assertIsNone(c.obter(grupo,'Errado'));self.assertTrue(c.avisos[grupo][0])

    def test_tipo_bencao_nao_contorna_rota_base(self):
        c=self.cat(aptidao=[dict(nome='Errado',base='Energia Reversa',tipo='Bênção')])
        self.assertTrue(c.avisos['aptidao'][0])

    def test_capacidade_rejeita_excesso(self):
        with self.assertRaisesRegex(ValueError,'excedem'):self.cat(talento=[{}]*11)

    def test_base_invalida_sem_heranca(self):
        c=self.cat(forma=[dict(nome='Errada',base='Leitura')])
        self.assertIsNone(c.obter('forma','Errada'))

    def test_escada_incompativel_e_tipos(self):
        for change in [dict(area_escada='alcance'),dict(area_personagem_classes_1_a_5='muito'),dict(peso=True),dict(classe_0='Não')]:
            c=self.cat(forma=[nova_forma(**change)])
            self.assertTrue(c.avisos['forma'][0],change)

    def test_escada_cone_entre_degraus_satura(self):
        self.assertEqual(subir(self.livro['escadas']['comprimento'],'3 m',1),'4,5 m')
        self.assertEqual(subir(self.livro['escadas']['raio'],'3 m',99),'15 m')

    def test_ce_ausente_consumo_explicito(self):
        c=self.cat(aptidao=[dict(nome='Paga',tipo='Aptidão'),dict(nome='Livre',tipo='Aptidão',escolha='Gratuita')])
        r=aptidoes(c,['Paga','Livre'],Contexto(escolhas=1))
        self.assertEqual(r['consumo'],1);self.assertFalse(r['avisos'])

    def test_gratuidade_herdada_explicitamente_alteravel(self):
        c=self.cat(aptidao=[dict(nome='Cobertura',base='Cobrir-se de Energia'),dict(nome='Cobertura paga',base='Cobrir-se de Energia',escolha='Consome uma escolha')])
        self.assertIn('Cobertura',menu(c,'aptidao',Contexto()))
        self.assertEqual(aptidoes(c,['Cobertura'],Contexto())['consumo'],0)
        self.assertEqual(aptidoes(c,['Cobertura paga'],Contexto(escolhas=1))['consumo'],1)

    def test_aptidao_ce_nao_adiciona_nivel_oculto(self):
        c=self.cat(aptidao=[dict(nome='Livre CE3',tipo='Aptidão',ce=3)])
        self.assertFalse(aptidoes(c,['Livre CE3'],Contexto(escolhas=1))['avisos'])

    def test_bencao_usa_lapidacao_sem_nivel_talento(self):
        c=self.cat(aptidao=[dict(nome='Bênção nova',tipo='Bênção',ce=2)])
        self.assertFalse(aptidoes(c,['Bênção nova'],Contexto(rota=4,refino=4,escolhas=1,nivel=1))['avisos'])
        self.assertTrue(aptidoes(c,['Bênção nova'],Contexto(rota=4,refino=3,escolhas=1))['avisos'])

    def test_bencao_ce_nunca_gratuita_sozinha(self):
        c=self.cat(aptidao=[dict(nome='Bênção nova',tipo='Bênção')])
        self.assertEqual(aptidoes(c,['Bênção nova'],Contexto(rota=4))['consumo'],1)
        self.assertTrue(aptidoes(c,['Bênção nova'],Contexto(rota=4))['avisos'])

    def test_rota_e_extensao_preservadas(self):
        c=self.cat(aptidao=[dict(nome='Extensão*',base='Extensão de Domínio')])
        self.assertNotIn('Extensão*',menu(c,'aptidao',Contexto(origem='Corpo Amaldiçoado')))
        self.assertNotIn('Energia Reversa',menu(c,'aptidao',Contexto(rota=4)))

    def test_cadeia_aquisicao_na_ordem(self):
        c=self.cat(aptidao=[dict(nome='Reversa?',base='Energia Reversa'),dict(nome='Circulação*',base='Circulação')])
        ctx=Contexto(nivel=14,refino=8,escolhas=2)
        self.assertFalse(aptidoes(c,['Reversa?','Circulação*'],ctx)['avisos'])
        self.assertTrue(any('anterior' in x for x in aptidoes(c,['Circulação*','Reversa?'],ctx)['avisos']))

    def test_alias_base_nao_duplica_aptidao(self):
        c=self.cat(aptidao=[dict(nome='Reversa?',base='Energia Reversa')])
        r=aptidoes(c,['Energia Reversa','Reversa?'],Contexto(nivel=14,refino=7,escolhas=2))
        self.assertTrue(any('repetida' in x for x in r['avisos']))

    def test_propria_uma_vez_entre_categorias(self):
        c=self.cat()
        r=aptidoes(c,['Aptidão Própria (CE 1)','Aptidão Própria (CE 2)'],Contexto(escolhas=2))
        self.assertTrue(any('repetida' in x for x in r['avisos']))

    def test_dom_simples_voto_e_aprendizado(self):
        c=self.cat(aptidao=[dict(nome='Círculo',base='Domínio Simples')])
        ctx=Contexto(refino=4,escolhas=1,voto_iniciante=True,aprendizado=frozenset(['Domínio Simples']))
        self.assertFalse(aptidoes(c,['Círculo'],ctx)['avisos'])
        ctx.aprendizado=frozenset();self.assertTrue(aptidoes(c,['Círculo'],ctx)['avisos'])

    def test_concessao_nomeada_preserva_excecao(self):
        c=self.cat(aptidao=[dict(nome='Reversa própria',base='Energia Reversa')])
        ctx=Contexto(escolhas=1,concessoes=frozenset(['Energia Reversa']))
        self.assertFalse(aptidoes(c,['Reversa própria'],ctx)['avisos'])

    def test_atributos_bencao(self):
        c=self.cat()
        ctx=Contexto(rota=4,refino=4,escolhas=1,atributos={'Destreza':3})
        self.assertTrue(any('Destreza' in x for x in aptidoes(c,['Ímpeto'],ctx)['avisos']))

    def test_talento_custo_ce_nivel_leque(self):
        c=self.cat(talento=[dict(nome='Reserva?',base='Reserva Profunda')])
        r=talentos(c,['Reserva?'],['Leitura'],Contexto(nivel=13,espacos=3,leques=1))
        self.assertEqual(r['custo'],3);self.assertFalse(r['avisos'])
        self.assertTrue(talentos(c,['Reserva?'],['Leitura'],Contexto(nivel=12,espacos=2,leques=0))['avisos'])

    def test_talento_sem_base_requisitos_literais(self):
        c=self.cat(talento=[dict(nome='Livre',ce=1,requisitos='Nível 30; =1+1',efeito='Ganhe +999')])
        r=talentos(c,['Livre'],[],Contexto(espacos=1))
        self.assertFalse(r['avisos']);self.assertEqual(r['custo'],1)
        self.assertEqual(r['cartas'][0]['efeito'],'Ganhe +999')

    def test_talento_rotas(self):
        c=self.cat(talento=[dict(nome='Instinto+',base='Instinto')])
        self.assertNotIn('Instinto+',menu(c,'talento',Contexto(rota=3)))
        self.assertIn('Instinto+',menu(c,'talento',Contexto(rota=2)))

    def test_talento_maximo_cinco(self):
        self.assertTrue(any('cinco' in x for x in talentos(self.cat(),['Leitura']*6,[],Contexto(espacos=30))['avisos']))

    def test_limpeza_e_reutilizacao_nao_mutam_dados(self):
        raw={'forma':[nova_forma()]};antes=deepcopy(raw)
        c=compilar(self.livro,raw,CAP)
        for _ in range(12):forma(c,'Nova *?~','entidade',6)
        self.assertEqual(raw,antes)
        self.assertNotIn('Nova *?~',menu(self.cat(),'forma'))


if __name__=='__main__':unittest.main(verbosity=2)
