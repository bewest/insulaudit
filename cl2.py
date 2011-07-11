#!/usr/bin/python
import user

import struct
import sys
import serial
import time
import logging
from pprint import pprint, pformat

from insulaudit.core import Command
from insulaudit.clmm.usbstick import *
from insulaudit import lib

logging.basicConfig( stream=sys.stdout )
log = logging.getLogger( 'auditor' )
log.setLevel( logging.DEBUG )
log.info( 'hello world' )
io  = logging.getLogger( 'auditor.io' )
io.setLevel( logging.DEBUG )

"""
######################
#
# ComLink2
# pseudocode analysis of critical procedures
# there is some implicit OO going on
#
execute(command):
  command.execute(self)

getSignalStrength:
  result = readSignalStrength()
  signal = result[0]

readSignalStrength:
  result = sendComLink2Command(6, 0)
  # result[0] is signal strength
  return result

initCommunicationsIO:
  # close/open serial
  readProductInfo( )
  readSignalStrength()

endCommunicationsIO:
  readSignalStrength()
  readInterfaceStatistics()
  # close port

readProductInfo():
  result = sendComLink2Command(4)
  # 1/0/255
  freq   = result[5]
  # decodeInterface stats

readInterfaceStatistics:
  result = sendComLink2Command(5, 0)
  result = sendComLink2Command(5, 1)
  # decode and log stats

sendComLink2Command(msg):
  # generally commands are 3 bytes, most often CMD, 0x00, 0x00
  serial.write(msg)
  return checkAck()
  # throw local usb exception

readStatus:
  result         = sendComLink2Command(3)
  commStatus     = result[0] # 0 indicates success
  status         = result[2]
  lb, hb         = result[3], result[4]
  bytesAvailable = makeInt(lb, hb)
  return (status & 0x1) > 0 ? bytesAvailable : 0

checkAck:
  time.sleep(.100)
  result     = serial.read(64)
  commStatus = result[0]
  # usable response
  assert commStatus == 1
  status     = result[1]
  # status == 102 'f' NAK, look up NAK
  if status == 85 # 'U'
    return result[3:]

calcRecordsRequired(length):
  if length > 64:
    return 2
  return 1


############################
#
# USB(Pump) Command Stuff
#

execute:
  allocateRawData()
  sendAndRead()

sendAndRead:
  sendDeviceCommand()
  if dataToCollect > 0 && !isHaltRequested():
    command.data = readDeviceData()

sendDeviceCommand:
  packet = buildTransmitPacket()
  serial.write(packet)
  if code != 93 || params[0] != 0:
    checkAck()

allocateRawData():
  bufferSize = bytesPerRecord * maxRecords

readDeviceData():
  eod     = False
  results = [ ]
  while not eod and !isHaltRequested():
    data = readDeviceDataIO( )
    results.extend(data)
  return results

readDeviceDataIO():
  results = readData()
  lb, hb  = results[5] & 0x7F, results[6]
  eod = (results[5] & 0x80) > 0
  resLength = makeInt(lb, hb)
  if resLength < 64:
    # throw error
  data = result[13:]
  assert data.length == resLength
  crc = result[-1]
  # crc check
  assert data[0] == CRC8(data)
  return data

readData():
  bytesAvailable = getNumBytesAvailable()
  packet = [12, 0, HighByte(bytesAvailable), LowByte(bytesAvailable)]
  packet.appcend( CRC8(packet) )

  response = writeAndRead(packet, bytesAvailable)
  # assert response.length > 14
  response[0] == 2
  # response[1] !=0 # interface number !=0
  # response[2] == 5 # timeout occurred
  # response[2] == 2 # NAK
  # response[2] # should be within 0..4
  return response

getNumBytesAvailable:
  bytes = readStatus( )
  timer.start()
  while bytesa == 0 and timer.length < 1:
    bytes = readStatus( )
    time.sleep(.100)
  return bytes

buildTransmitPacket:
  # 16 bytes + params
  # should have > 0 params
  paramsCount = commParams.length
  head   = [ 1, 0, 168, 1 ]
  # serial
  packet = head + serial
  # paramCount 2 bytes
  packet.extend( [ (0x80 | HighByte(paramsCount)), LowByte(paramsCount) ] )
  # not sure what this byte means
  button = 0
  # special case command 93
  if code == 93:
    button = 85
  packet.append(button)
  packet.append(maxRetries)
  # how many packets/frames/pages/flows will this take?
  responseSize = calcRecordsRequired(expectedLength)
  # really only 1 or 2?
  pages = responseSize
  if responseSize > 1:
    pages = 2
  packet.append(pages)
  packet.append(0)
  # command code goes here
  packet.append(code)
  packet.append(CRC8(packet))
  packet.extend( [ params, CRC8(params) ] )
  return packet

packSerialNumber:
  return makePackedBCD(serial)
"""

"""
######################
#
# Pump
#
initDevice:
  # cmdPowerControl
  # cmdReadErrorStatus
  # cmdReadState
  # cmdReadTempBasal
  initDevice2

iniDevice2:
  detectActiveBolus

detectActiveBolus:
  # cmdDetectBolus

shutDownPump
  if suspended:
    shutDownPump2()
    cmdCancelSuspend()
  # turn rf power off
  # retries 0
  cmdOff = Command(93, "rf power off", [ 0 ], 2)
  cmdOff.execute

shutDownPump2:
  Command(91, "keypad push (ack)", [ 2 ], 1).execute
  time.sleep(.500)
  Command(91, "keypad push (esc)", [ 1 ], 1).execute
  time.sleep(.500)

getNAKDescription:
  # pass

Command(code, descr)
  return Command(code, descr, 64, 1, 0)

Command(code, descr, params, tail)
  com =  Command(code, descr, 0, 1, 11)
  com.params = params
  #com.paramCount


execute:
  result = None
  for i in xrange(maxRetries)
    # reset bytes read
    response  = usb.execute(self)
    # handle stack trace
    if response: break
  return result


"""

if __name__ == '__main__':
  io.info("hello world")

  port = None
  try:
    port = sys.argv[1]
  except IndexError, e:
    print "usage:\n%s /dev/ttyUSB0" % sys.argv[0]
    sys.exit(1)
    
  #link = Link(port)
  #link.initUSBComms()
  #pprint( carelink( USBProductInfo(      ) ).info )


#####
# EOF
