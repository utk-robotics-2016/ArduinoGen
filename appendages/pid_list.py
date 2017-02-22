from appendages.component_list import ComponentList


class PID:
    def __init__(self, label, kp, ki, kd, min_output=None, max_output=None, reverse=False):
        self.label = label
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        if min_output is not None:
            self.min_output = float(min_output)
            self.max_output = float(max_output)
        self.reverse = reverse


class PidList(ComponentList):
    TIER = 1

    def __init__(self):
        self.pidDict = {}
        self.pidList = []
        self.vpidDict = {}
        self.vpidList = []

    def add(self, json_item):
        if 'min_output' in json_item:
            min_output = json_item['min_output']
            max_output = json_item['max_output']
        else:
            min_output = None
            max_output = None

        if not json_item['vpid']:
            pid = PID(json_item['label'], json_item['kp'], json_item['ki'], json_item['kd'],
                      min_output, max_output, json_item['reverse'])
            self.pidDict[pid.label] = pid
            self.pidList.append(pid)
            self.pidList.sort(key=lambda x: x.label, reverse=False)
        else:
            pid = PID(json_item['label'], json_item['kp'], json_item['ki'], json_item['kd'],
                      min_output, max_output, json_item['reverse'])
            self.vpidDict[pid.label] = pid
            self.vpidList.append(pid)
            self.vpidList.sort(key=lambda x: x.label, reverse=False)

    def get(self, label):
        if label in self.vpidDict:
            return self.vpidDict[label]
        elif label in self.pidDict:
            return self.pidDict[label]
        else:
            return None

    def get_includes(self):
        return '#include "PID.h"\n#include "vPID.h"\n'

    def get_constructor(self):
        rv = ""
        length_vpids = len(self.vpidList)
        if length_vpids > 0:
            for i, vpid in enumerate(self.vpidList):
                rv += "const char {0:s}_index = {1:d};\n".format(vpid.label, i)
            rv += ("double lastPositions_vpid[{0:d}];\ndouble Inputs_vpid[{0:d}], " +
                   "Setpoints_vpid[{0:d}], Outputs_vpid[{0:d}];\n").format(length_vpids)
            rv += "vPID vpids[{0:d}] = {{\n".format(length_vpids)
            for vpid in self.vpidList:
                rv += ("\tvPID(&Inputs_vpid[{0:s}_index], &Outputs_vpid[{0:s}_index], " +
                       "&Setpoints_vpid[{0:s}_index], {1:f}, {2:f}, {3:f}, {4:s}),\n")\
                        .format(vpid.label, vpid.kp, vpid.ki, vpid.kd,
                                "REVERSE" if vpid.reverse else "DIRECT")
            rv = rv[:-2] + "\n};\n"

        length_pids = len(self.pidList)
        if length_pids > 0:
            for i, pid in enumerate(self.pidList):
                rv += "const char {0:s}_index = {1:d};\n".format(pid.label, i)
            rv += ("double lastPositions_pid[{0:d}];\ndouble Inputs_pid[{0:d}], " +
                   "Setpoints_pid[{0:d}], Outputs_pid[{0:d}];\n").format(length_pids)
            rv += "PID pids[{0:d}] = {{\n".format(length_pids)
            for pid in self.pidList:
                rv += ("\tPID(&Inputs_pid[{0:s}_index], &Outputs_pid[{0:s}_index], " +
                       "&Setpoints_pid[{0:s}_index], {1:f}, {2:f}, {3:f}, {4:s}),\n")\
                        .format(pid.label, pid.kp, pid.ki, pid.kd,
                                "REVERSE" if pid.reverse else "DIRECT")
            rv = rv[:-2] + "\n};\n"
        return rv

    def get_setup(self):
        rv = ""
        for vpid in self.vpidList:
            if hasattr(vpid, 'min_output'):
                rv += ("\tvpids[{0:s}_index].SetOutputLimits({1:f}, {2:f});\n")\
                        .format(vpid.label, vpid.min_output, vpid.max_output)
        for pid in self.pidList:
            if hasattr(pid, 'min_output'):
                rv += ("\tpids[{0:s}_index].SetOutputLimits({1:f}, {2:f});\n")\
                        .format(pid.label, pid.min_output, pid.max_output)
        return rv

    def get_commands(self):
        rv = "\tkPidConstants,\n"
        rv += "\tkPidConstantsResult,\n"
        rv += "\tkModifyPidConstants,\n"
        rv += "\tkSetPidSetpoint,\n"
        rv += "\tkPidOff,\n"
        rv += "\tkPidDisplay,\n"
        rv += "\tkPidDisplayResult,\n"
        rv += "\tkVpidConstants,\n"
        rv += "\tkVpidConstantsResult,\n"
        rv += "\tkModifyVpidConstants,\n"
        rv += "\tkSetVpidSetpoint,\n"
        rv += "\tkVpidOff,\n"
        rv += "\tkVpidDisplay,\n"
        rv += "\tkVpidDisplayResult,\n"
        return rv

    def get_command_attaches(self):
        rv = "\tcmdMessenger.attach(kPidConstants, pidConstants);\n"
        rv += "\tcmdMessenger.attach(kModifyPidConstants, modifyPidConstants);\n"
        rv += "\tcmdMessenger.attach(kSetPidSetpoint, setPidSetpoint);\n"
        rv += "\tcmdMessenger.attach(kPidOff, pidOff);\n"
        rv += "\tcmdMessenger.attach(kPidDisplay, pidDisplay);\n"
        rv += "\tcmdMessenger.attach(kVpidConstants, vpidConstants);\n"
        rv += "\tcmdMessenger.attach(kModifyVpidConstants, modifyVpidConstants);\n"
        rv += "\tcmdMessenger.attach(kSetVpidSetpoint, setVpidSetpoint);\n"
        rv += "\tcmdMessenger.attach(kVpidOff, vpidOff);\n"
        rv += "\tcmdMessenger.attach(kVpidDisplay, vpidDisplay);\n"
        return rv

    def get_command_functions(self):
        rv = ""
        if len(self.pidList) > 0:
            rv += "void pidConstants() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum <0 || indexNum > {0:d}) {{\n".format(len(self.pidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kPidConstants);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kPidConstants);\n"
            rv += "\tcmdMessenger.sendCmdStart(kPidConstantsResult);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(pids[indexNum].GetKp());\n"
            rv += "\tcmdMessenger.sendCmdBinArg(pids[indexNum].GetKi());\n"
            rv += "\tcmdMessenger.sendCmdBinArg(pids[indexNum].GetKd());\n"
            rv += "\tcmdMessenger.sendCmdEnd();\n"
            rv += "}\n\n"

            rv += "void modifyPidConstants() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.pidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kModifyPidConstants);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tfloat gains[3];\n"
            rv += "\tfor(int i = 0; i < 3; i++) {\n"
            rv += "\t\t\tgains[i] = cmdMessenger.readBinArg<float>();\n"
            rv += "\t\tif(!cmdMessenger.isArgOk()){\n"
            rv += "\t\t\tcmdMessenger.sendBinCmd(kError, kModifyPidConstants);\n"
            rv += "\t\t\treturn;\n"
            rv += "\t\t}\n"
            rv += "\t}\n"
            rv += "\tpids[indexNum].SetTunings(gains[0], gains[1], gains[2]);\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kModifyPidConstants);\n"
            rv += "}\n\n"

            rv += "void setPidSetpoint() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.pidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kSetPidSetpoint);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tfloat value = cmdMessenger.readBinArg<float>();\n"
            rv += "\tif(!cmdMessenger.isArgOk()) {\n"
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kSetPidSetpoint);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tpids[indexNum].SetMode(AUTOMATIC);\n"
            rv += "\tSetpoints_pid[indexNum] = value;\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kSetPidSetpoint);\n"
            rv += "}\n\n"

            rv += "void pidOff() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.pidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kPidOff);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tpids[indexNum].SetMode(MANUAL);\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kPidOff);\n"
            rv += "}\n\n"

            rv += "void pidDisplay() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.pidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kPidDisplay);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kPidDisplay);\n"
            rv += "\tcmdMessenger.sendCmdStart(kPidDisplayResult);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(Inputs_pid[indexNum]);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(Setpoints_pid[indexNum]);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(Outputs_pid[indexNum]);\n"
            rv += "\tcmdMessenger.sendCmdEnd();\n"
            rv += "}\n\n"

        if len(self.vpidList) > 0:
            rv += "void vpidConstants() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum <0 || indexNum > {0:d}) {{\n".format(len(self.vpidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kVpidConstants);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kVpidConstants);\n"
            rv += "\tcmdMessenger.sendCmdStart(kVpidConstantsResult);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(vpids[indexNum].GetKp());\n"
            rv += "\tcmdMessenger.sendCmdBinArg(vpids[indexNum].GetKi());\n"
            rv += "\tcmdMessenger.sendCmdBinArg(vpids[indexNum].GetKd());\n"
            rv += "\tcmdMessenger.sendCmdEnd();\n"
            rv += "}\n\n"

            rv += "void modifyVpidConstants() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() ||indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.vpidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kModifyVpidConstants);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tfloat gains[3];\n"
            rv += "\tfor(int i = 0; i < 3; i++) {\n"
            rv += "\t\tgains[i] = cmdMessenger.readBinArg<float>();\n"
            rv += "\t\tif(!cmdMessenger.isArgOk()){\n"
            rv += "\t\t\tcmdMessenger.sendBinCmd(kError, kModifyVpidConstants);\n"
            rv += "\t\t\treturn;\n"
            rv += "\t\t}\n"
            rv += "\t}\n"
            rv += "\tvpids[indexNum].SetTunings(gains[0], gains[1], gains[2]);\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kModifyVpidConstants);\n"
            rv += "}\n\n"

            rv += "void setVpidSetpoint() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.vpidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kSetVpidSetpoint);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tfloat value = cmdMessenger.readBinArg<float>();\n"
            rv += "\tif(!cmdMessenger.isArgOk()){\n"
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kSetVpidSetpoint);\n"
            rv += "\t}\n"
            rv += "\tvpids[indexNum].SetMode(AUTOMATIC);\n"
            rv += "\tSetpoints_vpid[indexNum] = value;\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kSetVpidSetpoint);\n"
            rv += "}\n\n"

            rv += "void vpidOff() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.vpidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kVpidOff);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tpids[indexNum].SetMode(MANUAL);\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kVpidOff);\n"
            rv += "}\n\n"

            rv += "void vpidDisplay() {\n"
            rv += "\tint indexNum = cmdMessenger.readBinArg<int>();\n"
            rv += "\tif(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > {0:d}) {{\n".format(len(self.vpidList))
            rv += "\t\tcmdMessenger.sendBinCmd(kError, kVpidDisplay);\n"
            rv += "\t\treturn;\n"
            rv += "\t}\n"
            rv += "\tcmdMessenger.sendBinCmd(kAcknowledge, kVpidDisplay);\n"
            rv += "\tcmdMessenger.sendCmdStart(kVpidDisplayResult);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(Inputs_vpid[indexNum]);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(Setpoints_vpid[indexNum]);\n"
            rv += "\tcmdMessenger.sendCmdBinArg(Outputs_vpid[indexNum]);\n"
            rv += "\tcmdMessenger.sendCmdEnd();\n"
            rv += "}\n\n"

        return rv

    def get_core_values(self):
        for i, vpid in enumerate(self.vpidList):
            a = {}
            a['index'] = i
            a['label'] = vpid.label
            a['type'] = "PID"
            a['vpid'] = True
            yield a
        for i, pid in enumerate(self.pidList):
            a = {}
            a['index'] = i
            a['label'] = pid.label
            a['type'] = "PID"
            a['vpid'] = False
            yield a
