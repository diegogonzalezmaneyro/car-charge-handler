import time

rfid = str(input("ingrese RFID tag:"))
line_to_save = '{};{}\n'.format(rfid,time.time())

with open('rfid_inputs.txt', 'a') as file:
    file.write(line_to_save)
