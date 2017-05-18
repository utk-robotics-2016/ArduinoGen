from appendages.util.decorators import attr_check, type_check, singleton, void
import re
from parsed_template import ParsedTemplate
from appendages.arduino_gen.component import Component


@singleton
@attr_check
class TemplateParser:
    list_ = list

    def __new__(cls):
        return object.__new__(cls)

    def __init__(self):
        self.section_head_pattern = re.compile(r'\s*(.+)\s*{{{')
        self.include_pattern = re.compile(r'(["|<][\w.]+["|>])')
        self.local_pattern = re.compile(r'<<<([\w.]+)>>>')
        self.loop_separated_by_pattern = re.compile(r'loop_separated_by\([\'|\"](.+)[\'|\"]\)')
        self.loop_with_index_pattern = re.compile(r'loop_with_index\([\'|\"](.+)[\'|\"]\)')
        self.core_values_pattern = re.compile(r'(.+)\s*=\s*(.+)')
        self.if_pattern = re.compile(r'\s*if\s*\((.+)\)')
        self.else_pattern = re.compile(r'else')

    @type_check
    def parse_template(self, template_filename: str, list_: list) -> ParsedTemplate:
        self.list_ = list_
        self.setup_globals()
        self.lines = []
        # Pull file into memory
        with open(template_filename) as f:
            for line in f:
                self.lines.append(line)

        template_heirachy = {}
        self.num_lines = len(self.lines)
        # print("NUMBER OF LINES: {0:d}".format(self.num_lines))

        self.line_number = 0
        while self.line_number < self.num_lines:
            section_title, section_contents, end_line_number = self.grab_section()
            template_heirachy[section_title] = section_contents
            self.line_number = end_line_number + 1

        pt = ParsedTemplate()
        pt.includes = []
        if 'include' in template_heirachy:
            include_list = template_heirachy['include']
            for include in include_list:
                m = self.include_pattern.match(include.strip())
                if m is not None:
                    matches = m.groups()
                    if len(matches) == 1:
                        #TODO: check is m.groups() returns a tuple or list
                        # if list then replace the below line with:
                        # pt.include += matches
                        pt.includes += [matches[0]]
                else:
                    raise Exception("Include not formatted properly: {0:s}".format(include.strip()))
        
        if 'pins' in template_heirachy:
            pt.pins = self.handle_section(template_heirachy['pins'])
        else:
            pt.pins = ""

        if 'constructors' in template_heirachy:
            pt.constructors = self.handle_section(template_heirachy['constructors'])
        else:
            pt.constructors = ""

        if 'setup' in template_heirachy:
            pt.setup = self.handle_section(template_heirachy['setup'])
        else:
            pt.setup = ""
 
        if 'loop_functions' in template_heirachy:
            pt.loop_functions = self.handle_section(template_heirachy['loop_functions'])
        else:
            pt.loop_functions = ""

        if 'commands' in template_heirachy:
            pt.commands = self.handle_section(template_heirachy['commands'])
        else:
            raise Exception("commands section not in template")

        if 'command_attaches' in template_heirachy:
            pt.command_attaches = self.handle_section(template_heirachy['command_attaches'])
        else:
            raise Exception("command attaches section not in template")

        if 'command_functions' in template_heirachy:
            pt.command_functions = self.handle_section(template_heirachy['command_functions'])
        else:
            raise Exception("command functions section not in template")

        
        if 'extra_functions' in template_heirachy:
            pt.extra_functions = self.handle_section(template_heirachy['extra_functions'])
        else:
            pt.extra_functions = "" 

        pt.core_values = []
        if 'core_values' in template_heirachy:
            for index, appendage in enumerate(list_):
                d = {}
                d['label'] = appendage.label
                d['index'] = index
                d['type'] = appendage.__class__.__name__
                for line in template_heirachy['core_values']:
                    line = line.strip()  # Remove leading and trailing whitespace
                    if line == "":
                        continue
                    line = self.apply_globals(line)
                    line = self.apply_locals(line, appendage)
                    m = self.core_values_pattern.match(line)
                    if m is not None:
                        matches = m.groups()
                        if len(matches) == 2:
                            d[matches[0]] = matches[1]
                        else:
                            raise Exception("core values not formatted correctly")
                pt.core_values.append(d)
        else:
            for index, appendage in enumerate(list_):
                d = {}
                d['label'] = appendage.label
                d['index'] = index
                d['type'] = appendage.__class__.__name__
                pt.core_values.append(d)


        return pt

    @type_check
    def setup_globals(self) -> void:
        self.global_vars = {}
        self.global_vars['length'] = len(self.list_)

    @type_check
    def apply_globals(self, line: str) -> str:
        for global_var in self.global_vars:
            if "%%%{0:s}%%%".format(global_var) in line:
                try:
                    line = line.replace("%%%{0:s}%%%".format(global_var), str(self.global_vars[global_var]))
                except:
                    raise Exception("Error could not convert global {0:s} value {} to string".format(global_var, self.global_vars[global_var]))
        return line

    @type_check
    def grab_section(self) -> (tuple, void):
        section_contents = []
        section_head = ""
        has_section_head = False

        # print("GRABBING SECTION")

        while self.line_number < self.num_lines:
            line = self.lines[self.line_number]
            # print("\tLINE: {0:d} - {1:s}".format(self.line_number, line))
            if '{{{' in line:
                if not has_section_head:
                    m = self.section_head_pattern.match(line)
                    if m is not None:
                        matches = m.groups()
                        if len(matches) == 1:
                            section_head = matches[0]
                            has_section_head = True
                            # print("\tFOUND SECTION HEAD: {0:s}".format(section_head))
                        else:
                            raise Exception("Error reading section head on line {0:d}:{1:s}".format(self.line_number, line))
                    else:
                        raise Exception("Error reading section head on line {0:d}:{1:s}".format(self.line_number, line))
                else:
                    # print("\tFOUND INNER SECTION")
                    temp_section_head, temp_section_contents, end_line_number = self.grab_section()
                    section_contents.append((temp_section_head, temp_section_contents))
                    self.line_number = end_line_number
            elif '}}}' in line:
                if not has_section_head:
                    # in a format string }} => } and {{ => {
                    raise Exception("Error closing '}}}}}}' without opening '{{{{{{' on line number {0:d}".format(self.line_number))
                else:
                    # print("\tFOUND END OF SECTION")
                    return section_head, section_contents, self.line_number
            else:
                section_contents.append(line)
            self.line_number += 1
        raise Exception("Error finished file while still in section {0:s}".format(section_head))

    @type_check
    def handle_section(self, section: list, appendage: (Component, void)=None) -> str:
        rv = ""
        if_list =[]
        for line in section:
            if isinstance(line, str):
                # Handle previous conditional
                if len(if_list) > 0:
                    rv += self.handle_if(if_list, appendage)
                    if_list = []
                line = line.strip()  # Remove leading and trailing whitespace
                if line == "":
                    continue
                temp = self.apply_globals(line)
                if appendage is not None:
                    temp = self.apply_locals(line, appendage)
                rv += temp + "\n"
            # inner section
            elif isinstance(line, tuple):
                if line[0] == 'loop':
                    # Handle previous conditional
                    if len(if_list) > 0:
                        rv += self.handle_if(if_list, appendage)
                        if_list = []
                    rv += self.handle_loop(line[1])
                elif 'loop_separated_by' in line[0]:
                    # Handle previous conditional
                    if len(if_list) > 0:
                        rv += self.handle_if(if_list, appendage)
                        if_list = []
                    rv += self.handle_loop_separated_by(line[0], line[1])
                elif 'loop_with_index' in line[0]:
                    # Handle previous conditional
                    if len(if_list) > 0:
                        rv += self.handle_if(if_list, appendage)
                        if_list = []
                    rv += self.handle_loop_with_index(line[0], line[1])
                # Accumulate the conditional
                elif 'if' in line[0] or 'else' in line[0]:
                    if_list.append(line)
                else:
                    raise Exception("Unknown header type: {0:s}".format(line[0]))
        return rv

    @type_check
    def handle_loop(self, section: list) -> str:
        rv = ""
        if_list = []
        for appendage in self.list_:
            for line in section:
                if isinstance(line, str):
                    # Handle previous conditional
                    if len(if_list) > 0:
                        rv += self.handle_if(if_list, appendage)
                        if_list = []
                    line = line.strip()  # Remove leading and trailing whitespace
                    if line == "":
                        continue
                    temp = self.apply_globals(line)
                    rv += self.apply_locals(temp, appendage) + '\n'
                # inner section
                elif isinstance(line, tuple):
                    # Accumulate the conditional
                    if 'if' in line[0] or 'else' in line[0]:
                        if_list.append(line)
                    else:
                        # Handle previous conditional
                        if len(if_list) > 0:
                            rv += self.handle_if(if_list, appendage)
                            if_list = []
                        rv += self.handle_section(line, appendage)
            # Handle previous conditional
            if len(if_list) > 0:
                rv += self.handle_if(if_list, appendage)
                if_list = []
        return rv

    @type_check
    def handle_loop_separated_by(self, section_head: str, section_body: list) -> str:
        #TODO: add if handling 

        rv = ""
        m = self.loop_separated_by_pattern.match(section_head)
        if m is not None:
            matches = m.groups()
            if len(matches) == 1:
                for appendage in self.list_:
                    for line in section_body:
                        if isinstance(line, str):
                            line = line.strip()  # Remove leading and trailing whitespace
                            if line == "":
                                continue
                            temp = self.apply_globals(line)
                            rv += self.apply_locals(temp, appendage) + matches[0] +'\n'
                            # inner section
                        elif isinstance(line, tuple):
                            rv += self.handle_section(line)
            else:
                raise Exception("loop_separated_by section header not formatted correctly: {}".format(section_head))

                rv = rv[:-(len(matches[0]) + 1)] + '\n' # Remove the last separator
        else:
            raise Exception("loop_separated_by section header not formatted correctly: {}".format(section_head))
        return rv

    @type_check
    def handle_loop_with_index(self, section_head: str, section_body: list) -> str:
        #TODO: add if handling

        rv = ""
        m = self.loop_with_index_pattern.match(section_head)
        if m is not None:
            matches = m.groups()
            if len(matches) == 1:
                for index, appendage in enumerate(self.list_):
                    for line in section_body:
                        if isinstance(line, str):
                            line = line.strip()  # Remove leading and trailing whitespace
                            if line == "":
                                continue
                            temp = self.apply_globals(line)
                            temp = temp.replace("<<<{0:s}>>>".format(matches[0]), str(index))
                            rv += self.apply_locals(temp, appendage) + '\n'
                            # inner section
                        elif isinstance(line, tuple):
                            rv += self.handle_section(line)
            else:
                raise Exception("loop_with_index section header not formatted correctly: {}".format(section_head))
        else:
            raise Exception("loop_with_index section header not formatted correctly: {}".format(section_head))
        return rv

    @type_check
    def handle_if(self, if_list: list, appendage: (Component, void)=None) -> str:
        for i in if_list:
            m = self.if_pattern.match(i[0])
            # m is None only for the else
            if m is not None:
                matches = m.groups()
                # matches should be a list of a single element that is the conditional
                if len(matches) == 1:
                    condition = matches[0]
                    condition = self.apply_globals(condition)
                    if appendage is not None:
                        condition = self.apply_locals(condition, appendage)

                    # if the condition holds then use this section
                    if eval(condition):
                        return self.handle_section(i[1], appendage)
                else:
                    raise Exception("conditional not formatted correctly: {}".format(i[0]))

            # fullmatch is used so that else if doesn't trigger
            m = self.else_pattern.fullmatch(i[0])
            if m is not None:
                # use this section (the else)
                return self.handle_section(i[1], appendage)
        return ""

    @type_check
    def apply_locals(self, line: str, appendage: Component) -> str:
        matches = self.local_pattern.findall(line)
        locals_ = []
        if matches is not None and len(matches) > 0:
            for match in matches:
                # If match is in locals_ then we have already replaced it
                if match not in locals_:
                    dot = match.split('.')
                    value = appendage
                    for d in dot:
                        value = getattr(value, d)
                    try:
                        line = line.replace('<<<{0:s}>>>'.format(match), str(value))
                    except:
                         raise Exception("Error could not convert {} to string".format(value))
                    finally:
                        locals_.append(match)
        return line

