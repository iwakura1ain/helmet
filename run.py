from matrix import Matrix, Strip, TestStrip
from random import randint
from time import sleep

#import keyboard
import threading
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


STRIPS = [
    Adafruit_NeoPixel(LED_COUNT*2, 10, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0),
    Adafruit_NeoPixel(LED_COUNT, 12, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0),
    Adafruit_NeoPixel(LED_COUNT, 19, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 1),
    Adafruit_NeoPixel(LED_COUNT, 21, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, 0),
]
list(map(lambda s: s.begin(), STRIPS))

MATRIX = Matrix(STRIPS, connected=True)

EVENT = threading.Event()

def show_heart(m, e):
    i = 0
    while not e.is_set():
        m.clear_matrix()
        if i % 2 == 0:
            m.show_symbol("doubleheart")
        else:
            m.show_symbol("doubleheartwide")
        m.set_matrix()
        m.print_matrix()
        
        i += 1
        sleep(0.8)

def show_double_heart(m, e):
    m.clear_matrix()
    m.show_symbol("doubleheart")
    m.set_matrix()
    m.print_matrix()
    e.wait()

def bigeye_run(m, e):
    while not e.is_set():
        m.clear_matrix()
        action = randint(1, 17)

        if 5 <= action < 8:
            m.show_symbol("bigeyemidblink")
            m.set_matrix()
            m.print_matrix()
            sleep(0.1)

            m.clear_matrix()
            m.show_symbol("bigeyeblink")
            m.set_matrix()
            m.print_matrix()
            sleep(0.2)

        elif 8 <= action < 10:
            m.show_symbol("bigeyeleft")
            m.set_matrix()
            m.print_matrix()
            sleep(0.8)

        elif 10 <= action <12:
            m.show_symbol("bigeyeright")
            m.set_matrix()
            m.print_matrix()
            sleep(0.8)
        elif 12 <= action <14:
            m.show_symbol("bigeyedown")
            m.set_matrix()
            m.print_matrix()
            sleep(0.8)
            
        elif 14 <= action < 17:
            m.show_symbol("bigeyemidsmile")
            m.set_matrix()
            m.print_matrix()
            sleep(0.1)

            m.clear_matrix()
            m.show_symbol("bigeyesmile")
            m.set_matrix()
            m.print_matrix()
            sleep(0.8)

        
        else:
            m.show_symbol("bigeye")
            m.set_matrix()
            m.print_matrix()
            sleep(0.5)

def okay(m, e):
    m.letter_buff.clear_matrix()
    m.clear_matrix()
    m.show_letters("OKAY")
    m.set_matrix()
    m.print_matrix()
    e.wait()

def no(m, e):
    m.letter_buff.clear_matrix()
    m.clear_matrix()
    m.show_letters("NO")
    m.set_matrix()
    m.print_matrix()
    e.wait()

def yes(m, e):
    m.letter_buff.clear_matrix()
    m.clear_matrix()
    m.show_letters("YES")
    m.set_matrix()
    m.print_matrix()
    e.wait()

def hello(m, e):
    m.letter_buff.clear_matrix()
    m.clear_matrix()
    m.show_letters("HELLO")
    m.set_matrix()
    m.print_matrix()
    e.wait()


THREAD = None
EVENTS = {
    "1": bigeye_run,
    "2": show_heart,
    "3": show_double_heart,
    "h": hello,
    "y": yes,
    "n": no,
    "o": okay
}


def on_key_press(event):
    global THREAD
    global EVENT
    global MATRIX
    
    PRINT(f"EVENT: {event.name}")

    target_func = EVENTS.get(event.name, bigeye_run)

    EVENT.set()

    if THREAD is not None:
        THREAD.join()

    EVENT.clear()
    THREAD = threading.Thread(target=target_func, args=(MATRIX, EVENT,))
    THREAD.start()


#from sshkeyboard import listen_keyboard

def press(key):
    global THREAD
    global EVENT
    global MATRIX
    
    print(f"EVENT: {key}")

    target_func = EVENTS.get(key, bigeye_run)

    EVENT.set()
    
    if THREAD is not None:
        THREAD.join()


    EVENT.clear()
    THREAD = threading.Thread(target=target_func, args=(MATRIX, EVENT,))
    print(f"here")
    THREAD.start()

    print(f"here2")

def release(key):
    print(f"'{key}' released")

bigeye_run(MATRIX, EVENT)

#listen_keyboard(
#    on_press=press,
#    on_release=release,
#)