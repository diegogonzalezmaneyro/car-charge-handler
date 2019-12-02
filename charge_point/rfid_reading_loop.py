##Libs
import RPi.GPIO as GPIO
import time
import nfc

def save_rfid_txt(rfid):
        line_to_save = '{};{}\n'.format(rfid,time.time())
        file = open('rfid_inputs.txt', 'a')
        file.write(line_to_save)
        file.close()

###### Main program ########
def main():
        # Initialization..
        print( "Reading loop...")
        try:
                #Main loop
                while True:
                        print("asking for card")
                        uid_read=nfc.readNfc()
                        save_rfid_txt(uid_read)
        except KeyboardInterrupt:
                print("ctrl plus c pressed, service down..")

main()
