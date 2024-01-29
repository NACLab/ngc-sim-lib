from abc import ABC, abstractmethod
from NGC_Learn_Core.utils import check_attributes


class Command(ABC):
    def __init__(self, *args, required_calls=None):
        self.components = {}
        required_calls = ['name'] if required_calls is None else required_calls + ['name']
        for comp in args:
            if check_attributes(comp, required_calls, fatal=True):
                self.components[comp.name] = comp

    @abstractmethod
    def __call__(self, **kwargs):
        pass
