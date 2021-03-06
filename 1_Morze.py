import time
import board
import digitalio

led = digitalio.DigitalInOut(board.GP5)
led.direction = digitalio.Direction.OUTPUT

# Creating a dictionary of letters
dict_letters = {
    'a': [True, False, True, True, True, False],
    'b': [True, True, True, False, True, False, True, False, True, False],
    'c': [True, True, True, False, True, False, True, True, True, False, True, False],
    'd': [True, True, True, False, True, False, True, False],
    'e': [True, False],
    'f': [True, False, True, False, True, True, True, False, True, False],
    'g': [True, True, True, False, True, True, True, False, True, False],
    'h': [True, False, True, False, True, False, True, False],
    'i': [True, False, True, False],
    'j': [True, False, True, True, True, False, True, True, True, False, True, True, True, False],
    'k': [True, True, True, False, True, False, True, True, True, False],
    'l': [True, False, True, True, True, False, True, False, True, False],
    'm': [True, True, True, False, True, True, True, False],
    'n': [True, True, True, False, True, False],
    'o': [True, True, True, False, True, True, True, False, True, True, True, False],
    'p': [True, False, True, True, True, False, True, True, True, False, True, False],
    'q': [True, True, True, False, True, True, True, False, True, False, True, True, True, False],
    'r': [True, False, True, True, True, False, True, False],
    's': [True, False, True, False, True, False],
    't': [True, True, True, False],
    'u': [True, False, True, False, True, True, True, False],
    'v': [True, False, True, False, True, False, True, True, True, False],
    'w': [True, False, True, True, True, False, True, True, True],
    'x': [True, True, True, False, True, False, True, False, True, True, True, False],
    'y': [True, True, True, False, True, False, True, True, True, False, True, True, True, False],
    'z': [True, True, True, False, True, True, True, False, True, False, True, False],
    '1': [True, False, True, True, True, False, True, True, True, False, True, True, True, False, True, True, True, False],
    '2': [True, False, True, False, True, True, True, False, True, True, True, False, True, True, True, False],
    '3': [True, False, True, False, True, False, True, True, True, False, True, True, True, False],
    '4': [True, False, True, False, True, False, True, False, True, True, True, False],
    '5': [True, False, True, False, True, False, True, False, True, False],
    '6': [True, True, True, False, True, False, True, False, True, False, True, False],
    '7': [True, True, True, False, True, True, True, False, True, False, True, False, True, False],
    '8': [True, True, True, False, True, True, True, False, True, True, True, False, True, False, True, False],
    '9': [True, True, True, False, True, True, True, False, True, True, True, False, True, True, True, False, True, False],
    '0': [True, True, True, False, True, True, True, False, True, True, True, False, True, True, True, False, True, True, True, False],
    ' ': [False, False]}  

# Function, that helps checking the spelling
def spellcheck(message):
    spelling=1
    for i in range (len(message)):
        if message[i] in dict_letters:
            continue
        else: 
            print("Invalid symbol: '", message[i], "'")
            print("Please, try again.")
            spelling=0
            break
    return(spelling)

# The main script
while True:
    message=[char for char in input("\nPrint your text here (please, use english letters and numbers only):\n").lower()]
    spell = spellcheck(message)
    if spell == 1: 
        for i in range(len(message)):
            bukva=dict_letters[message[i]]
            for j in range(len(bukva)):
                print(int(bukva[j]), end='')
                led.value = bukva[j]
                time.sleep(1)
            print('00', end='')
            time.sleep(2)
