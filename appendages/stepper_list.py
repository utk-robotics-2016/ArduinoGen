from appendages.component_list import ComponentList


class Stepper:
    def __init__(self, label, steps, pin_a, pin_b, pin_c, pin_d, initial_speed, angle_per_step):
        self.label = label
        self.steps = steps
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_c = pin_c
        self.pin_d = pin_d
        self.initial_speed = initial_speed
        self.angle_per_step = angle_per_step


class StepperList(ComponentList):
    TIER = 1

    def __init__(self):
        self.stepperDict = {}
        self.stepperList = []

    def add(self, json_item):
        stepper = Stepper(json_item['label'], json_item['steps'],
                          json_item['pin_a'], json_item['pin_b'],
                          json_item['pin_c'], json_item['pin_d'],
                          json_item['initial_speed'], json_item['angle_per_step'])
        self.stepperDict[json_item['label']] = stepper
        self.stepperList.append(stepper)
        self.stepperList.sort(key=lambda x: x.label, reverse=False)

    def get(self, label):
        return self.actuators[label]

    def get_includes(self):
        return '#include "Stepper.h"\n'

    def get_pins(self):
        rv = ""
        for stepper in self.stepperList:
            rv += "const char {0:s}_pin_a = {1:d};\n".format(stepper.label, stepper.pin_a)
            rv += "const char {0:s}_pin_b = {1:d};\n".format(stepper.label, stepper.pin_b)
            rv += "const char {0:s}_pin_c = {1:d};\n".format(stepper.label, stepper.pin_c)
            rv += "const char {0:s}_pin_d = {1:d};\n".format(stepper.label, stepper.pin_d)
        rv += "\n"
        return rv

    def get_constructor(self):
        rv = ""
        for i, stepper in enumerate(self.stepperList):
            rv += "const char {0:s}_index = {1:d};\n".format(stepper.label, i)

        rv += ("Stepper steppers[{0:d}] = {{\n").format(len(self.stepperList))
        for stepper in self.stepperList:
            rv += ("\tStepper({0:d}, {1:s}_pin_a, {1:s}_pin_b, {1:s}_pin_c, {1:s}_pin_d), ")\
                    .format(stepper.steps, stepper.label)
        rv = rv[:-2] + "\n};\n"
        return rv

    def get_setup(self):
        rv = ""
        for stepper in self.stepperList:
            rv += "\tpinMode({0:s}_pin_a, OUTPUT);\n".format(stepper.label)
            rv += "\tpinMode({0:s}_pin_b, OUTPUT);\n".format(stepper.label)
            rv += "\tpinMode({0:s}_pin_c, OUTPUT);\n".format(stepper.label)
            rv += "\tpinMode({0:s}_pin_d, OUTPUT);\n".format(stepper.label)

        for stepper in self.stepperList:
            rv += ("\tsteppers[{0:s}_index].setSpeed({1:f});\n").format(stepper.label,
                                                                        stepper.initial_speed)
        rv += "\n"

        return rv

    def get_commands(self):
        return "\tkSetStepperSpeed,\n\tkStepStepper,\n"

    def get_command_attaches(self):
        rv = "\tcmdMessenger.attach(kSetStepperSpeed, setStepperSpeed);\n"
        rv += "\tcmdMessenger.attach(kStepStepper, stepStepper);\n"
        return rv

    def get_command_functions(self):
        rv = "void setStepperSpeed() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() ||indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.stepperList))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kSetStepperSpeed);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tint value = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk()){\n"
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kSetStepperSpeed);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\t\tsteppers[indexNum].setSpeed(value);\n"
        rv += "\t\tcmdMessenger.sendBinCmd(kAcknowledge, kSetStepperSpeed);\n"
        rv += "}\n\n"

        rv += "void stepStepper() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.stepperList))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kStepStepper);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tint value = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk()){\n"
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kStepStepper);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tsteppers[indexNum].step(value);\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kStepStepper);\n"
        rv += "}\n\n"
        return rv

    def get_core_values(self):
        for i, stepper in enumerate(self.stepperList):
            config = {}
            config['index'] = i
            config['label'] = stepper.label
            config['type'] = "Stepper"
            config['initial_speed'] = stepper.initial_speed
            config['angle_per_step'] = stepper.angle_per_step
            yield config
