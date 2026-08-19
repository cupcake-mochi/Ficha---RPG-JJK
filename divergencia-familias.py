# -*- coding: utf-8 -*-
"""A ficha e o manual discordam sobre as nove Familias.
Le os dois lados do repositorio; nenhum nome esta escrito aqui."""
import re, json
R = 'repos/JJK---Project-main/'
manual = re.findall(r"\['([^']+)', '[^']*'\]",
    re.search(r"H2\('Famílias'\).*?\n\s*\),", open(R+'manual/gerador/partB.js', encoding='utf-8').read(), re.S).group(0))
ficha = re.findall(r"'([^']+)'",
    re.search(r"const FAMILIAS = \[(.*?)\];", open(R+'sistema/05-material/gerador-ficha/dados.js', encoding='utf-8').read(), re.S).group(1))
manual = [f for f in manual if f != 'Família']   # o cabecalho da tabela nao e uma Familia
print(f"manual/gerador/partB.js       ({len(manual)}): {' · '.join(manual)}")
print(f"gerador-ficha/dados.js        ({len(ficha)}): {' · '.join(ficha)}")
print()
so_manual, so_ficha = [f for f in manual if f not in ficha], [f for f in ficha if f not in manual]
print(f"  so no manual, a ficha nao tem : {' · '.join(so_manual)}")
print(f"  so na ficha, o manual nao tem : {' · '.join(so_ficha)}")
print(f"  coincidem                     : {' · '.join(f for f in manual if f in ficha)}")
print()
MEL = json.load(open('catalogo-projeto-m.json', encoding='utf-8'))['melhorias']
orfas = [m for m, v in MEL.items() if v['familia'] in so_manual]
print(f"Consequencia: {len(orfas)} das {len(MEL)} Melhorias sao de Familia que a ficha nao imprime.")
for fam in so_manual:
    ms = [m for m, v in MEL.items() if v['familia'] == fam]
    print(f"   {fam:10} {len(ms):2} Melhorias: {', '.join(ms)}")
print()
print(f"E as {len(so_ficha)} Familias que so a ficha tem nao tem Melhoria nenhuma: {' · '.join(so_ficha)}")
