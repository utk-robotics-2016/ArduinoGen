class ultrasonic:
    def __init__(self, label, pin):
        self.label = label
        self.pin = pin


class ultrasonics:

    def __init__(self):
        self.sensor_list = []

    def add(self, json_item):
        self.sensor_list.append(ultrasonic(json_item['label'], json_item['pin']))

    def get_include(self):
        return "#include \"NewPing.h\";"

    def get_pins(self):
        rv = ""
        for sensor in self.sensor_list:
            rv = rv + "const char %s_pin = %d;\n" % (sensor.label, sensor.pin)
        return rv

    def get_constructor(self):
        rv = ""
        for i in range(len(self.sensor_list)):
            rv = rv + "const char %s_index = %d;\n" % (self.sensor_list[i].label, i)
        rv = rv + "NewPing ultrasonics[%d] = {\n" % len(self.sensor_list)

        for sensor in self.sensor_list:
            rv = rv + "    NewPing(%s_pin, %s_pin),\n" % (sensor.label, sensor.label)
        rv = rv[:-2] + "\n};\n"
        return rv

    def get_setup(self):
        return ""

    def get_response_block(self):
        rv = '''    else if(args[0].equals(String("rus"))){ // read ultrasonics
        if(numArgs == 2){
            int indexNum = args[1].toInt();
            if(indexNum > -1 && indexNum < %d){
                unsigned int response = ultrasonics[indexNum].ping();
                Serial.println(response);
            } else {
                Serial.println("Error: usage - rus [id]");
            }
        } else {
            Serial.println("Error: usage - rus [id]");
        }
    }
''' % (len(self.sensor_list))
        return rv
