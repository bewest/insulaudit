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
  serial.write(6)
  # check success, first byte == 51
  numOldBytes = readStatus( )
  if numOldBytes > 0:
    sendTransferDataCommand( )
    message = serial.read( )
    usb.readAckByte()
  
readAckByte:
  # retries twice
  serial.read(1) == 'U'
  # else NAK == f

readStatus:
  # sets m_status, used to decode receivedByteCount, hasData, RS232Mode,
  # FilterRepeat, AutoSleep, Status Error, SelfTestError
  self.status = sendCommandGetReply(2)
  bytesAvailable = serial.read(1)
  readAckByte() # serial.read(1) == ACK
  
sendCommandGetReply:
  sendCommand(command)
  return serial.read()

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
  

"""

if __name__ == '__main__':
  io.info("hello world")



#####
# EOF
