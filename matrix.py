from typing import List, Dict, Optional
from time import sleep

import numpy as np

from letters import LETTERS, SYMBOLS

from rpi_ws281x import *

class Strip:
    ...

class TestStrip(Strip):
    def __init__(self, length: int, connected: bool, loc=None):
        self.connected = connected
        self.length = length
        self.loc = loc

        self.arr = None
        if self.connected:
            self.arr = [" " for i in range(length*2)]
        else:
            self.arr = [" " for i in range(length)]

    def fill(self, idx: int, *args):
        self.arr[idx] = args[0]


    def __str__(self):
        if self.connected:
            if self.loc == "top":
                return f"{[a for a in reversed(self.arr[self.length:])]}\n{[a for a in self.arr[:self.length]]}"

            elif self.loc == "bottom":
                return f"{[a for a in self.arr[:self.length]]}\n{[a for a in reversed(self.arr[self.length:])]}"

        return f"{[a for a in self.arr]}"


class LetterBuff:
    def __init__(self, length: int=16, height: int=5):
        self.length = length
        self.height = height
        self.matrix_buff = np.array([[" " for _ in range(self.length)] for _ in range(self.height)])

        self.letter_buff = []

    def clear_matrix(self):
        self.matrix_buff = np.array([[" " for _ in range(self.length)] for _ in range(self.height)])
        self.letter_buff = []

    def push_letters(self, letters: str):
        # if len(letters) == 0:
        #     self.letter_buff = [np.array([[" "] for _ in range(self.height)])] + self.letter_buff

        for l in letters:
            letter = np.array(LETTERS[l])

            for i in range(len(letter[0])):
                self.letter_buff = [letter[:, i:i+1]] + self.letter_buff

    def advance_letters(self, step=1):
        for _ in range(step):
            if len(self.letter_buff) == 0:
                self.letter_buff = [np.array([[" "] for _ in range(self.height)])] + self.letter_buff

            self.matrix_buff = np.concatenate((self.matrix_buff[:, 1:], self.letter_buff.pop(-1)), axis=1)

    def show_symbol(self, symbol: str, skew="left"):
        self.clear_matrix()

        symbol_matrix = np.array(SYMBOLS[symbol])

        padding_length = int((self.length - len(symbol_matrix[0]))/2)
        extra_length = (self.length - len(symbol_matrix[0]))%2

        temp_matrix_buff = np.concatenate(
            (self.matrix_buff[:, :padding_length], symbol_matrix, self.matrix_buff[:, padding_length:]),
            axis=1
        )

        if extra_length > 0:
            temp_matrix_buff = np.concatenate(
                (self.matrix_buff[:, :extra_length], temp_matrix_buff) \
                if skew == "left" else \
                (temp_matrix_buff, self.matrix_buff[:, :extra_length]),
                axis=1
            )

        self.matrix_buff = temp_matrix_buff

    def show_letters(self, letters: str, skew="left"):
        self.clear_matrix()

        letters_length = sum([len(LETTERS[l][0]) for l in letters])
        letters_matrix = np.concatenate(
            [np.array(LETTERS[l]) for l in letters],
            axis=1
        )

        if letters_length > self.length:
            return  # too long

        padding_length = int((self.length - letters_length)/2)
        extra_length = (self.length - letters_length)%2

        temp_matrix_buff = np.concatenate(
            (self.matrix_buff[:, :padding_length], letters_matrix, self.matrix_buff[:, padding_length:]),
            axis=1
        )

        if extra_length > 0:
            temp_matrix_buff = np.concatenate(
                (self.matrix_buff[:, :extra_length], temp_matrix_buff) \
                if skew == "left" else \
                (temp_matrix_buff, self.matrix_buff[:, :extra_length]),
                axis=1
            )

        self.matrix_buff = temp_matrix_buff


class Matrix:
    def __init__(self, strips: List[Strip], length: int=16, connected: bool=False):
        self.strips = strips
        self.height = len(strips) + (1 if connected else 0)
        self.length = length
        self.connected = connected

        self.letter_buff = LetterBuff()
        
    # Define functions which animate LEDs in various ways.
    def colorWipe(self, strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
            strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChase(self, strip, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, color)
                strip.show()
                time.sleep(wait_ms/1000.0)
                #for i in range(0, strip.numPixels(), 3):
                #    strip.setPixelColor(i+q, 0)

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def rainbow(self, strip, color, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((i+j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
    
    def rainbowCycle(self, strip, color, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms/1000.0)

    def theaterChaseRainbow(self, strip, color, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, strip.numPixels(), 3):
                    strip.setPixelColor(i+q, wheel((i+j) % 255))
                strip.show()
                time.sleep(wait_ms/1000.0)
                #for i in range(0, strip.numPixels(), 3):
                #    strip.setPixelColor(i+q, 0)
                
    def showMatrix(self, func, matrix, color=None, sync=True):

        if sync:
            threads = []
            for strip in self.strips:
                threads.append(
                    Thread(target=func, args=(strip, color,))
                )

            list(map(lambda t: t.start(), threads))
            list(map(lambda t: t.join(), threads))

        else:
            for strip in self.matrix:
                func(strip, color)

        for strip in self.matrix:
            self.colorWipe(strip, Color(0,0,0), 10)


    def set_color(self, row: int, col: int, args: List=[]):
        
        if self.connected:  # first + last row loops around
            if row == 0:
                #return self.strips[0].fill(self.length*2 - 1 - col, *args)
                #print(row, self.length + col)
                
                return self.strips[0].setPixelColor(self.length + col, args[0])

            #elif row == self.height-1:
            #    return self.strips[-1].fill(self.length*2 - 1 - col, *args)

            #return self.strips[row-1].fill(col, *args)
            print(row-1, col)
            return self.strips[row-1].setPixelColor(col, args[0])

        return self.strips[row-1].setPixelColor(col, args[0])

    def set_matrix(self):
        for i, row in enumerate(self.letter_buff.matrix_buff):
            for j, col in enumerate(row):
                if col == "0":
                    self.set_color(i, j, [Color(255, 0, 0)])

    def clear_matrix(self):
        print(self.height)
        for i in range(self.height):
            for j in range(self.length):
                self.set_color(i, j, [Color(0, 0, 0)])
                
        self.print_matrix()

    def push_letters(self, *args, **kwargs):
        self.letter_buff.push_letters(*args, **kwargs)

    def clear_letters(self, *args, **kwargs):
        self.letter_buff.clear_matrix()

    def show_letters(self, *args, **kwargs):
        self.letter_buff.show_letters(*args, **kwargs)

    def show_symbol(self, *args, **kwargs):
        self.letter_buff.show_symbol(*args, **kwargs)

    def advance_letters(self, step=1):
        self.letter_buff.advance_letters(step)

    def print_matrix(self):
        # for i in range(self.height):
        #     print("\033[A \033[A", end="")
        #     if i != self.height-1:
        #         print("                                                          ", end="")

        for s in self.strips:
            #print(str(s), end="\n")
            s.show()

        #print("\n\n")

        #sleep(0.8)


from rpi_ws281x import *

# LED strip configuration:
LED_COUNT      = 16     # Number of LED pixels.
#LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 65      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
#LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53



if __name__=="__main__":
    strips = [
        Adafruit_NeoPixel(LED_COUNT*2, 10, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0),
        Adafruit_NeoPixel(LED_COUNT, 12, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0),
        Adafruit_NeoPixel(LED_COUNT, 19, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1),
        Adafruit_NeoPixel(LED_COUNT, 21, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0),
    ]
    list(map(lambda s: s.begin(), strips))

    matrix = Matrix(strips, connected=True)
    


    for i in range(0, 100):
        sleep(1)
        if i < 10:
            matrix.clear_matrix()
            matrix.set_color(0, i, [Color(255,0,0)])
            matrix.set_color(1, i, [Color(255,0,0)])
            matrix.set_color(2, i, [Color(255,0,0)])
            matrix.set_color(3, i, [Color(255,0,0)])
            matrix.set_color(4, i, [Color(255,0,0)])
            matrix.print_matrix()

        elif i == 10:
            matrix.clear_matrix()
            matrix.push_letters("ABCD")
            matrix.print_matrix()

        elif 10 < i < 40:
            matrix.clear_matrix()
            matrix.advance_letters()
            matrix.set_matrix()
            matrix.print_matrix()

        elif 40 <= i < 43:
            matrix.clear_matrix()
            matrix.show_letters("HELLO")
            matrix.set_matrix()
            matrix.print_matrix()

        elif 43 <= i < 60:
            matrix.clear_matrix()
            if i % 2 == 1:
                matrix.show_symbol("bigeye")
            else:
                matrix.show_symbol("bigeyeblink")
            matrix.set_matrix()
            matrix.print_matrix()

        elif  60 <= i:
            matrix.clear_matrix()
            if i % 2 == 1:
                matrix.show_symbol("bigeyeleft")
            else:
                matrix.show_symbol("bigeyeright")
            matrix.set_matrix()
            matrix.print_matrix()



    # matrix.set_color(0, 6, ["0"])
    # matrix.set_color(1, 5, ["0"])
    # matrix.set_color(2, 5, ["0"])
    # matrix.set_color(3, 5, ["0"])
    # matrix.set_color(4, 6, ["0"])
    # matrix.print_matrix()
    # matrix.clear_matrix()

    # matrix.set_color(0, 5, ["0"])
    # matrix.set_color(1, 5, ["0"])
    # matrix.set_color(2, 5, ["0"])
    # matrix.set_color(3, 5, ["0"])
    # matrix.set_color(4, 5, ["0"])
    # matrix.print_matrix()

    # lbuff = LetterBuff()

    # for i in range(50):
    #     if i == 0 or i == 10:
    #         lbuff.push("ABCD")
    #     else:
    #         lbuff.push()

    #     print(lbuff.advance(), end="\n\n")
