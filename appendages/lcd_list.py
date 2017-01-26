from appendages.component_list import ComponentList


class LCD:
    def __init__(self, label, rs, enable, d4, d5, d6, d7):
        self.label = label
        self.rs = rs
        self.enable = enable
        self.d4 = d4
        self.d5 = d5
        self.d6 = d6
        self.d7 = d7


class LcdList(ComponentList):
    # Tiers are 1 through 3
    # Required for generator to add import and constructors.
    TIER = 3

    def __init__(self):
        self.lcds = []

    def add(self, json_item):
        self.lcds.append(LCD(json_item['label'], json_item['rs'], json_item['enable'],
                             json_item['d4'], json_item['d5'], json_item['d6'], json_item['d7']))

    def get_includes(self):
        return '#include <LiquidCrystal.h>\n'

    def get_constructor(self):
        rv = "LiquidCrystal lcds[{0:d}] = {{".format(len(self.lcds))
        for lcd in self.lcds:
            rv += ("\tLiquidCrystal({0:d}, {1:d}, {2:d}, {3:d}, {4:d}, {5:d}),\n"
                   .format(lcd.rs, lcd.enable, lcd.d4, lcd.d5, lcd.d6, lcd.d7))
        rv = rv[:-2] + "\n};\n"
        return rv

    def get_commands(self):
        return "\tkPrintLCD,\n"

    def get_command_attaches(self):
        return "\tcmdMessenger.attach(kPrintLCD, printLCD);\n"

    def get_command_functions(self):
        rv = "void printLCD(){\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.lcds))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kPrintLCD);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tString text = cmdMessenger.readStringArg();\n"
        rv += "\tlcds[indexNum].print(text);\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kPrintLCD);\n"
        rv += "}\n"
        return rv

    def get_core_values(self):
        for i, lcd in enumerate(self.lcds):
            a = {}
            a['index'] = i
            a['label'] = lcd.label
            a['type'] = "Lcd"
            yield a
