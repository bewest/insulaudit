

Metronic uses a binary custom protocol to manage their pumps.


MM511. execute: pseudo code
  success = 0
  attempts = 0

  do
    setTotalReadByteCountExpected
    try
      getComLink.execute(this)
    except: basics
      re-init
  while( success == 0 && j <= maxRetries && !HaltRequested


ComLink2: execute(deviceCommand):
  usbcomand = new USBCommand(deviceCommand)
  usbcomand.execute();


USBCommand#execute
  allocateRawData()
  sendAndRead()



USBCommand#sendAndRead
  if this.state != 7 RETRY
    this.state = 4 SENDING

  sendDeviceCommand()

  if this.command.rawData.length > && !haltRequested
    this.state = 5 READ
    this.command.rawData = readDeviceData()

  if this.state = 7 # RETRY
    this.state = 4 # SEND
  
USBCommand#sendDeviceCommand
  packet = builtTransmitPacket()
  this.port.write(packet)
  sleep(this.getEffectTime())

  if ( command != 93 || this.commandParameters[0] != 0
    fetchAck

USBCommand#allocateRawData 
  this.rawData = new Array( command.bytesPerRecord * command.maxRecords )

USBCommand#readDeviceData()
  result = []
  do
    result.extend(readDeviceDataIO())
  while ((!this.eod) && !isHaltRequested())
  return result

USBCommand#readDeviceDataIO()
  bytes = readData()
  this.eodSet = ((result[5] && 0x80) > 0)

  msgByteCount = BangInt(0x7F & result[5], result[6])
  if (msgByteCount < 64)
    throw "Low Data BYte Count"

  message  = result[0:13]
  synthCRC = computeCRC8(message)
  commCRC  = result[-1]

  if (synthCRC != commCRC)
    throw "bad crc"

  return message

USBCommand#readData
  num = getNumBytesAvailable()

  packet = [ 0x0C, 0x0 ...]
  

USBCommand#getNumBytesAvailable

clmm pump comms - comms.msc

               pc      usb     
               |       |       
This is kind of a "send command" command.
write          |------>|      Hint: code is 14th byte
               |       |      (bytes[13])
read           |<------|       success [ 0x01, 0x85 U, ?? ]
               |       |       fail [ 0x01, 0x85 f, ?? ]
write          |------>|      code=[ 0x03 ] usb status command
repeat         |       |<     Continually ask for the usb
               |       |                  status until the stick
               |       |                  indicates that we are done
               |       |                  receiving and we have a length.
read           |<------|      success [ 0x01, 0x85 U, ?? ]
               |       |      fail    [ 0x01, 0x66 f, ?? ]
read           |<------|      tx.stats = bytes[5]
read           |<------|      length = bytes[6..8]
format         |<      |      Then use the length to format the
               |       |                flush command, which will give us
               |       |                the contents of radio buffer.
write          |------>|      command [ 0x0C, 0x00, 0x00,
               |       |                  HighByte(length),
               |       |                  LowByte(length), CRC ]
read           |<------|      read data in 64 byte chunks until we've got
               |       |      the amount of data we expected
               |       |       



