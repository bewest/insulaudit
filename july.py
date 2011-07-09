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
log.setLevel( logging.FATAL )
log.info( 'hello world' )
io  = logging.getLogger( 'auditor.io' )
io.setLevel( logging.DEBUG )

"""

#####################
#
# Pump Stuff
#
 The Pump Packet looks like this:
 7 bytes with parameters on the end
 00     167
 01     serial[ 0 ]
 02     serial[ 1 ]
 03     serial[ 2 ]
 04     commandCode
 05     sequenceNumber or paramCount
 06     [ parameters ]
 06/07  CRC8(packet)

 or:
 167, serial, code, seq/param, params, CRC8(packet)
NB the whole thing is wrapped by encodeDC()

get ACK packet: is:
packet = [ 167 ] + serial + [ 6, 0 ]
packet.append(CRC8(packet))


sendAck:
  ack_pack = ACK

  com_command = [ 5, ack_pack.length ]
  serial.write(com_command + ack_pack)
  usb.readAckByte, turn off RF?
  usb.readReadyByte

checkAck:
  bytesAvail = usb.readStatus( )
  usb.sendTransferDataCommand( ) # exec read data flow on usb
  response = serial.read( )
  ack = decodeDC(response)
  # can check header and CRC of response
  # should match the previously sent command
  ackBytes[4] == 6 # command ACK ok
  error = lookup_error(ackBytes[5])

initDevice:
  cmdPowerControl.execute()
  readPumpModelNumber.execute()
  cmdReadError.execute()
  cmdReadState.execute()
  cmdReadTmpBasal.execute()
  
initDeviceAfterModelNumberKnown()
  bolus = detectActiveBolus()
  if !bolus:
    cmdSetSuspend.execute()

detectActiveBolus:
  cmdDetectBolus.execute()
  # make sure it worked

shutdownPump
  cmdCancelSuspend.execute()

execute:
  # retry 3 times
  # if not ready, do usb.initCommunications
  executeIO()

executeIO:
  if paramCount > 0:
    packet = makeCommandPacket()
    packet.executeIO()
  
  if paramCount > 128:
    data = makeDataPacket(1, 1, 64)
    data.sendAndRead()

    data = makeDataPacket(2, 2, 64)
    data.sendAndRead()

    data = makeDataPacket(3, 131, 16)
    data.sendAndRead()
  elsif paramCount > 64:
    data = makeDataPacket(1, 1, 64)
    data.sendAndRead()

    data = makeDataPacket(2, 130, 32)
    data.sendAndRead()
  else:
    # special case commandCode == 64
    sendAndRead()

sendAndRead:
  sendCommand
  if expectedLength > 0 and !isHaltRequested():
    if pages
      data = readDeviceDataPage(length)
    else:
      data = readDeviceData()
      bytesRead += data.length
  else
    if commandParams.length > 0:
      # setState(7)
      bytesRead += commandParams.length
      
      checkAck()

sendCommand
  packet = buildPacket()
  usbCmd = 0
  if isUseMultiXmitMode():
    usbCmd = 10
  elsif paramCount == 0:
    usbCmd = 5
  else:
    usbCmd = 4
  usbCmd = [ usbCmd, packet.length ]
  command = usbCmd + packet
  serial.write(command)
  usb.readAckByte()
  # special case command 93 and paramCount == 0
  # needs to be sensitive to timeout
  usb.readReadyByte(usbCmd[0] == 4)

checkHeaderAndCRC(deviceData):
  # check CRC8
  # check serial number


readDeviceDataPage(expectedBytes):


"""

"""

##########
#
# USB Device
#

readDeviceData:
  bytesAvail = usb.readStatus( )
  usb.sendTransferDataCommand( ) # exec read data flow on usb
  response = decodeDC(serial.read( ))
  ack = usb.readAckByte
  if (ack) throw IOException
  checkHeaderCRC(response)
  response[5] is NAK (21) # look up NAK
  if response[4] != commandCode # throw Error
  dataLen = response[5] # length
  cpyLen = len(response) - 6 - 1
  return response[6:-1]

initUSBComms
  # clear the buffer
  serial.readUntilEmpty( )
  # set RS232 MODE On
  # check success, first byte == 51 READY
  sendCommandCheckReply(6, 51)
  numOldBytes = readStatus( )
  if numOldBytes > 0:
    sendTransferDataCommand( )
    message = serial.read( )
    usb.readAckByte()
  
readAckByte:
  # retries twice
  serial.read(1) == 'U' # 85
  # else NAK == 'f' # 102

readStatus:
  # sets m_status, used to decode receivedByteCount, hasData, RS232Mode,
  # FilterRepeat, AutoSleep, Status Error, SelfTestError
  self.status = sendCommandGetReply(2)
  bytesAvailable = serial.read(1)
  readAckByte() # serial.read(1) == ACK
  
sendCommandGetReply:
  sendCommand(command)
  return serial.read(1)

sendCommandCheckReply(command, expect):
  # retries twice
  reply = sendCommandGetReply(command)
  return reply == expect

sendCommand(command):
  serial.write(command)

setRfMode:
  sendCommand(7)
  # sleep
  readAckByte()

readReadyByte(setRFMode):
  #retries twice
  readReadyByteIO(setRFMode)
  # adjust sleep timing

readReadyByteIO(setRFMode)
  # for some reason this is tightly coupled
  if setRfMode: setRfMode
  # retries twice
  serial.read(1) == 51
  
sendDataTransfer:
  # data transfer command
  sendCommand(8)

"""

if __name__ == '__main__':
  io.info("hello world")



#####
# EOF
