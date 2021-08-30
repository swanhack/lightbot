/* This is the file for arduino 
   This expects the arduino to be connected to:
       - An RGB LED strip on STRIP_R, STRIP_G, STRIP_B
   It can currently: 
       - Blink the discord colour when SSIG_DISCORD_JOIN is received
*/

// Signals we expect to receive through serial
#define SSIG_DISCORD_JOIN 'Q'

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
struct strip_state active_state = {0, 0, 0};

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
inline int led_discord_pulse(int n) {
        const struct strip_state old_state = {active_state.rval, active_state.gval, active_state.bval};
        const struct strip_state discord_purple = {0, 179, 36};
        const struct strip_state discord_accent = {102, 0, 255};
        // Threshold to 16 or less
        int n_cap = n & 15;

        char str[50];
        for (int i = 0; i < n_cap; i++) {
                led_fadeto(&discord_purple);
                delay(250);
                led_fadeto(&discord_accent);
                sprintf(str, "%d, %d, %d\n\r", active_state.rval, active_state.gval, active_state.bval);
                Serial.print(str);
        }
        led_fadeto(&old_state);
        return 0;
        
}

// Act on whatever we have in the serial buffer
int perform_user_operation() {
        char op = Serial.read();
        char str[50];
        sprintf(str, "read %c\n\r", op);
        Serial.print(str);
        switch (op) {
        case SSIG_DISCORD_JOIN:
                delay(500);
                int char_n = Serial.parseInt();
                Serial.print(str);
                led_discord_pulse(char_n);
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
