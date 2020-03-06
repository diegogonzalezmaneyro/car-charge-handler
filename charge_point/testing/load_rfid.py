# # read a text file as a list of lines
# # find the last line, change to a file you have
# fileHandle = open ( 'test3.txt',"r" )
# lineList = fileHandle.readlines()
# fileHandle.close()
# print lineList
# print "The last line is:"
# print lineList[len(lineList)-1]
# # or simply
# print lineList[-1]
import time
WAITING_TIME = 10 #secs
with open('rfid_inputs.txt', 'r') as file:
    a = file.readlines()
aux = a[-1].split(';')
if (time.time()-float(aux[-1]))<WAITING_TIME:
    print(aux[0])
else:
    print(0)
