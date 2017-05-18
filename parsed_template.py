from appendages.util.decorators import attr_check, type_check


@attr_check
class ParsedTemplate:
    includes = list
    pins = str
    constructors = str
    setup = str
    loop_functions = str
    commands = str
    command_attaches = str
    command_functions = str
    extra_functions = str
    core_values = list

    def __init__(self):
        pass
