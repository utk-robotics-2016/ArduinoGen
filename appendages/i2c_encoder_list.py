from appendages.component_list import ComponentList


class I2CEncoder:
    def __init__(self, label, reverse, init_number):
        self.label = label
        self.reverse = reverse
        self.init_number = init_number


class I2CEncoderList(ComponentList):
    TIER = 1

    def __init__(self):
        self.sensors = dict()
        self.sorted_sensors = []

    def add(self, json_item):
        sensor = I2CEncoder(json_item['label'], json_item['reverse'], json_item['init_number'])
        self.sensors[json_item['label']] = sensor
        self.sorted_sensors.append(sensor)
        self.sorted_sensors.sort(key=lambda x: x.init_number, reverse=False)

    def get(self, label):
        if label in self.sensors:
            return self.sensors[label]
        else:
            return None

    def get_includes(self):
        return '#include <Wire.h>\n#include "I2CEncoder.h"\n'

    def get_constructor(self):
        rv = ""
        for i in range(len(self.sorted_sensors)):
            rv += "const char {0:s}_index = {1:d};\n".format(self.sorted_sensors[i].label, i)
        rv += "I2CEncoder i2cencoders[{0:d}];\n".format(len(self.sorted_sensors))
        return rv

    def get_setup(self):
        rv = "\tWire.begin();\n"
        for sensor in self.sorted_sensors:
            rv += ("\ti2cencoders[{0:s}_index].init(MOTOR_393_TORQUE_ROTATIONS, " +
                   "MOTOR_393_TIME_DELTA);\n").format(sensor.label)
        for sensor in self.sorted_sensors:
            if sensor.reverse:
                rv += "\ti2cencoders[{0:s}_index].setReversed(true);\n".format(sensor.label)
        for sensor in self.sorted_sensors:
            rv += "\ti2cencoders[{0:s}_index].zero();\n".format(sensor.label)
        rv += "\n"
        return rv

    def get_commands(self):
        rv = "\tkI2CEncoderPosition,\n"
        rv += "\tkI2CEncoderPositionResult,\n"
        rv += "\tkI2CEncoderRawPosition,\n"
        rv += "\tkI2CEncoderRawPositionResult,\n"
        rv += "\tkI2CEncoderSpeed,\n"
        rv += "\tkI2CEncoderSpeedResult,\n"
        rv += "\tkI2CEncoderVelocity,\n"
        rv += "\tkI2CEncoderVelocityResult,\n"
        rv += "\tkI2CEncoderZero,\n"
        return rv

    def get_command_attaches(self):
        rv = "\tcmdMessenger.attach(kI2CEncoderPosition,i2cEncoderPosition);\n"
        rv += "\tcmdMessenger.attach(kI2CEncoderRawPosition,i2cEncoderRawPosition);\n"
        rv += "\tcmdMessenger.attach(kI2CEncoderSpeed,i2cEncoderSpeed);\n"
        rv += "\tcmdMessenger.attach(kI2CEncoderVelocity,i2cEncoderVelocity);\n"
        rv += "\tcmdMessenger.attach(kI2CEncoderZero,i2cEncoderZero);\n"
        return rv

    def get_command_functions(self):
        rv = "void i2cEncoderPosition() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.sorted_sensors))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kI2CEncoderPosition);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kI2CEncoderPosition);\n"
        rv += "\tcmdMessenger.sendBinCmd(kI2CEncoderPositionResult, i2cencoders[indexNum].getPosition());\n"
        rv += "}\n\n"

        rv += "void i2cEncoderRawPosition() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.sorted_sensors))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kI2CEncoderRawPosition);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kI2CEncoderRawPosition);\n"
        rv += "\tcmdMessenger.sendBinCmd(kI2CEncoderRawPositionResult, i2cencoders[indexNum].getRawPosition());\n"
        rv += "}\n\n"

        rv += "void i2cEncoderSpeed() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.sorted_sensors))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kI2CEncoderSpeed);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kI2CEncoderSpeed);\n"
        rv += "\tcmdMessenger.sendBinCmd(kI2CEncoderSpeedResult, i2cencoders[indexNum].getSpeed());\n"
        rv += "}\n\n"

        rv += "void i2cEncoderVelocity() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.sorted_sensors))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kI2CEncoderVelocity);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kI2CEncoderVelocity);\n"
        rv += "\tcmdMessenger.sendBinCmd(kI2CEncoderVelocityResult, i2cencoders[indexNum].getVelocity());\n"
        rv += "}\n\n"

        rv += "void i2cEncoderZero() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.sorted_sensors))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kI2CEncoderZero);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\ti2cencoders[indexNum].zero();\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kI2CEncoderZero);\n"
        rv += "}\n\n"

        return rv

    def get_core_values(self):
        for i, encoder in enumerate(self.sorted_sensors):
            a = {}
            a['index'] = i
            a['label'] = encoder.label
            a['type'] = "Encoder"
            yield a
