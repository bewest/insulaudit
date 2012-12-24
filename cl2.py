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
  usbcommand.execute(self)



############################
#
# USB(Pump) Command Stuff
#


packSerialNumber:
  return makePackedBCD(serial)
"""

"""
######################
#
# Pump
#

# every command needs:
# code, retries, params, length, pages

initDevice:
  # cmdPowerControl Command(93, "rf power on", 2)
  # cmdPowerControl.params = [ 1, 1 ]
  # cmdPowerControl.retries = 0
  # cmdReadErrorStatus = Command(117, "read pump error status")
  # cmdReadState = Command(131, "Read Pump State")
  # cmdReadTempBasal = Command(152, "Read Temporary Basal")
  initDevice2

iniDevice2:
  detectActiveBolus = Command(76, "set temp basal rate (bolus detection only)", 3)
  detectActiveBolus.params = [ 0, 0, 0 ]
  detectActiveBolus.retries = 0

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

# 2 params
Command(code, descr)
  # 5: code, descr, bytesPerRecord, maxRecords, maxRetries
  return Command(code, descr, 64, 1, 0)

# 3 params
Command(code, descr, paramCount):
  # 5
  #
  com = Command(code, descr, 0, 1, 11)
  com.paramCount = paramCount
  numblocks = paramCount / 64 + 1

# 4 params
Command(code, descr, params, tail)
  # 5
  com =  Command(code, descr, 0, 1, 11)
  com.params = params
  #com.paramCount

# 5 params
Command(code, descr, bytesPerRecord, maxRecords, ??):
  # likely decompile error
  # 7
  Command(code, descr, bytesPerRecord, maxRecords, 0, 0, paramCount)
  dataOffset = 0
  cmdLength = 2

# 7 params
Command(code, descr, bytesPerRecord, maxRecords, address, addressLength, arg8):
  offset = 2
  if addressLength == 1:
    cmdLength = 2 + addressLength
  else:
    cmdLength = 2 + addressLength + 1
  retries = 2


# 511
execute:
  result = None
  for i in xrange(maxRetries)
    # reset bytes read
    response  = usb.execute(self)
    # handle stack trace
    if response: break
  return result

 

"""
"""

"""
class Link( core.CommBuffer ):
  class ID:
    VENDOR  = 0x0a21
    PRODUCT = 0x8001
  timeout = .100
  def __init__( self, port, timeout=None ):
    super(type(self), self).__init__(port, timeout)

  def setTimeout(self, timeout):
    self.serial.setTimeout(timeout)
  def getTimeout(self):
    return self.serial.getTimeout()

  def initUSBComms(self):
    self.initCommunicationsIO()
    #self.initDevice()

  def getSignalStrength(self):
    result = self.readSignalStrength()
    signal = result[0]

  def readSignalStrength(self):
    result = self.sendComLink2Command(6, 0)
    # result[0] is signal strength
    log.info('%r:readSignalStrength:%s' % (self, int(result[0])))
    return result

  def initCommunicationsIO(self):
    # close/open serial
    self.readProductInfo( )
    self.readSignalStrength()

  def endCommunicationsIO(self):
    self.readSignalStrength()
    self.readInterfaceStatistics()
    # close port
    self.close()

  def readProductInfo(self):
    result = self.sendComLink2Command(4)
    # 1/0/255
    log.info('readProductInfo:result')
    freq   = result[5]
    info   = self.decodeProductInfo(result)
    log.info('product info: %s' % pformat(info))
    # decodeInterface stats
      
  def decodeProductInfo(self, data):
    class F:
      body = data
    comm = USBProductInfo()
    comm.reply = F()
    comm.onACK()
    return comm.info

  def sendComLink2Command(self, msg, a2=0x00, a3=0x00):
    # generally commands are 3 bytes, most often CMD, 0x00, 0x00
    msg = bytearray([ msg, a2, a3 ])
    io.info('sendComLink2Command:write')
    self.write(msg)
    return self.checkAck()
    # throw local usb exception

  def checkAck(self):
    #time.sleep(.100)
    result     = bytearray(self.read(64))
    io.info('checkAck:read')
    commStatus = result[0]
    # usable response
    assert commStatus == 1
    status     = result[1]
    # status == 102 'f' NAK, look up NAK
    if status == 85: # 'U'
      log.info('ACK OK')
      return result[3:]
    assert False, "NAK!!"

  def decodeIFaceStats(self, data):
    class F:
      body = data
    comm = InterfaceStats()
    comm.reply = F()
    comm.onACK()
    return comm.info

  def readInterfaceStatistics(self):
    # decode and log stats
    result = self.sendComLink2Command(5, 0)
    info   = self.decodeIFaceStats(result)
    log.info("read radio Interface Stats: %s" % pformat(info))
    result = self.sendComLink2Command(5, 1)
    info   = self.decodeIFaceStats(result)
    log.info("read stick Interface Stats: %s" % pformat(info))


#######################
#
#
#
def CRC8(data):
  return lib.CRC8.compute(data)

################################
# Remote Stuff
#

class BaseCommand(object):
  code    = 0x00
  descr   = "(error)"
  retries = 2
  timeout = 3
  params  = [ ]
  bytesPerRecord = 0
  maxRecords = 0
  effectTime = 1

  def __init__(self, code, descr, *args):
    self.code   = code
    self.descr  = descr
    self.params = [ ]

  def format(self):
    pass

  def allocateRawData(self):
    self.raw = self.bytesPerRecord * self.maxRecords


class Device(object):
  def __init__(self, link):
    self.link = link

  def execute(self, command):
    self.command = command
    self.allocateRawData()
    self.sendAndRead()

  def sendAndRead(self):
    self.sendDeviceCommand()
    time.sleep(self.command.effectTime)
    if self.expectedLength > 0:
      # in original code, this modifies the length tested in the previous if
      # statement
      self.command.data = self.readDeviceData()

  def sendDeviceCommand(self):
    packet = self.buildTransmitPacket()
    io.info('sendDeviceCommand:write:%r' % (self.command))
    self.link.write(packet)
    time.sleep(.001)
    code = self.command.code
    params = self.command.params
    if code != 93 or params[0] != 0:
      self.link.checkAck()

  def allocateRawData(self):
    self.command.allocateRawData()
    self.expectedLength = self.command.bytesPerRecord * self.command.maxRecords

  def readDeviceData(self):
    self.eod = False
    results  = bytearray( )
    while not self.eod:
      data = self.readDeviceDataIO( )
      results.extend(data)
    return results

  def readDeviceDataIO(self):
    results   = self.readData()
    lb, hb    = results[5] & 0x7F, results[6]
    self.eod  = (results[5] & 0x80) > 0
    resLength = lib.BangInt((lb, hb))
    log.info('XXX resLength: %s' % resLength)
    #assert resLength < 64, ("cmd low byte count:\n%s" % lib.hexdump(results))

    data = results[13:13+resLength]
    assert len(data) == resLength
    crc = results[-1]
    # crc check
    log.info('readDeviceDataIO:msgCRC:%r:expectedCRC:%r:data:%r' % (crc, CRC8(data), data))
    assert crc == CRC8(data)
    return data

  def readData(self):
    bytesAvailable = self.getNumBytesAvailable()
    packet = [12, 0, lib.HighByte(bytesAvailable), lib.LowByte(bytesAvailable)]
    packet.append( CRC8(packet) )

    response = self.writeAndRead(packet, bytesAvailable)
    # assert response.length > 14
    assert (int(response[0]) == 2), repr(response)
    # response[1] != 0 # interface number !=0
    # response[2] == 5 # timeout occurred
    # response[2] == 2 # NAK
    # response[2] # should be within 0..4
    log.info("readData ACK")
    return response

  def writeAndRead(self, msg, length):
    io.info("writeAndRead:")
    self.link.write(bytearray(msg))
    time.sleep(.300)
    self.link.setTimeout(self.command.timeout)
    return bytearray(self.link.read(length))

  def getNumBytesAvailable(self):
    result = self.readStatus( )
    start = time.time()
    i     = 0
    while result == 0 and time.time() - start < 1:
      log.debug('%r:getNumBytesAvailable:attempt:%s' % (self, i))
      result = self.readStatus( )
      time.sleep(.10)
      i += 1
    log.info('getNumBytesAvailable:%s' % result)
    return result

  def readStatus(self):
    result         = self.link.sendComLink2Command(3)
    commStatus     = result[0] # 0 indicates success
    assert commStatus == 0
    status         = result[2]
    lb, hb         = result[3], result[4]
    bytesAvailable = lib.BangInt((lb, hb))
    self.status    = status

    if (status & 0x1) > 0:
      return bytesAvailable
    return 0

  def buildTransmitPacket(self):
    return self.command.format( )

class PumpCommand(BaseCommand):
  #serial = '665455'
  #serial = '206525'
  serial = '208850'

  params = [ ]
  bytesPerRecord = 64
  maxRecords = 1
  retries = 2
  __fields__ = ['maxRecords', 'code', 'descr',
                'serial', 'bytesPerRecord', 'params']
  def __init__(self, **kwds):
    for k in self.__fields__:
      value = kwds.get(k, getattr(self, k))
      setattr(self, k, value)

  def getData(self):
    return self.data

  def format(self):
    params = self.params
    code   = self.code
    maxRetries = self.retries
    serial = list(bytearray(self.serial.decode('hex')))
    paramsCount = len(params)
    head   = [ 1, 0, 167, 1 ]
    # serial
    packet = head + serial
    # paramCount 2 bytes
    packet.extend( [ (0x80 | lib.HighByte(paramsCount)),
                             lib.LowByte(paramsCount) ] )
    # not sure what this byte means
    button = 0
    # special case command 93
    if code == 93:
      button = 85
    packet.append(button)
    packet.append(maxRetries)
    # how many packets/frames/pages/flows will this take?
    responseSize = self.calcRecordsRequired()
    # really only 1 or 2?
    pages = responseSize
    if responseSize > 1:
      pages = 2
    packet.append(pages)
    packet.append(0)
    # command code goes here
    packet.append(code)
    packet.append(CRC8(packet))
    packet.extend(params)
    packet.append(CRC8(params))
    io.info(packet)
    return bytearray(packet)

  def calcRecordsRequired(self):
    length = self.bytesPerRecord * self.maxRecords
    i = length / 64
    j = length % 64
    if j > 0:
      return i + 1
    return i


class PowerControl(PumpCommand):
  """
    >>> PowerControl().format() == PowerControl._test_ok
    True
  """
  _test_ok = bytearray( [ 0x01, 0x00, 0xA7, 0x01, 0x66, 0x54, 0x55, 0x80,
                          0x02, 0x55, 0x00, 0x00, 0x00, 0x5D, 0xE6, 0x01,
                          0x0A, 0xA2 ] )
  code = 93
  descr = "RF Power On"
  params = [ 0x01, 0x0A ]
  retries = 0
  maxRecords = 0
  timeout = 17
  effectTime = 17

class PowerControlOff(PowerControl):
  params = [ 0x00, 0x0A ]

class ReadErrorStatus(PumpCommand):
  """
    >>> ReadErrorStatus().format() == ReadErrorStatus._test_ok
    True
  """
  _test_ok = bytearray([ 0x01, 0x00, 0xA7, 0x01, 0x66, 0x54, 0x55, 0x80,
                         0x00, 0x00, 0x02, 0x01, 0x00, 0x75, 0xD7, 0x00 ])
  code = 117
  descr = "Read Error Status any current alarms set?"
  params = [ ]
  retries = 2
  maxRecords = 1

class ReadHistoryData(PumpCommand):
  """
  """

  code = 128
  descr = "Read History Data"
  params = [ ]
  retries = 2
  maxRecords = 1

class ReadRTC(PumpCommand):
  """
  """

  code = 112
  descr = "Read RTC"
  params = [ ]
  retries = 2
  maxRecords = 1


  def getData(self):
    data = self.data
    d = {
      'hour'  : int(data[0]),
      'minute': int(data[1]),
      'second': int(data[2]),
      # XXX
      'year'  : 2000 + (data[4] & 0x0F),
      'month' : int(data[5]),
      'day'   : int(data[6]),
    }
    return "%(year)s-%(month)s-%(day)sT%(hour)s:%(minute)s:%(second)s" % (d)

class ReadPumpID(PumpCommand):
  """
  """

  code = 113
  descr = "Read Pump ID"
  params = [ ]
  retries = 2
  maxRecords = 1

  def getData(self):
    data = self.data
    return str(data[0:6])

class ReadBatteryStatus(PumpCommand):
  """
  """

  code = 114
  descr = "Read Battery Status"
  params = [ ]
  retries = 2
  maxRecords = 1

  def getData(self):
    data = self.data
    bd = bytearray(data)
    volt = lib.BangInt((bd[1], bd[2]))
    indicator = bd[0]
    battery = {'status': {0: 'normal', 1: 'low'}[indicator], 'voltage': volt/100.0 }
    return battery


class ReadFirmwareVersion(PumpCommand):
  """
  """

  code = 116
  descr = "Read Firmware Version"
  params = [ ]
  retries = 2
  maxRecords = 1

  def getData(self):
    data = self.data
    log.debug("READ FIRMWARE HEX:\n%s" % lib.hexdump(data))
    return str(data.split( chr(0x0b) )[0]).strip( )


class ReadPumpState(PumpCommand):
  """
    >>> ReadPumpState().format() == ReadPumpState._test_ok
    True
  """
  _test_ok = bytearray([ 0x01, 0x00, 0xA7, 0x01, 0x66, 0x54, 0x55, 0x80,
                         0x00, 0x00, 0x02, 0x01, 0x00, 0x83, 0x2E, 0x00 ])

  code = 131
  descr = "Read Pump State"
  params = [ ]
  retries = 2
  maxRecords = 1

class ReadGlucoseHistory(PumpCommand):
  """
  """
  descr = "Read glucose history"
  code = 131
  params = [ ]
  retries = 2


class ReadPumpModel(PumpCommand):
  """
    >>> ReadPumpModel().format() == ReadPumpModel._test_ok
    True
  """
  code = 141
  descr = "Read Pump Model Number"
  params = [ ]
  retries = 2
  maxRecords = 1
  _test_ok = bytearray([ 0x01, 0x00, 0xA7, 0x01, 0x66, 0x54, 0x55, 0x80,
                         0x00, 0x00, 0x02, 0x01, 0x00, 0x8D, 0x5B, 0x00 ])

  def getData(self):
    data = self.data
    length = data[0]
    msg = data[1:1+length]
    self.model = msg
    return str(msg)

def initDevice(link):
  device = Device(link)

  comm   = PowerControl()
  device.execute(comm)
  log.info('comm:%s:data:%s' % (comm, getattr(comm, 'data', None)))

  comm   = ReadErrorStatus()
  device.execute(comm)
  log.info('comm:%s:data:%s' % (comm, getattr(comm, 'data', None)))

  comm   = ReadPumpState()
  device.execute(comm)
  log.info('comm:%s:data:%s' % (comm, getattr(comm, 'data', None)))

  return device

def do_commands(device):
  comm = ReadPumpModel( )
  device.execute(comm)
  log.info('comm:%s:data:%s' % (comm, getattr(comm.getData( ), 'data', None)))
  log.info('REMOTE PUMP MODEL NUMBER: %s' % comm.getData( ))

  log.info("READ RTC")
  comm = ReadRTC( )
  device.execute(comm)
  log.info('comm:RTC:%s' % (comm.getData( )))

  log.info("READ PUMP ID")
  comm = ReadPumpID( )
  device.execute(comm)
  log.info('comm:READ PUMP ID: ID: %s' % (comm.getData( )))


  log.info("Battery Status")
  comm = ReadBatteryStatus( )
  device.execute(comm)
  log.info('comm:READ Battery Status: %r' % (comm.getData( )))

  log.info("Firmware Version")
  comm = ReadFirmwareVersion( )
  device.execute(comm)
  log.info('comm:READ Firmware Version: %r' % (comm.getData( )))

def shutdownDevice(device):
  comm = PowerControlOff()
  device.execute(comm)
  log.info('comm:%s:data:%s' % (comm, getattr(comm, 'data', None)))


if __name__ == '__main__':
  io.info("hello world")
  import doctest
  doctest.testmod( )

  port = None
  try:
    port = sys.argv[1]
  except IndexError, e:
    print "usage:\n%s /dev/ttyUSB0" % sys.argv[0]
    sys.exit(1)
    
  link = Link(port)
  link.initUSBComms()
  device = initDevice(link)
  do_commands(device)
  #shutdownDevice(device)
  link.endCommunicationsIO()
  #pprint( carelink( USBProductInfo(      ) ).info )


#####
# EOF
