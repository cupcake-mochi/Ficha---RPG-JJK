"""Gera o runtime leve dos cartões R53; não há editor visível separado."""
import json
from pathlib import Path
from cartoes_diretos import aplica,configuracao

def escrever(tr,destino):
    raiz=Path(__file__).resolve().parents[1]
    fonte=(raiz/'r53/runtime_direto.gs').read_text()
    Path(destino).write_text('var R53_EDITOR_ = '+json.dumps(configuracao(tr),ensure_ascii=False,separators=(',',':'))+';\n'+fonte)
