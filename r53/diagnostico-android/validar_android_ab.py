"""Valida a releitura nativa da cópia otimizada; nenhuma chamada de rede."""
import json
from pathlib import Path

from preparar_android_ab import PRIVATE, TARGET, cells, digest
from revisar import normalized


def main():
    before, after = {}, {}
    for start in range(1, 251, 25):
        for prefix, dest in [('antes', before), ('final', after)]:
            doc = json.loads((PRIVATE/f'{prefix}-{start}.json').read_text())
            assert doc['spreadsheetId'] == TARGET
            dest.update(cells(doc))
    expected = json.loads((PRIVATE/'esperado.json').read_text())
    assert before.keys() == after.keys()
    native = {}
    for address in before:
        old, new = before[address], after[address]
        if address in expected:
            f = new['userEnteredValue']['formulaValue']
            assert normalized(f) == normalized(expected[address]), address
            native[address] = f
            assert 'errorValue' not in new.get('effectiveValue', {}), address
            assert {k: v for k, v in old.items() if k != 'userEnteredValue'} == {k: v for k, v in new.items() if k != 'userEnteredValue'}, address
        else:
            assert old == new, address
    original_meta = json.loads((PRIVATE/'otimizada-metadados.json').read_text())['metadata']
    final_meta = json.loads((PRIVATE/'metadados-depois.json').read_text())
    assert original_meta['sheets'] == final_meta['sheets']
    a = json.loads((PRIVATE/'sentinelas-0-antes.json').read_text())
    b = json.loads((PRIVATE/'sentinelas-1-antes.json').read_text())
    final = json.loads((PRIVATE/'sentinelas-final.json').read_text())
    assert a['sheets'] == b['sheets'] == final['sheets']
    manifest = json.loads((PRIVATE/'manifesto.json').read_text())
    old_bytes = manifest['bytes_antes']
    new_bytes = sum(len(f.encode()) for f in native.values())
    saved = old_bytes-new_bytes
    result = dict(controle=manifest['controle'], otimizada=TARGET,
        intervalo=manifest['range'], formulas_conferidas=len(native),
        resultados_atuais_iguais=True, erros_novos_no_intervalo=0,
        formatos_e_validacoes_do_intervalo_preservados=True,
        estrutura_27_abas_e_condicionais_preservadas=True,
        sentinelas_financeiras_e_recursos_iguais=True,
        bytes_fd_antes=old_bytes, bytes_fd_depois=new_bytes,
        bytes_reduzidos=saved, reducao_fd_percentual=round(100*saved/old_bytes, 2),
        texto_formulas_ficha_antes=34725005,
        texto_formulas_ficha_estimado_depois=34725005-saved,
        reducao_texto_formulas_ficha_percentual=round(100*saved/34725005, 2),
        formulas_nativas_depois_sha256=digest(native),
        teste_android='pendente no aparelho afetado',
        limite='Percentual de texto UTF-8 de fórmulas, não memória/arquivo/velocidade. Total usa inventário anterior e delta exato desta única alteração.',
        acionadores='Cópias sem instalação de acionadores instaláveis; estado do script vinculado não relido nesta sessão.',
        fonte_producao='Sem alteração; experimento nativo em cópia. Gerador e correções independentes continuam pendentes.')
    Path(__file__).with_name('ANDROID-AB-2026-10-23.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
