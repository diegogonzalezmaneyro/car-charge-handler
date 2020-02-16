#-------------------------------------------------------------------------------
# Name:        open_evse
# Purpose:     Read RFID tag and checks webservice for activating open ovse.
#
# Author:      Proyecto UCU - SimpleTech
#
# Created:     07.06.2019
# Copyright:   (c) proyecto D2V - 2019
# Licence:
#   ----------------------------------------------------------------------------
#   "LICENCIA" (Revision 1):
#   ----------------------------------------------------------------------------
#-------------------------------------------------------------------------------


##Librerias utlilizadas
import RPi.GPIO as GPIO
import time
import logging
import urllib2
import urllib
import re
import display
import nfc

#Define Maytag PINS & hardware button.
MYTG_EN_PIN=29
MYTG_AV_PIN=31
HRDWR_TEST_PIN=26
BUZZER_PIN=33

#Enable debug
DEBUG=True
#Enable console print
VERBOSE=True
#Service Payment URL example
#urlWashPayment = 'http://simpletech.com.uy/test-stwash/actualizar-credito.php'
#urlFundsQuery = 'http://simpletech.com.uy/test-stwash/consultar-credito.php'

urlWashPayment = ''
urlFundsQuery = ''

#Variables for application
boton_test_hw=0 #hardware button pressed
maytag_available_signal=1 #Maytag available
wsResponse=0 #Global variable for wsResponse.
responseGlobal="algo" #response fromw web payment

#Force not to check machine status.
forceMaytagAllwaysAvailable=0
#forceMaytagAllwaysAvailable=1

intWsResponse=1

def debug(message):
        logging.debug(message)

def onScreen(message):
        if(VERBOSE):
                print(message)

def logAndScreen(message):
                debug(message)
                onScreen(message)
				
				
if(DEBUG):
        logging.basicConfig(format='%(asctime)s %(message)s',filename='open_evse.log', level=logging.DEBUG)

def initGPio():
        GPIO.cleanup()
        #Pin definitions
        GPIO.setmode(GPIO.BOARD) # Use BCM GPIO numbers
        GPIO.setup(HRDWR_TEST_PIN,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Hardware Test
        GPIO.setup(MYTG_AV_PIN,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Maytag Available
        GPIO.setup(MYTG_EN_PIN,GPIO.OUT) #Maytag Enable
        #Inicializes Maytag_Enable=0
        GPIO.output(MYTG_EN_PIN,False)
        GPIO.setup(BUZZER_PIN,GPIO.OUT)
        GPIO.output(BUZZER_PIN,False)


def getMAC(interface='eth0'):
  # Return the MAC address of the specified interface
  try:
    str = open('/sys/class/net/%s/address' %interface).read()
  except:
    str = "00:00:00:00:00:00"
  return str[0:17]

#Variable readings
def readLoopInputs():
                global maytag_available_signal
                boton_test_hw=GPIO.input(HRDWR_TEST_PIN)
                maytag_available_signal=GPIO.input(MYTG_AV_PIN)
                print "Read Loop Inputs", maytag_available_signal

#Send 20ms pulse to maytag machine.
def sendEnablePulse():
                logAndScreen("Sending maytag enable pulse..")
                GPIO.output(MYTG_EN_PIN,True)
                time.sleep(24/1000.0)
                GPIO.output(MYTG_EN_PIN,False)
                logAndScreen("pulse sent")

#Web Service Call, returns value of contador.
def httpPostQuery(uid_read,service_url):
                #uuid_read="12345598787689"
                dispositivo=getMAC('eth0')
                response="4"
                try:
                                #query_args = { 'RFID':uid_read }
                                query_args = { 'RFID':uid_read, 'dispositivo':dispositivo }
                                logAndScreen("Post call to "+service_url)
                                data = urllib.urlencode(query_args)
                                request = urllib2.Request(service_url, data)
                                response = urllib2.urlopen(request).read()
                                logAndScreen("WSresponse: "+response)
                                wsResponseParsed=re.findall('\d+',response)
                                response=wsResponseParsed[0]                                
                except urllib2.HTTPError, e:
                                logAndScreen('Encontre un HTTPError = ' + str(e.code))
                except urllib2.URLError, e:
                                logAndScreen('Encontre un URLError = ' + str(e.reason))
                except:
                                logAndScreen('Web Service Call: Found  Generic exception')

                return response

#Loops until machine becomes available
def checkMaytagAvailable():
                global maytag_available_signal
                maytagLogGenerated=0
                print "funcion checkMaytagAvailable", maytag_available_signal
                while (maytag_available_signal==1):
                                #Maytag unavailable
                                display.print_lcd_message("maytagUnavailable")
                                if (maytagLogGenerated==0):
                                                logAndScreen("Maytag unavailable,gooing loop..")
                                                maytagLogGenerated=1

                                maytag_available_signal=GPIO.input(MYTG_AV_PIN)
                print "Exit Available Loop"

def sendWrongBeep():
		sendBeep()
                sendBeep()
		
def sendBeep():
		GPIO.output(BUZZER_PIN,True)
		time.sleep(200/1000.0)
		GPIO.output(BUZZER_PIN,False)
		time.sleep(200/1000.0)


#Checks if maytag is available.
def isMaytagAvailable():
		global maytag_available_signal
		global forceMaytagAllwaysAvailable
                maytag_available_signal=GPIO.input(MYTG_AV_PIN)
                logAndScreen("MaytagAvailable: "+ str(maytag_available_signal))
                if (maytag_available_signal==1):
                        result = False
                else:
                        result = True
                if (forceMaytagAllwaysAvailable==1):
			result = True
		return result

###### Main program ########
def main():
        # Initialization..
        logAndScreen( "service init..")
        initGPio()
        display.init()
        try:
                        #Main loop
                        while True:
                                        #input readings.
                                        readLoopInputs()
                                        #TODO: Check if machine available(active low pin signal.)
                                        #checkMaytagAvailable()
                                        #print "luego del chequeo",maytag_available_signal
                                        #If PASS, then machine is available, and wait until a valid card is passing throug.
                                        logAndScreen("Machine available, asking for card")
                                        display.print_lcd_message("passCard")
                                        uid_read=nfc.readNfc()
                                        logAndScreen("Card Read: "+uid_read)
                                        #check Maytag Available when user ask for washing.
                                        #checkMaytagAvailable()
                                        if (isMaytagAvailable()):
                                                logAndScreen("Verifying..")
                                                display.print_lcd_message("verifying")
                                                ws_response=httpPostQuery(uid_read,urlFundsQuery)
                                                response=int(float(ws_response))
                                                ##Depending on web response..
                                                if (response==4):
                                                        display.print_lcd_message("netwokError")
							sendWrongBeep()
                                                        time.sleep(5)
                                                elif(response==2):
                                                        display.print_lcd_message("unasociatedCard")
                                                        sendWrongBeep()
                                                        time.sleep(5)
                                                elif(response==1):
                                                        display.print_lcd_message("invalidCard")
							sendWrongBeep()
                                                        time.sleep(5)
                                                elif(response==3):
                                                        display.print_lcd_message("noFounds")
							sendWrongBeep()
                                                        time.sleep(5)
                                                elif (response>=0): #When founds are enogh
                                                        display.print_verification_message(response)
                                                        sendBeep()
                                                        logAndScreen("Waiting for confirmation..")
                                                        uuid2=nfc.readNfcTOut()
                                                        logAndScreen("UUID2 Read: " + uuid2)
                                                        if (uuid2==uid_read):
                                                                display.print_lcd_message("authorizing")
                                                                ws_response=httpPostQuery(uid_read,urlWashPayment)
                                                                response=int(float(ws_response))
                                                                ##Depending on web response, the results to the machine.
                                                                if (response==2):
                                                                        display.print_lcd_message("unasociatedCard")
                                                                        sendWrongBeep()   
                                                                        time.sleep(5)
                                                                elif (response==4):
                                                                        display.print_lcd_message("networkError")
                                                                        sendWrongBeep()
                                                                        time.sleep(5) 
                                                                elif(response==1):
                                                                        display.print_lcd_message("invalidCard")
                                                                        sendWrongBeep()    
                                                                        time.sleep(5)
                                                                elif(response==3):
                                                                        display.print_lcd_message("noFounds")
                                                                        sendWrongBeep()
                                                                        time.sleep(5)
                                                                elif (response>=0):
                                                                        sendEnablePulse()
                                                                        display.print_auth_message(response)
									sendBeep()
                                                                        time.sleep(180)
                                                                else:
                                                                        display.print_lcd_message("internalError")
									sendWrongBeep()
                                                                        time.sleep(5)
                                                else:
                                                        display.print_lcd_message("internalError")
                                                        sendWrongBeep()
                                                        time.sleep(5)
                                        else:
                                                #Maytag unavailable
                                                logAndScreen("Maytag Unavailable")
                                                display.print_lcd_message("maytagUnavailable")
                                                sendWrongBeep()
                                                time.sleep(5)


        except KeyboardInterrupt:
                logAndScreen("ctrl plus c pressed, service down..")
                GPIO.cleanup()

        #except :
        #       logAndScreen("Main loop exception")
        #       GPIO.cleanup()

        GPIO.cleanup()


main()
