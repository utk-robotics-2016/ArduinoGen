// Auto-generated by ArduinoGen

// Includes
#include "CmdMessenger.h"
#include "Encoder.h"


// Globals
int ledState = HIGH;

// Pin definitions
const char LED = 13;
const char encoder_pin_a = 4;
const char encoder_pin_b = 5;
const char encoder2_pin_a = 7;
const char encoder2_pin_b = 8;

const char switch_pin = 1;
const char switch_pullup_pin = 2;



// Constructors
// Attach a new CmdMessenger object to the default Serial port
CmdMessenger cmdMessenger = CmdMessenger(Serial);
Encoder encoders[2] =
{
    Encoder(encoder_pin_a, encoder_pin_b),
    Encoder(encoder2_pin_a, encoder2_pin_b)
};
char digital_inputs[2] =
{
    switch_pin,
    switch_pullup_pin
};


// This is the list of recognized commands. These can be commands that can either be sent or received.
// In order to receive, attach a callback function to these events
enum
{
    kAcknowledge,
    kError,
    kUnknown,
    kSetLed,
    kPing,
    kPingResult,
    kPong,
    kReadEncoder,
    kReadEncoderResult,
    kZeroEncoder,
    kReadDigitalInput,
    kReadDigitalInputResult
};

void setup()
{
    // Init LED pin
    pinMode(LED, OUTPUT);

    pinMode(encoder_pin_a, INPUT);
    pinMode(encoder_pin_b, INPUT);
    pinMode(encoder2_pin_a, INPUT);
    pinMode(encoder2_pin_b, INPUT);
    pinMode(switch_pin, INPUT);
    pinMode(switch_pullup_pin, INPUT_PULLUP);


    // Initialize Serial Communication
    Serial.begin(115200);

    // Attach callback methods
    attachCommandCallbacks();

    // Flash led 3 times at the end of setup
    for(int i = 0; i < 3; i++)
    {
        digitalWrite(LED, HIGH);
        delay(250);
        digitalWrite(LED, LOW);
        delay(250);
    }
    ledState = LOW;
}

void loop()
{
    // Process incoming serial data, and perform callbacks
    cmdMessenger.feedinSerialData();


}

// Callbacks define on which received commands we take action
void attachCommandCallbacks()
{
    // Attach callback methods
    cmdMessenger.attach(unknownCommand);
    cmdMessenger.attach(kPing, ping);
    cmdMessenger.attach(kSetLed, setLed);
    cmdMessenger.attach(kReadEncoder, readEncoder);
    cmdMessenger.attach(kZeroEncoder, zeroEncoder);
    cmdMessenger.attach(kReadDigitalInput, readDigitalInput);

}

// Called when a received command has no attached function
void unknownCommand()
{
    cmdMessenger.sendCmd(kError, kUnknown);
}

// Called upon initialization of Spine to check connection
void ping()
{
    cmdMessenger.sendBinCmd(kAcknowledge, kPing);
    cmdMessenger.sendBinCmd(kPingResult, kPong);
}

// Callback function that sets led on or off
void setLed()
{
    // Read led state argument, interpret string as boolean
    ledState = cmdMessenger.readBoolArg();
    digitalWrite(LED, ledState);
    cmdMessenger.sendBinCmd(kAcknowledge, kSetLed);
}

// Command Functions
void readEncoder()
{
    int indexNum = cmdMessenger.readBinArg<int>();
    if(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > 2)
    {
        cmdMessenger.sendBinCmd(kError, kReadEncoder);
        return;
    }
    cmdMessenger.sendBinCmd(kAcknowledge, kReadEncoder);
    cmdMessenger.sendBinCmd(kReadEncoderResult, encoders[indexNum].read());
}
void zeroEncoder()
{
    int indexNum = cmdMessenger.readBinArg<int>()
                   if(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > 2)
    {
        cmdMessenger.sendBinCmd(kError, kZeroEncoder);
        return;
    }
    encoders[indexNum].write(0);
    cmdMessenger.sendBinCmd(kAcknowledge, kZeroEncoder);
}
void readDigitalInput()
{
    int indexNum = cmdMessenger.readBinArg<int>();
    if(!cmdMessenger.isArgOk() || indexNum < 0 || indexNum > 2)
    {
        cmdMessenger.sendBinCmd(kError, kReadDigitalInput);
        return;
    }
    cmdMessenger.sendBinCmd(kAcknowledge, kReadDigitalInput);
    cmdMessenger.sendBinCmd(kReadDigitalInputResult, digitalRead(digital_inputs[indexNum]));
}


// Extra Functions