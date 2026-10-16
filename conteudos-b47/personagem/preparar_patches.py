"""Produz patches revisáveis em patches/, sem escrever no núcleo."""
import difflib
from pathlib import Path
import subprocess

AREA=Path(__file__).resolve().parent
ROOT=AREA.parents[1]
BASE='ae16895967d23044f558f31638df23c0fbdd7598'


def fonte(path):
    return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT).decode('utf8')


def trocar(texto,antes,depois):
    if texto.count(antes)!=1:raise ValueError('Âncora mudou ou não é única: '+antes[:100])
    return texto.replace(antes,depois)


def diff(path,antes,depois):
    return ''.join(difflib.unified_diff(antes.splitlines(True),depois.splitlines(True),
                    fromfile='a/'+path,tofile='b/'+path))


def preparar():
    orig=fonte('ficha-v01/monta.py')
    hook="""# Frente de personagem C+D: módulos isolados e contexto fornecido pelo integrador.
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'conteudos-b47', 'personagem'))
import b47_personagem
_PCD_CONTRATO = json.load(open(os.path.join(os.path.dirname(AQUI), 'conteudos-b47', 'comum', 'contrato.json'), encoding='utf-8'))
_PERSONAGEM = b47_personagem.aplica(LAYOUT, dict(
    fam=_FAM, inv=_FIV, criacao=_CRIACAO, pecas=_PECAS,
    capacidades=_PCD_CONTRATO['capacidades'],
    inicio=indice_ficha._aba(LAYOUT, 'CONFIGURAÇÃO')['linhas']+4,
    abas={'forma':'DADOS_FORMAS','aptidao':'DADOS_APTIDOES','talento':'DADOS_TALENTOS'},
    chave_aviso_uso=lambda grupo,n: f'aviso.personagem.{grupo}.{n}'))
"""
    etapa1=trocar(orig,"_PECAS = custom_pecas.aplica(LAYOUT, _FAM, _FIV, _CRIACAO)\n",
        "_PECAS = custom_pecas.aplica(LAYOUT, _FAM, _FIV, _CRIACAO)\n"+hook)
    anchor='print(f"a CONFIGURAÇÃO: {configuracao.QUANTIDADE} efeitos, {len(_CFG[\'alvos\'])} caixas, paleta fixa")'
    merge="""for _name, _values in _PERSONAGEM['antes'].items():
    for _coord, _value in _values.items():
        _PROG['antes'].setdefault(_name, {}).setdefault(_coord, _value)
for _name, _values in _PERSONAGEM['depois'].items():
    _PROG['depois'].setdefault(_name, {}).update(_values)
"""
    etapa1=trocar(etapa1,anchor,merge+anchor)
    etapa1=trocar(etapa1,"_AN['linhas'].extend(custom_pecas.exporta(_PECAS))\n",
        "_AN['linhas'].extend(custom_pecas.exporta(_PECAS))\n"
        "_AN_FIM_PECAS = len(_AN['linhas'])+1\n"
        "_AN['linhas'].extend(b47_personagem.exporta(_PERSONAGEM))\n"
        "_PERSONAGEM['analise_inicio'] = _AN_FIM_PECAS+1\n"
        "_PERSONAGEM['analise_fim'] = len(_AN['linhas'])+1\n")
    # O transporte só é incorporado depois de revisar as reservas de nomes.
    etapa2=trocar(etapa1,"gs, celulas, pecas = emitir_gs.escrever(\n",
        "from b47_personagem import transporte as _PCD_TRANSPORTE\n"
        "_PCD_SUPLEMENTOS = _PCD_TRANSPORTE.suplementos(LAYOUT, _PERSONAGEM)\n"
        "emitir_gs.SEPARADAS.update(_PCD_TRANSPORTE.separadas(_PERSONAGEM))\n"
        "emitir_gs.COMPLEMENTOS.update(_PCD_TRANSPORTE.complementos(_PCD_SUPLEMENTOS))\n"
        "gs, celulas, pecas = emitir_gs.escrever(\n")
    etapa2=trocar(etapa2,'suplementos={"Origens.gs":', 'suplementos={**_PCD_SUPLEMENTOS, "Origens.gs":')
    etapa2=trocar(etapa2,"first,min(first+2999,len(_AN['linhas'])+1)", "first,min(first+2999,_AN_FIM_PECAS)")
    etapa2=trocar(etapa2,"range(_AN_FIM_CRIACAO+1,len(_AN['linhas'])+2,3000)", "range(_AN_FIM_CRIACAO+1,_AN_FIM_PECAS+1,3000)")
    js=fonte('ficha/modelo.gs.js')
    js2=trocar(js,'if (/^PecasAnalise\\d+\\.gs$/.test(arq)) {',
        'if (/^(?:PecasAnalise\\d+|PersonagemFormas\\d+|PersonagemPainel|PersonagemAnalise)\\.gs$/.test(arq)) {')
    anchor='if (typeof ABAS_DAS_RESTRICOES !== \'undefined\' && ABAS_DAS_RESTRICOES) juntarAbas_(ABAS_DAS_RESTRICOES);'
    linhas=anchor+"""
if (typeof ABAS_PERSONAGEM_FORMAS !== 'undefined' && ABAS_PERSONAGEM_FORMAS) juntarAbas_(ABAS_PERSONAGEM_FORMAS);
if (typeof ABAS_PERSONAGEM_APTIDOES !== 'undefined' && ABAS_PERSONAGEM_APTIDOES) juntarAbas_(ABAS_PERSONAGEM_APTIDOES);
if (typeof ABAS_PERSONAGEM_TALENTOS !== 'undefined' && ABAS_PERSONAGEM_TALENTOS) juntarAbas_(ABAS_PERSONAGEM_TALENTOS);"""
    js2=trocar(js2,anchor,linhas)
    js2=trocar(js2,"'DADOS_RESTRICOES', 'ANALISE',","'DADOS_RESTRICOES', 'DADOS_FORMAS', 'DADOS_APTIDOES', 'DADOS_TALENTOS', 'ANALISE',")
    anchor='  Object.keys(COMPLEMENTOS_ESPERADOS_).forEach(function (arq) {'
    guarda="""  [
    ['ABAS_PERSONAGEM_FORMAS', 'FormasPersonagem.gs'],
    ['ABAS_PERSONAGEM_APTIDOES', 'AptidoesPersonagem.gs'],
    ['ABAS_PERSONAGEM_TALENTOS', 'TalentosPersonagem.gs']
  ].forEach(function (item) {
    if (!globais_()[item[0]]) throw new Error('Falta o ' + item[1] + ': cole todos os arquivos antes de construir.');
  });
"""
    # Esta âncora só existe uma vez dentro de construir, além da função de
    # junção inicial com indentação diferente.
    pos=js2.index(anchor,js2.index("if (typeof VALORES_PECAS_ === 'undefined'"))
    js2=js2[:pos]+guarda+js2[pos:]
    old="""  if (SOBRAS_.length) throw new Error('Apague do projeto os arquivos de geração anterior: ' + SOBRAS_.join(', ') + '. Nada foi alterado.');"""
    guard_old="""  Object.keys(globais_()).forEach(function (nome) {
    if (!/^VALORES_PERSONAGEM_FORMAS_\\d+_$/.test(nome)) return;
    var esperado = Object.keys(COMPLEMENTOS_ESPERADOS_).some(function (arq) { return COMPLEMENTOS_ESPERADOS_[arq] === nome; });
    if (!esperado && globais_()[nome]) registrarSobra_({arquivo:'PersonagemFormas' + nome.match(/\\d+/)[0] + '.gs'});
  });
"""
    js2=trocar(js2,old,guard_old+old)
    pasta=AREA/'patches';pasta.mkdir(exist_ok=True)
    (pasta/'01-incorporacao.patch').write_text(diff('ficha-v01/monta.py',orig,etapa1),encoding='utf8',newline='\n')
    (pasta/'02-transporte.patch').write_text(diff('ficha-v01/monta.py',etapa1,etapa2)+diff('ficha/modelo.gs.js',js,js2),encoding='utf8',newline='\n')
    leitor=fonte('ler-analise.py')
    literal_cd='''        literal_cd = bool(re.fullmatch(r"custom\\.(?:forma|aptidao|talento)\\.\\d+\\.(?:tipo|base|familia|resolucao|restricao_embutida|alcance_.*|area_.*|escolha|rota)", str(l[0])))
'''
    leitor2=trocar(leitor,'        texto = l[0] in ',literal_cd+'        texto = literal_cd or l[0] in ')
    leitor2=trocar(leitor2,'(IFS|SWITCH|TEXTJOIN)\\(', '(IFS|SWITCH|TEXTJOIN|LET)\\(')
    leitor2=trocar(leitor2,'("aviso.efeito.", "aviso.efeito_caixa.", "aviso.custom.")',
        '("aviso.efeito.", "aviso.efeito_caixa.", "aviso.custom.", "aviso.personagem.aptidao.", "aviso.personagem.talento.")')
    (pasta/'03-leitor.patch').write_text(diff('ler-analise.py',leitor,leitor2),encoding='utf8',newline='\n')
    return etapa2,js2


if __name__=='__main__':
    preparar()
    print('Três patches preparados na área de entrega. Nenhum patch aplicado ao núcleo.')
