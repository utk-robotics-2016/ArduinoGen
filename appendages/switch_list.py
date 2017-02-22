from appendages.component_list import ComponentList


class Switch:
    def __init__(self, label, pin, pullup):
        self.label = label
        self.pin = pin
        self.pullup = pullup


class SwitchList(ComponentList):
    TIER = 1

    def __init__(self):
        self.switchList = []

    def add(self, json_item):
        self.switchList.append(Switch(json_item['label'], json_item['pin'], json_item['pullup']))
        self.switchList.sort(key=lambda x: x.label, reverse=False)

    def get_pins(self):
        rv = ""
        for sensor in self.switchList:
            rv += "const char {0:s}_pin = {1:d};\n".format(sensor.label, sensor.pin)
        rv += "\n"
        return rv

    def get_constructor(self):
        rv = ""
        for i, sensor in enumerate(self.switchList):
            rv += "const char {0:s}_index = {1:d};\n".format(sensor.label, i)
        rv += "char switches[{0:d}] = {{\n".format(len(self.switchList))
        for sensor in self.switchList:
            rv += ("\t{0:s}_pin,\n").format(sensor.label)
        rv = rv[:-2] + "\n};\n"
        return rv

    def get_setup(self):
        rv = ""
        for sensor in self.switchList:
            if sensor.pullup:
                rv += "\tpinMode({0:s}_pin, INPUT_PULLUP);\n".format(sensor.label)
            else:
                rv += "\tpinMode({0:s}_pin, INPUT);\n".format(sensor.label)
        rv += "\n"
        return rv

    def get_commands(self):
        return "\tkReadSwitch,\n\tkReadSwitchResult,\n"

    def get_command_attaches(self):
        return "\tcmdMessenger.attach(kReadSwitch, readSwitch);\n"

    def get_command_functions(self):
        rv = "void readSwitch() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.switchList))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kReadSwitch);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\t\tcmdMessenger.sendBinCmd(kAcknowledge, kReadSwitch);\n"
        rv += "\t\tcmdMessenger.sendBinCmd(kReadSwitchResult, digitalRead(switches[indexNum]));\n"
        rv += "}\n\n"
        return rv

    def get_core_values(self):
        for i, switch in enumerate(self.switchList):
            a = {}
            a['index'] = i
            a['label'] = switch.label
            a['type'] = "Switch"
            yield a
