"""Esclarecimentos da R60/R61 sobre a base R53, conferidos no livro R63 (8e7e83bb)."""

# catalogo--melhoria-reacao e fundamento--conjurar
REACAO = ("Fora do seu turno, esta conjuração fica fora do limite de feitiços do próprio turno. "
          "Durante ele, vale o limite de um feitiço de Classe 1 ou maior, salvo exceção expressa.")

# origens--restricao-prenuncio
PRENUNCIO_TRECHO = "o anúncio a cancela, sem gastar a Reação dele."
PRENUNCIO = "Os custos que ele já tenha pago ao declarar essa Reação, como PE, não voltam."

# R66 (registros R66-05 a R66-12, motivo "frequência aprovada por cena"): cinco habilidades passam de "uma vez por
# combate" para "uma vez por cena". A troca é uma regra do R66, não redação; a carta da FICHA segue o R66 desde
# 12/11/2026 (r53/diagnostico-android/CORRECAO-FREQUENCIA-CENA-2026-11-12.md). Cada frase aparece uma vez na carta.
FREQUENCIA_POR_CENA = {
    ("caminhos", "Evocador", "30"): [
        ("Ação Completa · Uma vez por combate · Participantes a até 18 m.",
         "Ação Completa · Uma vez por cena · Participantes a até 18 m."),
        ("Marque o uso da habilidade no combate.", "Marque o uso da habilidade na cena."),
    ],
    ("trilhas", "Parceria", "27"): [
        ("Reação de quem executa · Uma vez por combate · Turno de outra criatura · Invocação a até 18 m.",
         "Reação de quem executa · Uma vez por cena · Turno de outra criatura · Invocação a até 18 m."),
        ("quando a resposta começar e marque o uso da habilidade no combate.",
         "quando a resposta começar e marque o uso da habilidade na cena."),
        ("O uso por combate pertence ao conjunto, mesmo que a beneficiária seja substituída.",
         "O uso por cena pertence ao conjunto, mesmo que a beneficiária seja substituída."),
    ],
    ("caminhos", "Incursor", "30"): [
        ("Uma vez por combate, pode ativar imediatamente antes de outra criatura começar um turno.",
         "Uma vez por cena, pode ativar imediatamente antes de outra criatura começar um turno."),
    ],
    ("trilhas", "Assassino", "27"): [
        ("Uma vez por combate, ao utilizar Golpe Cirúrgico, pode transformar aquele golpe em uma Sentença Final.",
         "Uma vez por cena, ao utilizar Golpe Cirúrgico, pode transformar aquele golpe em uma Sentença Final."),
    ],
    ("trilhas", "Malabarista", "27"): [
        ("Uma vez por combate · Fluidez e 12 PE.", "Uma vez por cena · Fluidez e 12 PE."),
    ],
}
