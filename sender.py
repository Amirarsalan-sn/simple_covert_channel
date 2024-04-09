import pyperclip
import random
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
"""
random_sequence = '\t \t \t \t '  # -> 1 0 1 0 1 0 1 0
new_random_sequence = 0
previous_clipboard = ''


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


def random_seq_gen():
    global new_random_sequence
    random_seq = random.randint(0, 256)
    new_random_sequence = random_seq


def send_message(message: str, index: int):
    control_char = 8 * ' '
    global random_sequence
    global previous_clipboard
    enc_m = random_sequence
    enc_m = enc_m + convert_num_code(ord(message[index]))
    if i == 0:  # this is the first message so the 'start' flag should be 1.
        control_char = '\t' + 7 * ' '
    if i == len(message) - 1:  # this is the last message so the 'end' flag should be set.
        control_char = ' ' + '\t' + 6 * ' '
    enc_m = enc_m + control_char
    current_clipboard = pyperclip.paste()
    if current_clipboard[:len(current_clipboard) - 24] == previous_clipboard:
        new_clipboard = previous_clipboard + enc_m
    else:
        new_clipboard = current_clipboard + enc_m
        previous_clipboard = current_clipboard
    pyperclip.copy(new_clipboard)


ceq_mode = False
while True:
    state = 'send'
    time_out_number = 0
    time_out_limit = 1000
    if ceq_mode:
        random_sequence = convert_num_code(new_random_sequence)
        ceq_mode = False
    m = input('Enter message: ')
    if m == 'ceq':  # in this protocol, you can change the random sequence number with this command (Change SEQuence).
        random_seq_gen()
        m = m + ':' + str(new_random_sequence)
        ceq_mode = True
    if len(m) == 0:
        continue
    time_out = False
    for i in range(len(m)):
        if time_out:
            break
        #print(f'sending {m[i]}')
        send_message(m, i)
        state = 'wait'
        time_out_number = 0
        while state == 'wait':
            curr_clip = pyperclip.paste()
            clipboard_enc = curr_clip[len(curr_clip) - 24:len(curr_clip)]
            if clipboard_enc[0:8] == random_sequence:
                if clipboard_enc[18] == '\t':
                    state = 'sending'

            sleep(0.001)
            time_out_number += 1
            if time_out_number == time_out_limit:
                print('time out reached, try to send the message again.')
                time_out = True
                break
    pyperclip.copy(previous_clipboard)
