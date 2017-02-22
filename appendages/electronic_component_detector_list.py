from appendages.component_list import ComponentList

'''
The value from Decode will be packed into an int in the following format.

Each pad's code fits in 3 bits, with the last bit unused.
0|555|444|333|222|111

Component | Code
----------|-----
  Unknown | 0
     Wire | 1
 Resistor | 2
Capacitor | 3
 Inductor | 4
    Diode | 5

For example, let's say the components are on the following pads:
1: Inductor
2: Resistor
3: Capacitor
4: Wire
5: Diode

The code would be 42315, packed into an int would be:
 |  5|  1|  3|  2|  4
0|101|001|011|010|100; Without seperators: 0101001011010100
'''


class ElectronicComponentDetector:
    def __init__(self, label):
        self.label = label


class ElectronicComponentDetectorList(ComponentList):
    TIER = 1

    def __init__(self):
        self.electronic_component_detectorList = []

    def add(self, json_item):
        self.electronic_component_detectorList.append(ElectronicComponentDetector(json_item['label']))

    def get_includes(self):
        return '#include "ElectronicComponentDetector.h"\n'

    def get_constructor(self):
        rv = "ElectronicComponentDetector ecd;\n"
        return rv

    def get_setup(self):
        rv = "ecd.init();\n"
        return rv

    def get_commands(self):
        # List of serial commands
        return "\tkDecode,\n\tkDecodeResult,\n"

    def get_command_attaches(self):
        rv = "\tcmdMessenger.attach(kDecode, Decode);\n"
        return rv

    def get_command_functions(self):
        rv = "void Decode() {\n"
        rv += "\tchar pad = cmdMessenger.readBinArg<char>();\n"
        rv += "\tchar code[5];\n"
        rv += "\tint rv = 0;\n"
        rv += "\tecd.decode(pad - '0', code, false);\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kDecode);\n"
        rv += "\tfor(int i = 0; i < 5; i++) { \n"
        rv += "\t\trv |= code[i] << (i * 3);\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kDecodeResult, rv);"
        rv += "}\n\n"
        return rv

    def get_core_values(self):
        for i, arm in enumerate(self.electronic_component_detectorList):
            config = {}
            config['index'] = i
            config['type'] = "Electronic Component Detector"
            config['label'] = arm.label
            yield config
