import ast
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import runpy
from preparar_patches import AREA,fonte,preparar
from b47_personagem.transporte import fatiar_colunas


class TestPatches(unittest.TestCase):
    def test_patches_em_copias_dentro_da_area(self):
        python,js=preparar()
        ast.parse(python)
        local=AREA/'_local';local.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='patch-check-',dir=local) as temp:
            temp=Path(temp)
            subprocess.run(['git','init','--quiet',str(temp)],check=True,capture_output=True)
            for path in ('ficha-v01/monta.py','ficha/modelo.gs.js','ler-analise.py'):
                destino=temp/path;destino.parent.mkdir(parents=True,exist_ok=True)
                destino.write_text(fonte(path),encoding='utf8',newline='\n')
            for nome in ('01-incorporacao.patch','02-transporte.patch','03-leitor.patch'):
                patch=AREA/'patches'/nome
                r=subprocess.run(['git','apply','--check',str(patch)],cwd=temp,capture_output=True,text=True)
                self.assertEqual(r.returncode,0,nome+' '+r.stderr)
                subprocess.run(['git','apply',str(patch)],cwd=temp,check=True,capture_output=True)
            self.assertEqual((temp/'ficha-v01/monta.py').read_text(encoding='utf8'),python)
            self.assertEqual((temp/'ficha/modelo.gs.js').read_text(encoding='utf8'),js)
            subprocess.run(['node','--check',str(temp/'ficha/modelo.gs.js')],check=True,capture_output=True)
            r=subprocess.run(['node',str(AREA/'teste-carregamento.js'),str(temp/'ficha/modelo.gs.js')],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            print('CARREGAMENTO '+r.stdout.strip(),flush=True)
            leitor=runpy.run_path(str(temp/'ler-analise.py'))
            ficha=leitor['de_linhas']([
                ['formato.versao','10','','cabeçalho'],
                ['custom.forma.1.alcance_personagem_classe_0','007','','configuração'],
                ['custom.forma.1.base','007','','configuração'],
                ['custom.talento.1.categoria','2','','configuração'],
                ['aviso.personagem.aptidao.1','Aquisição anterior ausente','DADOS_AM!A1','aviso']])
            self.assertEqual(ficha['custom.forma.1.alcance_personagem_classe_0']['valor'],'007')
            self.assertEqual(ficha['custom.forma.1.base']['valor'],'007')
            self.assertEqual(ficha['custom.talento.1.categoria']['valor'],2)
            self.assertEqual(leitor['relatorio'](ficha)[0],'reprovada')

    def test_fragmentos_nao_perdem_colunas(self):
        cells={f'A{r}':'a'*30 for r in range(1,31)}
        cells.update({f'B{r}':'b'*30 for r in range(1,31)})
        parts=fatiar_colunas(cells,limite=1500)
        self.assertEqual(len(parts),2)
        self.assertEqual([(p[0],p[1]) for p in parts],[(1,1),(2,2)])
        self.assertTrue(all(p[2]<=1500 for p in parts))

    def test_coluna_grande_recusada_sem_corte_silencioso(self):
        with self.assertRaisesRegex(ValueError,'coluna excede'):
            fatiar_colunas({'A1':'x'*2000},1000)


if __name__=='__main__':unittest.main(verbosity=2)
