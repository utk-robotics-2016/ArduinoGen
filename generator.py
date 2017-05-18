import os
import json
import platform
from subprocess import call

from template_parser import TemplateParser
from appendages.util.decorators import singleton, attr_check, type_check
from appendages.util.logger import Logger
logger = Logger()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CURRENT_ARDUINO_CODE_DIR = "/Robot/CurrentArduinoCode"


@singleton
@attr_check
class Generator:
    appendage_dict = dict
    parsed_templates = list

    def __new__(cls, appendage_dict: dict):
        return object.__new__(cls)

    @type_check
    def __init__(self, appendage_dict: dict):
        self.appendage_dict = appendage_dict
        self.parsed_templates = []

    def load_templates(self):
        tp = TemplateParser()
        for i, (device_type, device_list) in enumerate(self.appendage_dict.items()):
            percent = i / len(self.appendage_dict)

            # Untitle
            device_type_file = device_type.lower().replace(" ", "_")
            
            logger.info("\tLoading templates... [{0:s}] {1:d}/{2:d}".format('=' * int(percent * 20) + ' ' * (20 - int(percent * 20)), i + 1, len(self.appendage_dict)), extra={'repeated': True})
            parsed_template = tp.parse_template('appendages/arduino_gen/{0:s}.template'.format(device_type_file),
                                                device_list)
            parsed_template.tier = device_list[0].TIER
            self.parsed_templates.append(parsed_template)
        self.parsed_templates.sort(key=lambda i: i.tier)

    def write_file(self, filename):
        with open('{0:s}/arduino.template'.format(CURRENT_DIR)) as f:
            template = f.read()

        logger.info("\tWriting file... [{0:s}] 1/10".format('=' * 1 + ' ' * 9), extra={'repeated': True})
        template = template.replace('<<<includes>>>', self.get_includes())
        logger.info("\tWriting file... [{0:s}] 2/10".format('=' * 2 + ' ' * 8), extra={'repeated': True})
        template = template.replace('<<<pins>>>', self.get_pins())
        logger.info("\tWriting file... [{0:s}] 3/10".format('=' * 3 + ' ' * 7), extra={'repeated': True})
        template = template.replace('<<<constructors>>>', self.get_constructors())
        logger.info("\tWriting file... [{0:s}] 4/10".format('=' * 4 + ' ' * 6), extra={'repeated': True})
        template = template.replace('<<<setup>>>', self.get_setup())
        logger.info("\tWriting file... [{0:s}] 5/10".format('=' * 5 + ' ' * 5), extra={'repeated': True})
        template = template.replace('<<<loop_functions>>>', self.get_loop())
        logger.info("\tWriting file... [{0:s}] 6/10".format('=' * 6 + ' ' * 4), extra={'repeated': True})
        template = template.replace('<<<commands>>>', self.get_commands())
        logger.info("\tWriting file... [{0:s}] 7/10".format('=' * 7 + ' ' * 3), extra={'repeated': True})
        template = template.replace('<<<command_attaches>>>', self.get_command_attaches())
        logger.info("\tWriting file... [{0:s}] 8/10".format('=' * 8 + ' ' * 2), extra={'repeated': True})
        template = template.replace('<<<command_functions>>>', self.get_command_functions())
        logger.info("\tWriting file... [{0:s}] 9/10".format('=' * 9 + ' ' * 1), extra={'repeated': True})
        template = template.replace('<<<extra_functions>>>', self.get_extra_functions())
        logger.info("\tWriting file... [{0:s}] 10/10".format('=' * 10), extra={'repeated': True})
        with open(filename, 'w') as f:
            f.write(template)
            f.flush()

        if platform.system() == "Linux":
            #TODO
            #call([CURRENT_DIR + ?, "--style=allman", "-n",filename])
            pass
        elif platform.system() == "Darwin": # Mac
            call([CURRENT_DIR + "/astyle/mac/build/mac/bin/Astyle", "--style=allman", "-n",filename])
        elif platform.system() == "Windows":
            #TODO: Anthony?
            #call([CURRENT_DIR + ?, "--style=allman", "-n",filename])
            pass



    def get_includes(self):
        includes = []
        for parsed_template in self.parsed_templates:
            for temp_include in parsed_template.includes:
                if temp_include not in includes:
                    includes.append(temp_include)

        rv = ""
        for include in includes:
            rv += "#include {0:s}\n".format(include)

        return rv

    def get_pins(self):
        rv = ""
        for parsed_template in self.parsed_templates:
            rv += parsed_template.pins + "\n"
        return rv[:-2]

    def get_constructors(self):
        rv = ""
        for parsed_template in self.parsed_templates:
            rv += parsed_template.constructors + "\n"
        return rv[:-2]

    def get_setup(self):
        rv = ""
        for parsed_template in self.parsed_templates:
            rv += parsed_template.setup + "\n"
        return rv[:-2]

    def get_loop(self):
        rv = ""
        for parsed_template in self.parsed_templates:
            rv += parsed_template.loop_functions + "\n"
        return rv[:-2]

    def get_commands(self):
        rv = ""
        self.commands = {}
        self.commands['kAcknowledge'] = 0
        self.commands['kError'] = 1
        self.commands['kUnknown'] = 2
        self.commands['kSetLed'] = 3
        self.commands['kPing'] = 4
        self.commands['kPingResult'] = 5
        self.commands['kPong'] = 6
        cmd_idx = 7
        for parsed_template in self.parsed_templates:
            cmds = parsed_template.commands
            rv += cmds
            cmds = cmds.split(',')
            for cmd in cmds:
                cmd = cmd.replace('\t', '').replace('\n', '').replace(',', '')
                if cmd != "":
                    self.commands[cmd] = cmd_idx
                    cmd_idx += 1
        rv = rv[:-2] # remove last comma
        return rv

    def get_command_attaches(self):
        rv = ""
        for parsed_template in self.parsed_templates:
            rv += parsed_template.command_attaches
        return rv[:-1]

    def get_command_functions(self):
        rv = "// Command Functions\n"
        for parsed_template in self.parsed_templates:
            rv += parsed_template.command_functions + "\n"
        return rv[:-2]

    def get_extra_functions(self):
        rv = "// Extra Functions"
        for parsed_template in self.parsed_templates:
            rv += parsed_template.extra_functions + "\n"
        return rv[:-2]

    def write_shell_scripts(self, folder, arduino):
        with open("{0:s}/upload.sh".format(folder), 'w') as upload_fo:
            upload_fo.write("#!/usr/bin/env bash\n")
            upload_fo.write("cd {0:s}/{1:s}\n".format(CURRENT_ARDUINO_CODE_DIR, arduino))
            upload_fo.write("git add -A\n")
            upload_fo.write('git commit -m "new uploaded arduino code for %s"\n' % arduino)
            upload_fo.write("git push\n")
            upload_fo.write("pio run -t upload\n")
        os.chmod("{0:s}/upload.sh".format(folder), 0o777)

        with open("{0:s}/serial.sh".format(folder), 'w') as serial_fo:
            serial_fo.write("#!/usr/bin/env bash\n")
            serial_fo.write("picocom /dev/%s -b 115200 --echo\n" % arduino)
        os.chmod("{0:s}/serial.sh".format(folder), 0o777)

    def write_core_config_file(self, folder, arduino):
        core_config = {}
        core_config['appendages'] = []

        for parsed_template in self.parsed_templates:
            core_config['appendages'] += parsed_template.core_values

        core_config['commands'] = self.commands

        with open("{0:s}/{1:s}_core.json".format(folder, arduino), 'w') as fo:
            fo.write(json.dumps(core_config, indent=4))
        os.chmod("{0:s}/{1:s}_core.json".format(folder, arduino), 0o777)
