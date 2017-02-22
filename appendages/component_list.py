class ComponentList:
    TIER = 0

    def __init__(self):
        pass

    def add(self, json_item):
        raise NotImplementedError("ComponentList: add not implemented")

    def get(self, label):
        return None

    def get_includes(self):
        return ""

    def get_pins(self):
        return ""

    def get_constructors(self):
        return ""

    def get_setup(self):
        return ""

    def get_commands(self):
        raise NotImplementedError("ComponentList: get_commands not implemented")

    def get_command_attaches(self):
        raise NotImplementedError("ComponentList: get_command_attaches not implemented")

    def get_command_functions(self):
        raise NotImplementedError("ComponentList: get_command_functions not implemented")

    def get_loop_functions(self):
        return ""

    def get_extra_functions(self):
        return ""

    def get_core_values(self):
        raise NotImplementedError("ComponentList: get_core_values not implemented")
