from ngcsimlib.context.contextObj import ContextObj
from ngcsimlib.context.contextObjectDecorators import component

@component
class Component(ContextObj):
    def __init__(self, name):
        super().__init__(name)
