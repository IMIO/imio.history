# -*- extra stuff goes here -*-


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    from AccessControl import allow_module
    allow_module('imio.history.utils')
