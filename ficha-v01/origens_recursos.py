"""Regras passivas de Núcleo Dependente e habilitação de Fôlego Recuperado."""
import re
import indice_ficha as ix

PE = '=LET(peNucleo,{base},IF(OR(peNucleo="",DADOS_CONFIG!$C$3=1),peNucleo,peNucleo+DADOS_CUSTOM!$B$131))'
INTEGRIDADE = '=IF(DADOS_CUSTOM!$B$128,0,{base})'
MOVIMENTO = '=LET(movNucleo,{base},IF(DADOS_CUSTOM!$B$129,FLOOR(MAX(0,VALUE(SUBSTITUTE(movNucleo," m",""))/2),1.5)&" m",movNucleo))'
BLOQUEAR = '=IF(DADOS_CUSTOM!$B$129,"Não pode bloquear · Núcleo inativo",{base})'

def ref(idx, chave):
    r, c = ix._lc(idx[chave])
    return f"'FICHA'!${ix._letras(c)}${r}"

def helpers(idx):
    origem = ref(idx, 'origem')
    def base(nome):
        return f'OR({origem}="{nome}",AND($B$121,$B$123="{nome}"))'
    def menor(nome):
        return f'OR({ref(idx,"menor 1")}="{nome}",{ref(idx,"menor 2")}="{nome}")'
    ess, nivel = ref(idx, 'atr_Essência'), ref(idx, 'nivel')
    return {
        'B128': f'=AND({base("Corpo Amaldiçoado")},{menor("Núcleo Dependente")})',
        'B129': f'=AND($B$128,N({ref(idx,"energia")})<=0,N({ref(idx,"energia_temp")})<=0)',
        'B130': f'=AND({base("Restrição Celestial · Sem Energia")},{menor("Fôlego Recuperado")})',
        'B131': f'=IF($B$128,MAX(0,N({ess}))+MIN(7,MAX(0,INT((N({nivel})-2)/4)))*INT(MAX(0,N({ess}))/2),0)',
    }

def aplicar(celulas, idx):
    ficha = celulas['FICHA']
    for chave, molde in [('energia_max', PE), ('integridade_max', INTEGRIDADE),
                         ('deslocamento', MOVIMENTO)]:
        c = idx[chave]
        ficha[c] = molde.format(base=ficha[c][1:])
    for c, formula in list(ficha.items()):
        if formula.startswith('=IF(AND(') and '"Não pode bloquear"' in formula:
            ficha[c] = BLOQUEAR.format(base=formula[1:])
            break
    else:
        raise ValueError('Bloquear corporal não encontrado')

def anterior(formula):
    """Desembrulha só o molde exato para comparadores históricos."""
    if not isinstance(formula, str):
        return formula
    for molde in [PE, INTEGRIDADE, MOVIMENTO, BLOQUEAR]:
        p = re.escape(molde).replace(re.escape('{base}'), '(?P<base>.+)')
        m = re.fullmatch(p, formula)
        if m:
            return '=' + m['base']
    return formula
