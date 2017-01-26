from appendages.component_list import ComponentList


class Magnetometer:
    def __init__(self, label):
        self.label = label


class MagnetometerList(ComponentList):
    # TODO is this the right tier for this?
    TIER = 2

    def __init__(self):
        self.sensor_list = []

    def add(self, json_item):
        self.sensor_list.append(Magnetometer(json_item['label']))

    def get_includes(self):
        return '#include <Wire.h>\n#include "Magnetometer.h"\n'

    def get_constructor(self):
        return "Magnetometer magnetometer;\n"

    def get_setup(self):
        return "\tWire.begin();\n\tmagnetometer.config();\n"

    def get_commands(self):
        return "\tkReadX,\n\tkReadXResult,\n\tkReadY,\n\tkReadYResult\n\tkReadZ,\n\tkReadZResult,\n"

    def get_command_functions(self):
        rv = "void readX() {\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kReadX);\n"
        rv += "\tcmdMessenger.sendBinCmd(kReadXResult, magnetometer.readX());\n"
        rv += "}\n"

        rv += "void readY() {\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kReadY);\n"
        rv += "\tcmdMessenger.sendBinCmd(kReadYResult, magnetometer.readY());\n"
        rv += "}\n"

        rv += "void readZ() {\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kReadZ);\n"
        rv += "\tcmdMessenger.sendBinCmd(kReadZResult, magnetometer.readZ());\n"
        rv += "}\n"

        return rv

    def get_indices(self):
        return [0, self.sensor_list[0].label]

    def get_core_values(self):
        a = {}
        a['index'] = 0
        a['label'] = self.sensor_list[0].label
        a['type'] = "Magnetometer"
        return a
