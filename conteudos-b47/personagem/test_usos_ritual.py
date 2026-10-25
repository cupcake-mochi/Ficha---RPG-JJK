"""Regressão focal da checagem de Ritual, sem gerar a ficha inteira."""
import unittest
from types import SimpleNamespace
from openpyxl.formula import Tokenizer
from b47_personagem.fontes_livro import carregar
from b47_personagem.planilha import Plano
from b47_personagem.usos import aplicar


def emitir(verificacoes=None):
    dados=[['BA2','atr_Inteligência',None],['BB2','AB19',None],
           ['BA3','atr_Força',None],['BB3','D19',None],
           ['BA4','atr_Destreza',None],['BB4','L19',None]]
    layout={'abas':[{'nome':'DADOS','celulas':dados},
        {'nome':'DADOS_AM','colunas':319,'linhas':89,
         'celulas':[[f'IA{r}','="Requisito"',None] for r in range(2,14)]}]}
    fam={'H':{'nível':"'FICHA'!$AH$11",'refino':"'DADOS_AM'!$A$3"},
         'ROTA':"'DADOS_AM'!$A$2",'D':SimpleNamespace(T={'carta_aptidao':(233,2,13,8)}),
         'aptidoes_c':[{'nome':f'D{r}'} for r in range(100,112)],'passivas_c':[]}
    p=Plano();p.tabelas['aptidao']={'aba':'DADOS_APTIDOES','total':44,
        'nomes':"'DADOS_APTIDOES'!$O$2:$O$45",'colunas':
        dict(nome=15,identidade=24,tipo=14,ce=16,refino_minimo=20,nivel_minimo=21,escolha=23)}
    tr={'plano':p,'antes':{},'depois':{},'catalogos':{'aptidoes':{'aba':'DADOS_AM','coluna':81}}}
    ctx={'fam':fam}
    if verificacoes is not None:ctx['verificacoes']=verificacoes
    aplicar(layout,tr,carregar(),ctx)
    return tr,ctx


class TestRitual(unittest.TestCase):
    def test_todas_as_doze_vagas_consultam_rota_resolvida(self):
        tr,_=emitir()
        formulas=[v for v in tr['depois']['DADOS_AM'].values()
                  if isinstance(v,str) and '"Conferir Técnica Inata"' in v]
        self.assertEqual(len(formulas),12)
        for f in formulas:
            self.assertIn("NOT(('DADOS_AM'!$A$2=1))",f)
            self.assertNotIn('origem',f.lower())  # Não compara nomes de origem.
            Tokenizer(f)

    def test_verificacao_explicita_do_integrador_tem_precedencia(self):
        source={'tecnica_inata':'$Z$1','aprendeu_extensao':'$Z$2'}
        tr,ctx=emitir(source)
        formulas=tr['depois']['DADOS_AM'].values()
        ritual=next(f for f in formulas if isinstance(f,str) and '"Conferir Técnica Inata"' in f)
        extensao=next(f for f in formulas if isinstance(f,str) and '"Conferir aprendizado de Extensão de Domínio"' in f)
        self.assertIn('NOT($Z$1)',ritual);self.assertIn('NOT($Z$2)',extensao)
        self.assertEqual(ctx['verificacoes'],source)

    def test_demais_requisitos_continuam_emitidos(self):
        tr,_=emitir();formulas=list(tr['depois']['DADOS_AM'].values())
        self.assertTrue(any('Nível mínimo não atendido' in f for f in formulas if isinstance(f,str)))
        self.assertTrue(any('Exige Inteligência 5' in f for f in formulas if isinstance(f,str)))
        self.assertTrue(any('Conferir aprendizado de Domínio Simples' in f for f in formulas if isinstance(f,str)))


if __name__=='__main__':unittest.main()
