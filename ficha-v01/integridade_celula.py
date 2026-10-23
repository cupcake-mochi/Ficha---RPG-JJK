"""Recusa perdas silenciosas de texto na passagem pelo Workbook."""


def atribuir(celula, valor, matriz=None):
    from openpyxl.worksheet.formula import ArrayFormula
    # check_string do openpyxl corta textos longos antes de emitir um erro.
    # Recusar ANTES de atribuir protege também descrições e outros textos.
    if isinstance(valor, str) and len(valor) > 32767:
        raise ValueError(f'{celula.parent.title}!{celula.coordinate}: '
                         f'{len(valor)} caracteres excedem o limite de integridade '
                         'do Workbook (32767); nenhuma truncagem é permitida')
    celula.value = ArrayFormula(matriz, valor) if matriz else valor
    obtido = celula.value.text if matriz else celula.value
    if obtido != valor:
        raise ValueError(f'{celula.parent.title}!{celula.coordinate}: '
                         'o Workbook alterou o conteúdo durante a atribuição')
