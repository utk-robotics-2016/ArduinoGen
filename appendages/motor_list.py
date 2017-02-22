from appendages.component_list import ComponentList


class Motor:
    def __init__(self, label, dir_pin_a, dir_pin_b, pwm_pin, reverse, motor_controller, motor_type):
        self.label = label
        self.dir_pin_a = dir_pin_a
        self.dir_pin_b = dir_pin_b
        self.pwm_pin = pwm_pin
        self.reverse = reverse
        self.motor_controller = motor_controller
        self.motor_type = motor_type


class MotorList(ComponentList):
    TIER = 1

    def __init__(self):
        self.motorDict = {}
        self.motorList = []

    def add(self, json_item):
        if json_item['motor_controller'].lower() == 'monster moto':
            motor = Motor(json_item['label'], json_item['dir_pin_a'], json_item['dir_pin_b'],
                          json_item['pwm_pin'], json_item['reverse'], 'MonsterMoto', json_item['motor_type'])
        elif json_item['motor_controller'].lower() == 'rover five':
            motor = Motor(json_item['label'], json_item['dir_pin_a'], -1, json_item['pwm_pin'],
                          json_item['reverse'], 'RoverFive', json_item['motor_type'])
        elif json_item['motor_controller'].lower() == 'vex':
            motor = Motor(json_item['label'], -1, -1, json_item['pwm_pin'], json_item["reverse"],
                          'Vex', json_item['motor_type'])
        elif json_item['motor_controller'].lower() == 'mosfet':
            motor = Motor(json_item['label'], json_item['dir_pin_a'], -1, -1, json_item['reverse'],
                          'Mosfet', json_item['motor_type'])
        self.motorDict[motor.label] = motor
        self.motorList.append(motor)
        self.motorList.sort(key=lambda x: x.label, reverse=False)

    def get(self, label):
        if label in self.motorDict:
            return self.motorDict[label]
        else:
            return None

    def get_includes(self):
        return '#include "Motor.h"\n'

    def get_pins(self):
        rv = ""
        for motor in self.motorList:
            rv += "const char {0:s}_dir_pin_a = {1:d};\n".format(motor.label, motor.dir_pin_a)
            rv += "const char {0:s}_dir_pin_b = {1:d};\n".format(motor.label, motor.dir_pin_b)
            rv += "const char {0:s}_pwm_pin = {1:d};\n".format(motor.label, motor.pwm_pin)
        return rv

    def get_constructor(self):
        rv = ""
        for i, motor in enumerate(self.motorList):
            rv += "const char {0:s}_index = {1:d};\n".format(motor.label, i)
        rv += "Motor motors[{0:d}] = {{\n".format(len(self.motorList))
        for motor in self.motorList:
            rv += "\tMotor({0:s}_dir_pin_a, {0:s}_dir_pin_b, {0:s}_pwm_pin, {1:d}, {2:s}),\n"\
                    .format(motor.label, 1 if motor.reverse else 0,
                            motor.motor_controller)
        rv = rv[:-2] + "\n};\n"
        return rv

    def get_setup(self):
        rv = ""
        for motor in self.motorList:
            rv += "\tpinMode({0:s}_dir_pin_a, OUTPUT);\n".format(motor.label)
            if not motor.dir_pin_b == -1:
                rv += "\tpinMode({0:s}_dir_pin_b, OUTPUT);\n".format(motor.label)
            rv += "\tpinMode({0:s}_pwm_pin, OUTPUT);\n".format(motor.label)
        return rv

    def get_commands(self):
        return "\tkDriveMotor,\n\tkStopMotor,\n"

    def get_command_attaches(self):
        rv = "\tcmdMessenger.attach(kDriveMotor, driveMotor);\n"
        rv += "\tcmdMessenger.attach(kStopMotor, stopMotor);\n"
        return rv

    def get_command_functions(self):
        rv = "void driveMotor() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.motorList))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kDriveMotor);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tint value = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(cmdMessenger.isArgOk() && value > -1024 && value < 1024) {\n"
        rv += "\t\tmotors[indexNum].drive(value);\n"
        rv += "\t\tcmdMessenger.sendBinCmd(kAcknowledge, kDriveMotor);\n"
        rv += "\t} else {\n"
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kDriveMotor);\n"
        rv += "\t}\n"
        rv += "}\n\n"

        rv += "void stopMotor() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.motorList))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kStopMotor);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tmotors[indexNum].stop();\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kStopMotor);\n"
        rv += "}\n\n"
        return rv

    def get_core_values(self):
        for i, motor in enumerate(self.motorList):
            a = {}
            a['index'] = i
            a['label'] = motor.label
            a['type'] = "Motor"
            a['motor_controller'] = motor.motor_controller
            a['motor_type'] = motor.motor_type
            yield a
