"""Bônus passivos de Reserva Excedente e Bolsa Orgânica, sem alterar saldos."""
import re
import indice_ficha as ix
from origens_recursos import ref

PE = '=LET(peOrigem,{base},IF(OR(peOrigem="",DADOS_CONFIG!$C$3=1),peOrigem,peOrigem+DADOS_CUSTOM!$B$132))'
CARGA = '=LET(cargaOrigem,{base},IF(OR(cargaOrigem="",DADOS_CONFIG!$C$13=1),cargaOrigem,cargaOrigem+DADOS_CUSTOM!$B$133))'
NOTA_PE = ('Reserva Excedente e Núcleo Dependente já entram automaticamente nos PE máximos quando válidos. '
           'Use este Buff somente para outros ajustes. Ao atualizar uma ficha antiga, confira as compensações '
           'manuais dessas capacidades para não aplicar o mesmo benefício duas vezes.')


def helpers(idx):
    origem = ref(idx, 'origem')
    def menor(nome):
        return f'OR({ref(idx,"menor 1")}="{nome}",{ref(idx,"menor 2")}="{nome}")'
    return {
        'B132': f'=IF(AND($B$126,{menor("Reserva Excedente")}),2*MAX(0,N({ref(idx,"atr_Essência")})),0)',
        'B133': (f'=IF(AND(OR({origem}="Híbrido",AND($B$121,$B$123="Híbrido")),'
                 f'{menor("Bolsa Orgânica")}),MAX(0,N({ref(idx,"maestria")})),0)'),
    }


def aplicar(celulas, idx, carga):
    ficha = celulas['FICHA']
    ficha[idx['energia_max']] = PE.format(base=ficha[idx['energia_max']][1:])
    celulas['DADOS'][carga] = CARGA.format(base=celulas['DADOS'][carga][1:])


def notas(layout):
    ix._aba(layout, 'FICHA')['notas'][ix.indice(layout)['buff de energia']] = NOTA_PE


def anterior(formula):
    """Comparadores históricos: retira apenas o envoltório novo exato."""
    if not isinstance(formula, str):
        return formula
    for molde in (PE, CARGA):
        m = re.fullmatch(re.escape(molde).replace(re.escape('{base}'), '(?P<base>.+)'), formula)
        if m:
            return '=' + m['base']
    return formula
