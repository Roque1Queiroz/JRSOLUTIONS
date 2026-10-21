# -*- coding: utf-8 -*-
"""Código curto do cliente, por empresa. Não é o id interno."""


def formatar_codigo(codigo):
    if codigo is None:
        return ''
    return '{:02d}'.format(int(codigo))


def proximo_codigo(ultimo):
    return (ultimo or 0) + 1
