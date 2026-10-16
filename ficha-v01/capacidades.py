"""Capacidades compartilhadas B47; posições de uso não são cadastros.

A mudança de capacidade/partição implica migração e revisão do contrato ANALISE.
"""
FAMILIAS = 10
MELHORIAS = 30
RESTRICOES = 30
PERICIAS = 10
OFICIOS = 10
CURTOS = PERICIAS + OFICIOS
INICIO_PROGRESSAO = 737
INICIO_CURTOS = INICIO_PROGRESSAO + 60
PASSO_CURTOS = 14
FIM_PROGRESSAO = INICIO_CURTOS + ((CURTOS - 1) // 2) * PASSO_CURTOS + 12
INICIO_FAMILIAS = FIM_PROGRESSAO + 4
