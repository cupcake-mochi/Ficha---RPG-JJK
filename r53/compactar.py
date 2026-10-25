"""Emissão menor, sem mudar campos, referências ou regras do motor R53.

Só compartilha buscas totais protegidas por IFERROR, com chave literal ou
referência simples. Não antecipa expressões arbitrárias de ramos de IF.
"""
from collections import Counter
from formulas import X, ref, native, IF


def fatorar_sufixos(expr):
    if not isinstance(expr, X):
        return expr
    args = tuple(fatorar_sufixos(a) for a in expr.args)
    out = X(expr.op, args)
    if out.op == 'IF':
        condition, yes, no = args
        suffixes = []
        prefix = yes
        while prefix.op == '&' and prefix != no:
            suffixes.insert(0, prefix.args[1])
            prefix = prefix.args[0]
        if suffixes and prefix == no:
            suffix = suffixes[0]
            for part in suffixes[1:]:
                suffix = suffix.cat(part)
            return no.cat(IF(condition, suffix, ''))
    return out


def compartilhar_buscas(expr, refs, lookup_range, fields, separator=','):
    """Retorna vínculos LET e árvore; a emissão antiga fica se não diminuir."""
    counts = Counter()
    def visit(e):
        if not isinstance(e, X):
            return
        if e.op == 'lookup' and e.args[0].op in ('ref', 'lit'):
            counts[e] += 1
        for a in e.args:
            visit(a)
    visit(expr)
    bindings = []
    replacements = {}
    for node, count in counts.items():
        if count < 2:
            continue
        # Letras apenas: identificadores não confundem com referências A1.
        number = len(bindings)
        suffix = ''
        while True:
            suffix = chr(97 + number % 26) + suffix
            number = number // 26 - 1
            if number < 0:
                break
        name = 'busca' + suffix
        if name in refs or name in refs.values():
            raise ValueError('Identificador LET já utilizado: ' + name)
        value = native(node, refs, lookup_range, fields, separator)
        if (count - 1) * len(value) <= (count + 1) * len(name) + 2:
            continue
        bindings.append((name, node))
        replacements[node] = ref(name)
    def replace(e):
        if not isinstance(e, X):
            return e
        if e in replacements:
            return replacements[e]
        return X(e.op, tuple(replace(a) for a in e.args))
    return bindings, replace(expr)


def native_compact(expr, refs, lookup_range, fields, separator=',', suffixes=False):
    if suffixes:
        expr = fatorar_sufixos(expr)
    original = native(expr, refs, lookup_range, fields, separator)
    bindings, compact = compartilhar_buscas(expr, refs, lookup_range, fields, separator)
    if not bindings:
        return original
    local_refs = dict(refs, **{name: name for name, _ in bindings})
    args = []
    for name, node in bindings:
        args.extend((name, native(node, refs, lookup_range, fields, separator)))
    args.append(native(compact, local_refs, lookup_range, fields, separator))
    candidate = 'LET(' + separator.join(args) + ')'
    return candidate if len(candidate) < len(original) else original
