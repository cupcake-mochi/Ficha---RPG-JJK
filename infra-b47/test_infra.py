"""Fixtures pequenas, sem autenticação, rede, gerador ou Google."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch


def load(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


apps = load('apps_script')
runner = load('executar')


class InfraTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root/'fontes'
        self.src.mkdir()
        (self.src/'Codigo.gs').write_bytes('const nome = "ação";\r\n'.encode())
        self.files = [{'name': 'Codigo', 'type': 'SERVER_JS', 'source': 'anterior'},
                      {'name': 'appsscript', 'type': 'JSON', 'source': '{"timeZone":"America/Sao_Paulo"}'},
                      {'name': 'Tela', 'type': 'HTML', 'source': '<p>Olá</p>'}]
        self.snapshot = self.root/'antes.json'
        self.save_remote()

    def save_remote(self, script_id='fixture'):
        apps.gravar(self.snapshot, {'scriptId': script_id, 'files': self.files})

    def test_payload_preserva_manifesto_html_e_bytes(self):
        payload = apps.preparar(self.src, self.snapshot, 'fixture')
        self.assertEqual(payload['files'][1:], self.files[1:])
        self.assertEqual(payload['files'][0]['source'].encode(), (self.src/'Codigo.gs').read_bytes())
        self.assertEqual(apps.indice(payload['files'])[('Codigo', 'SERVER_JS')]['bytes'], (self.src/'Codigo.gs').stat().st_size)

    def test_teto_bytes_e_igualdade_limite(self):
        f = {'name': 'Grande', 'type': 'SERVER_JS', 'source': 'x'*899999}
        apps.indice([f])
        f['source'] += 'x'
        with self.assertRaises(ValueError):
            apps.indice([f])
        f['source'] = 'á'*450000
        with self.assertRaises(ValueError):
            apps.indice([f])

    def test_destino_errado(self):
        with self.assertRaises(ValueError):
            apps.preparar(self.src, self.snapshot, 'outro')

    def test_nao_apaga_script_remoto_desconhecido(self):
        self.files.append({'name': 'Helper', 'type': 'SERVER_JS', 'source': 'helper'})
        self.save_remote()
        with self.assertRaises(ValueError):
            apps.preparar(self.src, self.snapshot, 'fixture')

    def test_manifesto_obrigatorio_e_nomes_unicos(self):
        self.files = self.files[:1]
        self.save_remote()
        with self.assertRaises(ValueError):
            apps.preparar(self.src, self.snapshot, 'fixture')
        with self.assertRaises(ValueError):
            apps.indice(self.files*2)

    def test_readback_ordem_irrelevante_conteudo_exato(self):
        payload = apps.preparar(self.src, self.snapshot, 'fixture')
        path = self.root/'pacote.json'
        apps.gravar(path, payload)
        self.files = list(reversed(payload['files']))
        self.save_remote()
        self.assertTrue(apps.conferir(path, self.snapshot, 'fixture')['igual'])
        self.files[0]['source'] += ' '
        self.save_remote()
        self.assertFalse(apps.conferir(path, self.snapshot, 'fixture')['igual'])
        self.files.pop()
        self.save_remote()
        self.assertFalse(apps.conferir(path, self.snapshot, 'fixture')['igual'])

    def test_conferencia_rejeita_pacote_destinado_a_outro_projeto(self):
        payload = apps.preparar(self.src, self.snapshot, 'fixture')
        payload['scriptId'] = 'outro'
        path = self.root/'pacote.json'
        apps.gravar(path, payload)
        with self.assertRaises(ValueError):
            apps.conferir(path, self.snapshot, 'fixture')

    def test_vazio_e_symlink(self):
        (self.src/'Codigo.gs').unlink()
        with self.assertRaises(ValueError):
            apps.locais(self.src)
        (self.src/'Codigo.gs').symlink_to(self.snapshot)
        with self.assertRaises(ValueError):
            apps.locais(self.src)

    def test_runner_exit_e_timeout(self):
        for code in (0, 7):
            r = runner.run_task([sys.executable, '-c', f'print("fixture"); raise SystemExit({code})'], self.root/f'{code}.log', 5, os.environ.copy())
            self.assertEqual(r['exit_code'], code)
            self.assertEqual(r['estado'], 'executado' if code == 0 else 'falhou')
        r = runner.run_task([sys.executable, '-c', 'import time; time.sleep(10)'], self.root/'timeout.log', 0.1, os.environ.copy())
        self.assertEqual(r['estado'], 'falhou')
        self.assertLess(r['exit_code'], 0)

    def test_recibo_rejeita_modelo_corrompido_e_base_obsoleta(self):
        base = self.root/'baseline'
        base.mkdir()
        names = ('pecas-modelo.json', 'pecas-modelo-anterior.json')
        for n in names:
            (base/n).write_text('{}')
        runner.gravar(base/'recibo.json', {'fingerprint': 'atual', 'arquivos': {n: runner.hash_file(base/n) for n in names}})
        with patch.object(runner, 'OUT', self.root):
            self.assertTrue(runner.baseline_valida('atual'))
            self.assertFalse(runner.baseline_valida('outra'))
            (base/names[0]).write_text('{"alterado":true}')
            self.assertFalse(runner.baseline_valida('atual'))

    def test_recibo_json_com_estrutura_invalida_nao_interrompe_executor(self):
        base = self.root/'baseline'
        base.mkdir()
        invalidos = [None, [], 'texto', {'fingerprint': 'atual', 'arquivos': []},
                     {'fingerprint': 'atual', 'arquivos': None},
                     {'fingerprint': 'atual', 'arquivos': {'../fora.json': 'hash'}}]
        with patch.object(runner, 'OUT', self.root):
            for data in invalidos:
                with self.subTest(recibo=data):
                    runner.gravar(base/'recibo.json', data)
                    self.assertFalse(runner.baseline_valida('atual'))

    def test_cli_nao_sobrescreve_snapshot_com_pacote(self):
        anterior = self.snapshot.read_bytes()
        symbolic = self.root/'link-snapshot.json'
        symbolic.symlink_to(self.snapshot)
        hard = self.root/'hardlink-snapshot.json'
        hard.hardlink_to(self.snapshot)
        for saida in (self.snapshot, symbolic, hard):
            with self.subTest(saida=saida):
                run = subprocess.run([sys.executable, str(Path(apps.__file__)), 'preparar',
                                      '--fontes', str(self.src), '--snapshot', str(self.snapshot),
                                      '--script-id', 'fixture', '--saida', str(saida)],
                                     capture_output=True, text=True, timeout=5)
                self.assertEqual(run.returncode, 2)
                self.assertEqual(self.snapshot.read_bytes(), anterior)

    def test_cli_nao_sobrescreve_fonte_com_manifesto(self):
        fonte = self.src/'Codigo.gs'
        anterior = fonte.read_bytes()
        run = subprocess.run([sys.executable, str(Path(apps.__file__)), 'manifesto',
                              '--fontes', str(self.src), '--saida', str(fonte)],
                             capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(fonte.read_bytes(), anterior)

    def test_cli_nao_sobrescreve_pacote_com_conferencia(self):
        package = self.root/'pacote.json'
        apps.gravar(package, apps.preparar(self.src, self.snapshot, 'fixture'))
        self.files = json.loads(package.read_text())['files']
        self.save_remote()
        anterior = package.read_bytes()
        run = subprocess.run([sys.executable, str(Path(apps.__file__)), 'conferir',
                              '--pacote', str(package), '--snapshot', str(self.snapshot),
                              '--script-id', 'fixture', '--saida', str(package)],
                             capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(package.read_bytes(), anterior)

    def test_relatorio_separa_execucao_falha_impedimento(self):
        def task(code, deps=()):
            return dict(comando=[sys.executable, '-c', f'raise SystemExit({code})'],
                        escopo='fixture', ferramentas=deps, pesado=False,
                        baseline=False, entradas=[], limite='')
        tasks = {'passa': task(0), 'falha': task(9),
                 'bloqueado': task(0, ['ferramenta-fixture-inexistente-b47'])}
        args = SimpleNamespace(testes=list(tasks), permitir_pesados=False, timeout=5)
        with patch.object(runner, 'OUT', self.root), patch.object(runner, 'PYTHON', Path(sys.executable)), patch.object(runner, 'fingerprint', return_value='fixture'), patch.object(runner, 'inventario', return_value=tasks):
            self.assertEqual(runner.executar(args), 1)
        report = json.loads(next(self.root.glob('*/relatorio.json')).read_text())
        self.assertEqual([r['estado'] for r in report['resultados']], ['executado', 'falhou', 'impedido'])
        self.assertEqual([r['exit_code'] for r in report['resultados']], [0, 9, None])


if __name__ == '__main__':
    unittest.main()
