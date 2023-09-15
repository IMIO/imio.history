# -*- coding: utf-8 -*-

from AccessControl import allow_module


allow_module('imio.history.utils')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
