/* This is the file for arduino 
   This expects the arduino to be connected to:
       - An RGB LED strip on STRIP_R, STRIP_G, STRIP_B
   It can currently: 
       - Blink the discord colour when SSIG_DISCORD_JOIN is received
*/

// Signals we expect to receive through serial
#define SSIG_DISCORD_JOIN 1
#define SSIG_SET_DEFAULT_COLOUR 2
#define SSIG_QUERY_STATE 3

// RGB strip pins
#define RGB_R 11
#define RGB_G 10
#define RGB_B 9
/// How we traverse from R to B
#define RGB_ITER -1
/// Strip state
struct strip_state {
        uint8_t rval;
        uint8_t gval;
        uint8_t bval;
};

// The current state of the strip.
/// ONLY led_fadeto should change this
struct strip_state active_state = {0x00, 0x00, 0x00};

inline void get_iterator_array(const struct strip_state start, const struct strip_state end,
                               uint8_t *iterators) {
        for (int i = 0; i < 3; i++) {
                if (*(&start.rval + i) < *(&end.rval + i))
                        iterators[i] = 1;
                else
                        iterators[i] = -1;
        }
}

// Fade the strip to a specific state
void led_fadeto(const struct strip_state *state) {
        // What we iterate R, G, and B by
        uint8_t rgb_iterators[3];
        get_iterator_array(active_state, *state, &rgb_iterators[0]);

        int change_occurred = 1;
        while (change_occurred) {
                change_occurred = 0;
                if (active_state.rval != state->rval) {
                        active_state.rval += rgb_iterators[0];
                        change_occurred = 1;
                }

                if (active_state.gval != state->gval) {
                        active_state.gval += rgb_iterators[1];
                        change_occurred = 1;
                }

                if (active_state.bval != state->bval) {
                        active_state.bval += rgb_iterators[2];
                        change_occurred = 1;
                }

                analogWrite(RGB_R, active_state.rval);
                analogWrite(RGB_G, active_state.gval);
                analogWrite(RGB_B, active_state.bval);
                delay(3);
        }
        
}

// Pulse the strip with the discord colour N times
inline int led_discord_pulse(int n,  const struct strip_state *accent_state) {
        const struct strip_state old_state = {active_state.rval, active_state.gval, active_state.bval};
        const struct strip_state discord_purple =  {102, 0, 255};
        // Threshold to 16 or less
        int n_cap = n & 15;

        for (int i = 0; i < n_cap; i++) {
                led_fadeto(&discord_purple);
                delay(200);
                led_fadeto(accent_state);
                delay(200);
        }
        led_fadeto(&old_state);
        return 0;
        
}

// Act on whatever we have in the serial buffer
int perform_user_operation() {
        uint8_t operation;
        // Read single byte (operation spec)
        Serial.readBytes(&operation, 1);
        uint8_t operands[8];
        switch (operation) {
        case SSIG_DISCORD_JOIN:
                {
                        // Read 4 bytes (R, G, B, count)
                        Serial.readBytes(&operands[0], 4);
                        const struct strip_state accent = {operands[0], operands[1], operands[2]};
                        led_discord_pulse(operands[3], &accent);
                }
                break;
        case SSIG_SET_DEFAULT_COLOUR:
                {
                        // Read 3 bytes (R, G, B)
                        Serial.readBytes(&operands[0], 3);
                        const struct strip_state default_colour = {operands[0], operands[1], operands[2]};
                        led_fadeto(&default_colour);
                }
                break;
        case SSIG_QUERY_STATE:
                Serial.write(active_state.rval);
                Serial.write(active_state.gval);
                Serial.write(active_state.bval);
                break;

        }
        return 0;
}

void setup() {
        Serial.begin(9600);
        pinMode(RGB_R, OUTPUT);
        pinMode(RGB_G, OUTPUT);
        pinMode(RGB_B, OUTPUT);
}

void loop() {
        if (Serial.available()) {
                perform_user_operation();
        }
}
