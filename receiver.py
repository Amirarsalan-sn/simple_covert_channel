import pyperclip
import math
from time import sleep

"""
0 -> space character
1 -> tab character 
format of the packets appended at the end of the last data in the clipboard:
8 bits of random sequence, 8 bits of data(one byte), 8 bits of control chars.
control chars:
  0     1       2      3 4 5 6 7
start  end   received  zeros(maybe packet id for correct transportation of data -> future updates).

this script, reads the clipboard periodically and whenever it see's the pattern specified by random_sequence
and the start flag as '1', it reads the clipboard continuously and sets the received flag accordingly
"""
random_sequence = '\t \t \t \t '  # -> 1 0 1 0 1 0 1 0


def convert_num_code(number):
    result = ''
    digits = 8
    digits -= 1
    while digits >= 0:
        if (number >> digits) % 2 == 0:
            result += ' '
        else:
            result += '\t'
        digits -= 1

    return result


def convert_code_num(code: str):
    num = 0
    for index in range(0, 8):
        if code[index] == '\t':
            num += 2 ** (7-index)
    return num


while True:
    buffer = ''
    state = 'pending'
    print('waiting for message')
    while True:
        curr_clip = pyperclip.paste()
        if len(curr_clip) < 24:
            continue
        curr_len = len(curr_clip)
        enc_m = curr_clip[curr_len - 24: curr_len]
        if enc_m[0:8] == random_sequence:
            if enc_m[18] == '\t': # the sender is not aware of receiver's receive still.
                sleep(0.001)
                continue
            if enc_m[16] == '\t' and state == 'pending':  # it's a starting message.
                buffer += chr(convert_code_num(enc_m[8:16]))
                enc_m = enc_m[:18] + '\t' + enc_m[19:]

                pyperclip.copy(curr_clip[:curr_len-24] + enc_m)
                state = 'start'
                #print(buffer)
                continue
            elif enc_m[16] == ' ' and enc_m[17] == ' ' and state == 'start':  # it's still transmitting.
                buffer += chr(convert_code_num(enc_m[8:16]))
                enc_m = enc_m[:18] + '\t' + enc_m[19:]

                pyperclip.copy(curr_clip[:curr_len-24] + enc_m)
                #print(buffer)
                continue
            elif enc_m[17] == '\t':  # this is the last packet.
                buffer += chr(convert_code_num(enc_m[8:16]))
                enc_m = enc_m[:18] + '\t' + enc_m[19:]

                pyperclip.copy(curr_clip[:curr_len-24] + enc_m)
                state = 'pending'
                #print(buffer)
                print(f'read a message: {buffer}')
                if buffer.startswith('ceq'):  # time to change the random sequence.
                    buffer = int(buffer.split(':')[1])
                    random_sequence = convert_num_code(buffer)
                break

        sleep(0.001)

