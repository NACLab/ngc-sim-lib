from enum import Enum


class _HelpSection:
    def __init__(self, section_path, section_tile, blank_msg, indent=1):
        self.section_path = section_path
        self.section_tile = section_tile
        self.blank_msg = blank_msg
        self.indent = indent

    def _write_section(self, data):
        _indent = "\t" * self.indent
        _indent_2 = "\t" * (self.indent + 1)
        guide = f"{_indent}{self.section_tile}:\n"

        if data is not None:
            for key, item in data.items():
                guide += f"{_indent_2}{key}: {item}\n"
        else:
            guide += f"{_indent_2}{self.blank_msg}\n"
        return guide

    def write(self, data):
        for p in self.section_path.split("/"):
            data = data.get(p, None) if data is not None else None
        if data is None and self.blank_msg == "":
            return ""
        else:
            return self._write_section(data)


class _BlockSection:
    def __init__(self, *lines, indent=1):
        self.lines = lines
        self.indent = indent

    def write(self, kls):
        _indent = "\t" * self.indent
        guide = f""
        for line in self.lines:
            guide += f"{_indent}{line}\n"
        return guide


_input_section = _HelpSection("compartments/inputs",
                              "Input Compartments",
                              "There are no required inputs")

_output_section = _HelpSection("compartments/outputs",
                               "Output Compartments",
                               "There are no expected outputs")

_param_section = _HelpSection("hyperparameters",
                              "Hyperparameters",
                              "There are no required hyperparameters")


class GuideList(Enum):
    """"""
    Input = "input"
    Output = "output"
    Parameters = "params"
    Monitoring = "monitoring"
    Wiring = "wiring"


class Guides:
    """
    A container that builds and hold all the guides defined for each class.

    | For developers
    | To add a new guide first edit the GuideList enum with the value being
    | the name of guide on the Guides objects
    | Next define the guide below with
    |   __GUIDE_NAME = "GUIDE TITLE", [LIST, OF, GUIDE, SECTIONS]
    | Finally add self.guideName = self.__write_guide(*self.__GUIDE_NAME)

    Args:
         base_cls: the class the guides are written for
    """
    # Title, section

    # Section Guides
    __inputs = "Input Guide", [_input_section]
    __outputs = "Output Guide", [_output_section]
    __params = "Parameter Guide", [_param_section]

    # Compound Guides
    __monitoring = "Monitoring Guide", [_output_section],
    __wiring = "Wiring Guide", [_input_section, _output_section]

    def __init__(self, base_cls):
        self.__base_cls = base_cls
        self.__help = base_cls.help()

        self.inputs = self.__write_guide(*self.__inputs)
        self.outputs = self.__write_guide(*self.__outputs)
        self.monitoring = self.__write_guide(*self.__monitoring)
        self.params = self.__write_guide(*self.__params)

        self.wiring = self.__write_guide(*self.__wiring)

    def __write_guide(self, title, sections):
        if hasattr(self.__base_cls, "help"):
            guide = f"{title} for {self.__base_cls.__name__}\n"
            for section in sections:
                guide += f"{section.write(self.__help)}\n"
        else:
            guide = f"No help section found for {self.__base_cls.__name__}\n"
        return guide
