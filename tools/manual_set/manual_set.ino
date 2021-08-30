#define RLED 11
#define GLED 10
#define BLED 9

struct {
        short r;
        short g;
        short b;
} ledColour;

inline void printCol() {
        char str[100];
        sprintf(str, "%d,%d,%d\n\r", ledColour.r, ledColour.g, ledColour.b);
        Serial.print(str);
}

void setup() {
        Serial.begin(9600);
        pinMode(RLED, OUTPUT);
        pinMode(GLED, OUTPUT);
        pinMode(BLED, OUTPUT);

        ledColour.r = 120;
        ledColour.g = 120;
        ledColour.b = 120;
}

void loop() {
        if (Serial.available()) {
                char in = Serial.read();
                switch(in) {
                case 'G':
                        if (ledColour.r + 10 <= 255) ledColour.r += 10;
                        break;
                case 'C':
                        if (ledColour.g + 10 <= 255) ledColour.g += 10;
                        break;
                case 'R':
                        if (ledColour.b + 10 <= 255) ledColour.b += 10;
                        break;
                case 'H':
                        if (ledColour.r - 10 >= 0) ledColour.r -= 10;
                        break;
                case 'T':
                        if (ledColour.g - 10 >= 0) ledColour.g -= 10;
                        break;
                case 'N':
                        if (ledColour.b - 10 >= 0) ledColour.b -= 10;
                        break;
                default:
                        break;
                }
                printCol();
        }
        analogWrite(RLED, ledColour.r);
        analogWrite(GLED, ledColour.g);
        analogWrite(BLED, ledColour.b);
}



                        
