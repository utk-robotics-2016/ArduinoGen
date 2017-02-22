from appendages.component_list import ComponentList


class FourWheelDrive:
    def __init__(self, label, use_velocity_control, lf_motor, rf_motor, lb_motor, rb_motor,
                 wheel_diameter, wheelbase_width, wheelbase_length):
        self.label = label
        self.lf_motor = lf_motor
        self.rf_motor = rf_motor
        self.lb_motor = lb_motor
        self.rb_motor = rb_motor
        self.use_velocity_control = use_velocity_control
        self.wheel_diameter = wheel_diameter
        self.wheelbase_width = wheelbase_width
        self.wheelbase_length = wheelbase_length


class FourWheelDriveList(ComponentList):
    TIER = 3

    def __init__(self):
        self.drive_list = []

    def add(self, json_item, motors, vcms):
        use_velocity_control = json_item['use_velocity_control']
        if use_velocity_control:
            lf_motor = vcms.get(json_item['left_front_drive_motor'])
            rf_motor = vcms.get(json_item['right_front_drive_motor'])
            lb_motor = vcms.get(json_item['left_back_drive_motor'])
            rb_motor = vcms.get(json_item['right_back_drive_motor'])
        else:
            lf_motor = motors.get(json_item['left_front_drive_motor'])
            rf_motor = motors.get(json_item['right_front_drive_motor'])
            lb_motor = motors.get(json_item['left_back_drive_motor'])
            rb_motor = motors.get(json_item['right_back_drive_motor'])

        self.drive_list.append(FourWheelDrive(json_item['label'], use_velocity_control, lf_motor,
                                              rf_motor, lb_motor, rb_motor,
                                              json_item['wheel_diameter'],
                                              json_item['wheelbase_width'],
                                              json_item['wheelbase_length']))

    def get_includes(self):
        return '#include "FourWheelDrive.h"'

    def get_constructor(self):
        rv = "FourWheelDrive fwds[] = {\n"
        for drivebase in self.drive_list:
            if drivebase.use_velocity_control:
                rv += ("\tFourWheelDrive(&vcms[{0:s}_index], &vcms[{1:s}_index], " +
                       "&vcms[{2:s}_index], &vcms[{3:s}_index]),\n")\
                        .format(drivebase.lf_motor.label, drivebase.rf_motor.label,
                                drivebase.lb_motor.label, drivebase.rb_motor.label)
            else:
                rv += ("\tFourWheelDrive(&motors[{0:s}_index], &motors[{1:s}_index], " +
                       "&motors[{2:s}_index], &motors[{3:s}_index]),\n")\
                        .format(drivebase.lf_motor.label, drivebase.rf_motor.label,
                                drivebase.lb_motor.label, drivebase.rb_motor.label)
        rv = rv[:-2] + "\n};\n"
        return rv

    def get_commands(self):
        rv = "\tkDriveFWD,\n"
        rv += "\tkStopFWD,\n"
        rv += "\tkDriveFWD_PID,\n"
        rv += "\tkGetFWDLeftVelocity,\n"
        rv += "\tkGetFWDLeftVelocityResult,\n"
        rv += "\tkGetFWDRightVelocity,\n"
        rv += "\tkGetFWDRightVelocityResult,\n"
        rv += "\tkGetFWDLeftFrontVelocity,\n"
        rv += "\tkGetFWDLeftFrontVelocityResult,\n"
        rv += "\tkGetFWDLeftBackVelocity,\n"
        rv += "\tkGetFWDLeftBackVelocityResult,\n"
        rv += "\tkGetFWDRightFrontVelocity,\n"
        rv += "\tkGetFWDRightFrontVelocityResult,\n"
        rv += "\tkGetFWDRightBackVelocity,\n"
        rv += "\tkGetFWDRightBackVelocityResult,\n"
        rv += "\tkGetFWDLeftPosition,\n"
        rv += "\tkGetFWDLeftPositionResult,\n"
        rv += "\tkGetFWDRightPosition,\n"
        rv += "\tkGetFWDRightPositionResult,\n"
        return rv

    def get_command_attaches(self):
        rv = "\tcmdMessenger.attach(kDriveFWD, driveFWD);\n"
        rv += "\tcmdMessenger.attach(kStopFWD, stopFWD);\n"
        rv += "\tcmdMessenger.attach(kDriveFWD_PID, driveFWD_PID);\n"
        rv += "\tcmdMessenger.attach(kGetFWDLeftVelocity, getFWDLeftVelocity);\n"
        rv += "\tcmdMessenger.attach(kGetFWDRightVelocity, getFWDRightVelocity);\n"
        rv += "\tcmdMessenger.attach(kGetFWDLeftFrontVelocity, getFWDLeftFrontVelocity);\n"
        rv += "\tcmdMessenger.attach(kGetFWDLeftBackVelocity, getFWDLeftBackVelocity);\n"
        rv += "\tcmdMessenger.attach(kGetFWDRightFrontVelocity, getFWDRightFrontVelocity);\n"
        rv += "\tcmdMessenger.attach(kGetFWDRightBackVelocity, getFWDRightBackVelocity);\n"
        rv += "\tcmdMessenger.attach(kGetFWDLeftPosition, getFWDLeftPosition);\n"
        rv += "\tcmdMessenger.attach(kGetFWDRightPosition, getFWDRightPosition);\n"
        return rv

    def get_command_functions(self):
        rv = "void driveFWD() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kDriveFWD);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tint values[4];\n"
        rv += "\tfor(int i = 0; i < 4; i++) {\n"
        rv += "\t\tvalues[i] = cmdMessenger.readBinArg<int>();\n"
        rv += "\t\tif(!cmdMessenger.isArgOk() || values[i] < -1023 || values[i] > 1023) {\n"
        rv += "\t\t\tcmdMessenger.sendBinCmd(kError, kDriveFWD);\n"
        rv += "\t\t\treturn;\n"
        rv += "\t\t}\n"
        rv += "\t}\n"
        rv += "\tfwds[indexNum].drive(values[0], values[1], values[2], values[3]);\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kDriveFWD);\n"
        rv += "}\n\n"

        rv += "void stopFWD() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kStopFWD);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tfwds[indexNum].stop();\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kStopFWD);\n"
        rv += "}\n\n"

        rv += "void driveFWD_PID() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kDriveFWD_PID);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tfloat values[4];\n"
        rv += "\tfor(int i = 0; i < 4; i++) {\n"
        rv += "\t\tvalues[i] = cmdMessenger.readBinArg<float>();\n"
        rv += "\t\tif(!cmdMessenger.isArgOk()){\n"
        rv += "\t\t\tcmdMessenger.sendBinCmd(kError, kDriveFWD_PID);\n"
        rv += "\t\t\treturn;\n"
        rv += "\t\t}\n"
        rv += "\t}\n"
        rv += "\tfwds[indexNum].drivePID(values[0], values[1], values[2], values[3]);\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kDriveFWD_PID);\n"
        rv += "}\n\n"

        rv += "void getFWDLeftVelocity() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDLeftVelocity);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDLeftVelocity);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDLeftVelocityResult, fwds[indexNum].getLeftVelocity());\n"
        rv += "}\n\n"

        rv += "void getFWDRightVelocity() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDRightVelocity);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDRightVelocity);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDRightVelocityResult, fwds[indexNum].getRightVelocity());\n"
        rv += "}\n\n"

        rv += "void getFWDLeftFrontVelocity() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDLeftFrontVelocity);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDLeftFrontVelocity);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDLeftFrontVelocityResult, fwds[indexNum].getLeftFrontVelocity());\n"
        rv += "}\n\n"

        rv += "void getFWDLeftBackVelocity() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDLeftBackVelocity);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDLeftBackVelocity);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDLeftBackVelocityResult, fwds[indexNum].getLeftBackVelocity());\n"
        rv += "}\n\n"

        rv += "void getFWDRightFrontVelocity() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDRightFrontVelocity);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDRightFrontVelocity);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDRightFrontVelocityResult, fwds[indexNum].getRightFrontVelocity());\n"
        rv += "}\n\n"

        rv += "void getFWDRightBackVelocity() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDRightBackVelocity);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDRightBackVelocity);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDRightBackVelocityResult, fwds[indexNum].getRightBackVelocity());\n"
        rv += "}\n\n"

        rv += "void getFWDLeftPosition() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDLeftPosition);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDLeftPosition);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDLeftPositionResult, fwds[indexNum].getLeftPosition());\n"
        rv += "}\n\n"

        rv += "void getFWDRightPosition() {\n"
        rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
        rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.drive_list))
        rv += "\t\tcmdMessenger.sendBinCmd(kError, kGetFWDRightPosition);\n"
        rv += "\t\treturn;\n"
        rv += "\t}\n"
        rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kGetFWDRightPosition);\n"
        rv += "\tcmdMessenger.sendBinCmd(kGetFWDRightPositionResult, fwds[indexNum].getRightPosition());\n"
        rv += "}\n\n"

        return rv

    def get_core_values(self):
        for i, drivebase in enumerate(self.drive_list):
            config = {}
            config['index'] = i
            config['label'] = drivebase.label
            config['type'] = "Four Wheel Drive"
            config['use_velocity_control'] = drivebase.use_velocity_control
            config['left_front_motor'] = drivebase.lf_motor.label
            config['left_back_motor'] = drivebase.lb_motor.label
            config['right_front_motor'] = drivebase.rf_motor.label
            config['right_back_motor'] = drivebase.rf_motor.label
            config['wheelbase_width'] = drivebase.wheelbase_width
            config['wheelbase_length'] = drivebase.wheelbase_length
            yield config
