from appendages.component_list import ComponentList


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
        rv += "\tecd.decode(pad, code, false);\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kDecode);\n"
        rv += "\tcmdMessenger.sendCmdStart(kDecodeResult);\n"
        rv += "\tfor(int x = 0 ; x <= 4 ; x++ ) { \n"
        rv += "\t\tcmdMessenger.sendCmdBinArg(code[x]);\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendCmdEnd();\n"
        rv += "}\n\n"
        return rv

    def get_core_values(self):
        for i, arm in enumerate(self.electronic_component_detectorList):
            config = {}
            config['index'] = i
            config['type'] = "Electronic Component Detector"
            config['label'] = arm.label
            yield config
