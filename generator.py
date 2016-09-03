import os
import shutil
import fileinput
import getpass

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CURRENT_ARDUINO_CODE_DIR = "/CurrentArduinoCode"

class Generator:
    def __init__(self, appendage_dict):
        self.appendage_dict = appendage_dict

    def add_header(self):
        return "// Auto-generated by ArduinoGen\n\n"

    def add_includes(self):
        rv = "// Includes\n"

        keys = self.appendage_dict.keys()
        for i in range(1, 3):
            for key in keys:
                if not self.appendage_dict[key].tier == i:
                    continue
                include = self.appendage_dict[key].get_include()
                if include != "":
                    rv += "%s\n" % include
        rv += "\n"

        rv += "#define STR1(x)  #x\n"
        rv += "#define STR(x)  STR1(x)\n\n"
        rv += "// Globals\n"
        rv += "int ledState = HIGH;\n"
        rv += "// Command parsing\n"
        rv += "const int MAX_ARGS = 6;\n"
        rv += "String args[MAX_ARGS];\n"
        rv += "int numArgs = 0;\n\n"

        return rv

    def add_pins(self):
        rv = "// Pin definitions\nconst char LED = 13;\n"
        keys = self.appendage_dict.keys()
        for key in keys:
            pins = self.appendage_dict[key].get_pins()
            if not pins == "":
                rv += pins + "\n"
        rv += "\n"
        return rv

    def add_constructors(self):
        rv = "// Constructors\n"
        keys = self.appendage_dict.keys()
        for i in range(1, 3):
            for key in keys:
                if not self.appendage_dict[key].tier == i:
                    continue
                constructor = self.appendage_dict[key].get_constructor()
                if not constructor == "":
                    rv += constructor + "\n"
        rv += "\n"
        return rv

    def add_setup(self):
        rv = "void setup() {\n    // Init LED pin\n    pinMode(LED, OUTPUT);\n\n"
        keys = self.appendage_dict.keys()
        for key in keys:
            rv += self.appendage_dict[key].get_setup()
        rv += "    //Init Serial\n    Serial.begin(115200);\n}\n\n"
        return rv

    def add_loop(self):
        extra = ""
        keys = self.appendage_dict.keys()
        for key in keys:
            extra += self.appendage_dict[key].get_loop_functions()
        return '''/* The loop is set up in two parts. First the Arduino does the work it needs to
 * do for every loop, next is runs the checkInput() routine to check and act on
 * any input from the serial connection.
 */
void loop() {
    int inbyte;

    // Accept and parse serial input
    checkInput();
    %s
}

''' % extra

    def add_parse_args(self):
        return '''void parse_args(String command) {
    numArgs = 0;
    int beginIdx = 0;
    int idx = command.indexOf(" ");

    String arg;
    char charBuffer[16];

    while (idx != -1)
    {
        arg = command.substring(beginIdx, idx);

        // add error handling for atoi:
        args[numArgs++] = arg;
        beginIdx = idx + 1;
        idx = command.indexOf(" ", beginIdx);
    }

    arg = command.substring(beginIdx);
    args[numArgs++] = arg;
}

'''

    def add_check_input(self):
        return '''/* This routine checks for any input waiting on the serial line. If any is
 * available it is read in and added to a 128 character buffer. It sends back
 * an error should the buffer overflow, and starts overwriting the buffer
 * at that point. It only reads one character per call. If it receives a
 * newline character is then runs the parseAndExecuteCommand() routine.
 */
void checkInput() {
    int inbyte;
    static char incomingBuffer[128];
    static char bufPosition=0;

    if(Serial.available()>0) {
        // Read only one character per call
        inbyte = Serial.read();
        if(inbyte==10||inbyte==13) {
            // Newline detected
            incomingBuffer[bufPosition]='\\0'; // NULL terminate the string
            bufPosition=0; // Prepare for next command

            // Supply a separate routine for parsing the command. This will
            // vary depending on the task.
            parseAndExecuteCommand(String(incomingBuffer));
        }
        else {
            incomingBuffer[bufPosition]=(char)inbyte;
            bufPosition++;
            if(bufPosition==128) {
                Serial.println("error: command overflow");
                bufPosition=0;
            }
        }
    }
}

'''

    def add_parse_and_execute_command_beginning(self):
        return '''/* This routine parses and executes any command received. It will have to be
 * rewritten for any sketch to use the appropriate commands and arguments for
 * the program you design. I find it easier to separate the input assembly
 * from parsing so that I only have to modify this function and can keep the
 * checkInput() function the same in each sketch.
 */
void parseAndExecuteCommand(String command) {
    Serial.println("> " + command);
    parse_args(command);
    if(args[0].equals(String("ping"))) {
        if(numArgs == 1) {
            Serial.println("ok");
        } else {
            Serial.println("error: usage - 'ping'");
        }
    }
    else if(args[0].equals(String("le"))) { // led set
        if(numArgs == 2) {
            if(args[1].equals(String("on"))) {
                ledState = HIGH;
                digitalWrite(LED,HIGH);
                Serial.println("ok");
            } else if(args[1].equals(String("off"))) {
                ledState = LOW;
                digitalWrite(LED,LOW);
                Serial.println("ok");
            } else {
                Serial.println("error: usage - 'le [on/off]'");
            }
        } else {
            Serial.println("error: usage - 'le [on/off]'");
        }
    }
    else if(args[0].equals(String("rl"))) { // read led
        if(numArgs == 1) {
            Serial.println(ledState);
        } else {
            Serial.println("error: usage - 'rl'");
        }
    }
'''

    def add_commands(self):
        rv = ""
        keys = self.appendage_dict.keys()
        for key in keys:
            rv += self.appendage_dict[key].get_response_block()
        return rv

    def add_parse_and_execute_command_ending(self):
        return '''    else if(args[0].equals(String("ver"))) { // version information
        if(numArgs == 1) {
            String out = "Source last modified: ";
            out += __TIMESTAMP__;
            out += "\\r\\nPreprocessor timestamp: " __DATE__ " " __TIME__;
            out += "\\r\\nSource code line number: ";
            out += __LINE__;
            out += "\\r\\nUsername: " STR(__USER__);
            out += "\\r\\nDirectory: " STR(__DIR__);
            out += "\\r\\nGit hash: " STR(__GIT_HASH__);
            Serial.println(out);
        } else {
            Serial.println("error: usage - 'ver'");
        }
    }
    else {
        // Unrecognized command
        Serial.println("error: unrecognized command");
    }
}

'''

    def add_extra_functions(self):
        rv = '''double toDouble(String s)
{
  char buf[s.length() + 1];
  s.toCharArray(buf, s.length() + 1);
  return atof(buf);
}'''
        keys = self.appendage_dict.keys()
        for appendage in self.appendage_dict.values():
            rv += self.appendage.get_extra_functions()
        return rv

    def write_shell_scripts(self, writeTo, arduino):
        upload_fo = open("%s/upload.sh" % writeTo, 'w')
        upload_fo.write("#!/usr/bin/env bash\n")
        upload_fo.write("ino build\n")
        upload_fo.write("git add -A\n")
        upload_fo.write('git commit -m "new uploaded arduino code for %s"\n' % arduino)
        upload_fo.write("git push\n")
        upload_fo.write("ino upload\n")
        upload_fo.close()
        os.chmod("%s/upload.sh" % writeTo, 0777)

        serial_fo = open("%s/serial.sh" % writeTo, 'w')
        serial_fo.write("#!/usr/bin/env bash\n")
        serial_fo.write("picocom /dev/%s -b 115200 --echo\n" % arduino)
        serial_fo.close()
        os.chmod("%s/serial.sh" % writeTo, 0777)
    
    def write_indices_file(self, writeTo, arduino):
        indices = {}
        for appendages in self.appendage_dict.values():
            for i, appendaage in appendages.get_indices:
                indices[appendage.label] = i
        
        indices_text = json.dumps(indices)

        indices_fo = open("%s/%s_indices.json" % (writeTo, arduino), 'w')
        indices_fo.write(indices_text)
        indices_fo.close()
        os.chmod("%s/%s_indices.json" % (writeTo, arduino), 'w')
