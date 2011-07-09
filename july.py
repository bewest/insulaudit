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
# Command Stuff
# (pseudocode analysis of MM512.java)
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

buildPacket:
  # 7 bytes + params
  packet = [ ]
  head   = [ 167, ] + serial 
  body   = [ self.code ]
  tail   = [ 0 ]
  if paramCount > 0:
    if sequenceNumber:
      tail = [ sequenceNumber ]
    else:
      tail = [ paramCount ]
    tail.append( commandParams )
  packet = head + body + tail
  packet.append(CRC8(packet))
  return encodeDC(packet)

makeCommandPacket:
  # returns a new "Command"
  # which special cases 93
  command = Command(self.code, 0, 0, 0)
  if code == 93 and commandParams[0] == 1:
    command.setUseMultiXmitMode(true)
  return command

makeDataPacket(packetNumber, sequenceNumber, paramCount):
  command = Command(self.code, 0, 0, self.commandType)
  command.paramCount     = paramCount
  command.sequenceNumber = sequenceNumber
  command.params         = self.params[packetOffset:packetOffset+packetSize]
  return command


"""

"""
#####################
#
# Pump Stuff
# (pseudocode analysis of MM512.java)
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
  sendCommand()
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
  # collect multiple pages of data for commands with longer reads.
  done = False
  pages = [ ]
  while not done:
    # get a page
    data = readDeviceData()
    # if no more data we're done
    if data.length == 0
      done = true
    else
      # add data to pages
      pages.append(data)
      done = pages.length >= expectedBytes || isHaltRequested()
      # sendAck to acknowledge receipt of this page
      if not done and isHaltRequested():
        sendAck()
  return pages

readDeviceData:
  bytesAvail = usb.readStatus( )
  usb.sendTransferDataCommand( ) # exec read data flow on usb
  response = decodeDC(serial.read( ))
  ack = usb.readAckByte()
  if (!ack) throw IOException
  checkHeaderCRC(response)
  response[5] is NAK (21) # look up NAK
  if response[4] != commandCode # throw Error
  dataLen = response[5] # length
  cpyLen = len(response) - 6 - 1
  return response[6:-1]


packSerial
  return makePackedBCD(serial)

encodeDC(msg):
  # realign bytes
  nibbles = [ ]
  encoded = [ ]
  # collect nibbles
  for (b in msg):
    highNibble = b >> 4 & 0xF
    lowNibble  = b & 0xF
    dcValue1   = ENCODE_TABLE[highNibble]
    dcValue2   = ENCODE_TABLE[lowNibble]
    nibbles.append(dcValue1 >> 2)

    high2Bits = dcValue1 & 0x3
    low2Bits  = dcValue2 >> 4 & 0x3
    nibbles.append( high2Bits << 2 | low2Bits )
    nibbles.append( dcValue2 & 0xF )
  
  for i in nibbles.iter:
    # last item gets a padding terminator
    v  = nibbles[i]
    lb = (v, 5)
    # most elide the next item
    if i < nibbles.length - 1:
      lb = (v, nibbles[i+1])
    encoded.append(Util.makeByte(lb[0], lb[2]))
  return encoded

decodeDC(msg):
  decoded     = [ ]
  nibbleCount = 0
  bitCount    = 0
  sixBitValue = 0
  highValue   = 0
  highNibble  = 0
  # 
  for B in msg:
    bP = 7
    while bP >= 0:
      bitValue = B >> bP & 0x1
      sixBitValue = sixBitValue << 1 | bitValue
      bitCount++
      if (bitCount !=6)
        continue; # next
      nibbleCount++
      if nibbleCount == 1:
        highNibble = decodeDCByte(sixBitValue)
      else
        lowNibble = decodeDCByte(sixBitValue)
        byteValue = makeByte(highNibble, lowNibble)
        # append to result
        decoded.append(byteValue)
        nibbleCount = 0
      sixBitValue = 0
      bitCount    = 0
      bp--

  return decoded

decodeDCByte(B):
  # B should be 0 < B && B < 63
  # look up in decode table
  for k, v in ENCODE_TABLE:
    if V == B
      return k

set/isUseMultiXmitMode: # simple getter/setter for m_useMultiXmitMode

Command(code, bytesPerRecord, maxRecords, address, addressLength, commandType)
XXX: acquireDataFromDevice, acquireDataFromDeviceConclusion only have disassembly, making it a bit harder to understand.

"""

"""

##########
#
# USB Device
#

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
  
sendDataTransferCommand:
  # data transfer command
  sendCommand(8)

"""

if __name__ == '__main__':
  io.info("hello world")



#####
# EOF
