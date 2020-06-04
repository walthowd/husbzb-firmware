__author__ = 'miwebb ehasdar'

# Reference URLS for EZSP and ASH protocol
# http://www.silabs.com/Support%20Documents/TechnicalDocs/UG100-EZSPReferenceGuide.pdf
# http://wwwqa.silabs.com/Support%20Documents/TechnicalDocs/UG100.pdf
# https://www.silabs.com/Support%20Documents/TechnicalDocs/UG101.pdf

# This tools has various modules used by IoT Solutions for interacting with EZSP and TMSP NCPs.

import serial
from xmodem import XMODEM
import sys
import time
import argparse
import serial.tools.list_ports
import json
import os
import logging
logging.basicConfig()

# EZSP Init return codes:
NO_ERROR = 0
ERROR_NCP_INVALID_ACK = -1
ERROR_NCP_WRONG_EZSP_VERSION = -2

BOOTLOADER_INIT_TIMEOUT = 10

# Silicon Labs CEL EM3588 USB Stick
CEL_VID = '10C4'
#CEL_PID = '8A5E'
# Nortek/GoControl HUSBZB-1
CEL_PID = '8A2A'
CEL_BAUD = 57600
CEL_XON_XOFF = True
CEL_RTS_CTS = False
# Silicon Labs WSTK (J-Link Pro OB)
WSTK_VID = '1366'
WSTK_PID = '0105'
WSTK_BAUD = 115200
WSTK_XON_XOFF = False
WSTK_RTS_CTS = True

def is_valid_file(parser, arg):
    if not os.path.isfile(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

parser = argparse.ArgumentParser(description='')
subparsers = parser.add_subparsers(help='flash, scan')
parser_flash = subparsers.add_parser('flash', help='Flashes a NCP with a new application packaged in an EBL file.')
parser_flash.add_argument('-p','--port', type=str, required=True,
                    help='Serial port for NCP')
parser_flash.add_argument('-f', '--file', type=lambda x: is_valid_file(parser, x), required=True,
                    help='EBL file to upload to NCP')
parser_flash.set_defaults(which='flash')

parser_scan = subparsers.add_parser('scan', help='Scan OS for attached Zigbee NCPs.')
parser_scan.set_defaults(which='scan')

# HELPER
def randSeqUpTo(n):
    curr = 0x42
    out = []
    while len(out) < n:
        out.append(curr)
        if bin(curr)[-1] == '0':
            curr = curr >> 1
        else:
            curr = (curr >> 1) ^ 0xB8
    return out

def trans(s):
    seq = randSeqUpTo(len(s))
    out = []
    for i in range(len(s)):
        out.append(ord(s[i]) ^ seq[i])
    return out

def ezspV4Init(ser):
    #flush input buffer
    ser.flushInput()
    # EZSP RST Frame
    ser.write(b'\x1A\xC0\x38\xBC\x7E')
    # Wait for RSTACK FRAME (Reset ACK)
    resp = ser.read(7)
    # If we get an invalid RSTACK FRAME, fail detection
    if resp != b'\x1A\xC1\x02\x0B\x0A\x52\x7E':
        return ERROR_NCP_INVALID_ACK
    # EZSP Configuration Frame: version ID: 0x00
    # Note: Must be sent before any other EZSP commands
    # { FRAME CTR + EZSP [0x00 0x00 0x00 0x04] + CRC + FRAME END }
    ser.write(b'\x00\x42\x21\xA8\x50\xED\x2C\x7E')
    # Wait for Data Response { protocolVersion, stackType, stackVersion }
    # this must be ACK'd
    resp = ser.read(11)
    # DATA ACK response frame
    ser.write(b'\x81\x60\x59\x7E')
    # Check ncp data response:
    # 5.8.1 ncp example: { 0x01 0x42 0xa1 0xa8 0x50 0x28 0x05 0xea 0xbe 0xee 0x7e }
    if resp[1:5] != b'\x42\xA1\xA8\x50':
        return ERROR_NCP_WRONG_EZSP_VERSION
    # EZSP v4 init ok
    return NO_ERROR

def ezspV5Init(ser):
    #flush input buffer
    ser.flushInput()
    # EZSP RST Frame
    ser.write(b'\x1A\xC0\x38\xBC\x7E')
    # Wait for RSTACK FRAME (Reset ACK)
    resp = ser.read(7)
    # If we get an invalid RSTACK FRAME, fail detection
    if resp != b'\x1A\xC1\x02\x0B\x0A\x52\x7E':
        return ERROR_NCP_INVALID_ACK
    # EZSP Configuration Frame: version ID: 0x00
    # Note: Must be sent before any other EZSP commands
    # { FRAME CTR + EZSP [0x00 0x00 0x00 0x05] + CRC + FRAME END }
    ser.write(b'\x00\x42\x21\xA8\x51\xFD\x0D\x7E')
    # Wait for Data Response { protocolVersion, stackType, stackVersion }
    # this must be ACK'd
    resp = ser.read(11)
    # DATA ACK response frame
    ser.write(b'\x81\x60\x59\x7E')
    # Check ncp data response:
    # 5.9.0 ncp example: { 0x01 0x42 0xa1 0xa8 0x51 0x28 0x15 0xeb 0xdb 0x08 0x7e }
    if resp[1:5] != b'\x42\xA1\xA8\x51':
        return ERROR_NCP_WRONG_EZSP_VERSION
    # EZSP v5 init ok
    return NO_ERROR

def ezspV6Init(ser):
    #flush input buffer
    ser.flushInput()
    # EZSP RST Frame
    ser.write(b'\x1A\xC0\x38\xBC\x7E')
    # Wait for RSTACK FRAME (Reset ACK)
    resp = ser.read(7)
    # If we get an invalid RSTACK FRAME, fail detection
    if resp != b'\x1A\xC1\x02\x0B\x0A\x52\x7E':
        return ERROR_NCP_INVALID_ACK
    # EZSP Configuration Frame: version ID: 0x00
    # Note: Must be sent before any other EZSP commands
    # { FRAME CTR + EZSP [0x00 0x00 0x00 0x06] + CRC + FRAME END }
    ser.write(b'\x00\x42\x21\xA8\x52\xCD\x6E\x7E')
    # Wait for Data Response { protocolVersion, stackType, stackVersion }
    # this must be ACK'd
    resp = ser.read(11)
    # DATA ACK response frame
    ser.write(b'\x81\x60\x59\x7E')
    # Check ncp data response:
    # 6.0.0 ncp example: { 0x01 0x42 0xa1 0xa8 0x52 0x28 0x15 0xd2 0xe7 0xae 0x7e }
    if resp[1:5] != b'\x42\xA1\xA8\x52':
        return ERROR_NCP_WRONG_EZSP_VERSION
    # EZSP v6 init ok
    return NO_ERROR
	
def ezspV7Init(ser):
    #flush input buffer
    ser.flushInput()
    # EZSP RST Frame
    ser.write(b'\x1A\xC0\x38\xBC\x7E')
    # Wait for RSTACK FRAME (Reset ACK)
    resp = ser.read(7)
    # If we get an invalid RSTACK FRAME, fail detection
    if resp != b'\x1A\xC1\x02\x0B\x0A\x52\x7E':
        return ERROR_NCP_INVALID_ACK
    # EZSP Configuration Frame: version ID: 0x00
    # Note: Must be sent before any other EZSP commands
    # { FRAME CTR + EZSP [0x00 0x00 0x00 0x07] + CRC + FRAME END }
    ser.write(b'\x00\x42\x21\xA8\x53\xDD\x4F\x7E')
    # Wait for Data Response { protocolVersion, stackType, stackVersion }
    # this must be ACK'd
    resp = ser.read(11)
    # DATA ACK response frame
    ser.write(b'\x81\x60\x59\x7E')
    # Check ncp data response:
    # 7.0.0 ncp example: { 0x01 0x42 0xa1 0xa8 0x53 0x28 0x15 0xd6 0xd1 0x9e 0x7e }
    if resp[1:5] != b'\x42\xA1\xA8\x53':
        return ERROR_NCP_WRONG_EZSP_VERSION
    # EZSP v7 init ok
    return NO_ERROR	

def flash(port, file):
    # STATIC FUNCTIONS
    def getc(size, timeout=1):
        return ser.read(size)

    def putc(data, timeout=1):
        ser.write(data)
        time.sleep(0.001)

    print 'Restarting NCP into Bootloader mode...'

    # Default port settings
    BAUD = 57600;
    XON_XOFF = True;
    RTS_CTS = False;
    # Check CEL or WSTK
    for p in serial.tools.list_ports.comports():
        if p[0] == port:
            # Parse out VID and PID
            vid = p[2].split('PID=')[1].split(':')[0]
            pid = p[2].split('PID=')[1].split(':')[1][0:4]
            # Check if CEL EM3588 USB stick
            if vid == CEL_VID and pid == CEL_PID:
                print 'CEL stick'
                BAUD = CEL_BAUD
                XON_XOFF = CEL_XON_XOFF
                RTS_CTS = CEL_RTS_CTS
                break
            # Check if WSTK board
            if vid == WSTK_VID and pid == WSTK_PID:
                print 'WSTK board'
                BAUD = WSTK_BAUD
                XON_XOFF = WSTK_XON_XOFF
                RTS_CTS = WSTK_RTS_CTS
                break

    # Init serial port
    ser = serial.Serial(
        port=port,
        baudrate=BAUD,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=XON_XOFF,
        rtscts=RTS_CTS
    )

    # Wait for ncp ready
    time.sleep(1)

    # EZSP protocol initialization
    if ezspV7Init(ser)!=NO_ERROR and ezspV6Init(ser)!=NO_ERROR and ezspV5Init(ser)!=NO_ERROR and ezspV4Init(ser)!=NO_ERROR:
        print 'NCP no ZigBee Ack. Please try again.'
        sys.exit(1)

    #flush input buffer
    ser.flushInput()

    # EZSP Configuration Frame: launchStandaloneBootloader ID: 0x8F
    # { FRAME CTR + EZSP [0x01 0x00 0x8F 0x01] + CRC + FRAME END }
    # Note: FRAME CTR is 0x11 which needs to be escaped [ 0x7D 0x31 ]
    ser.write(b'\x7D\x31\x43\x21\x27\x55\x6E\x90\x7E')

    # Read response bytes
    ser.read(8)
    ser.close()

    # Wait for restart
    time.sleep(4)

    # Open new connection
    ser = serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        xonxoff=True
    )

    # Burn the prompt
    ser.write('\x0A')
    # Boot menu - legacy or Gecko bootloader?
    # Gecko  BL verion at 2nd line
    # Legacy BL verion at 3rd line
    ser.readline() # read blank line
    verBL = ser.readline() # read Gecko BTL version or blank line
    if not ("Gecko Bootloader" in verBL):
        verBL = ser.readline() # read Legacy BTL version
    print verBL # show Bootloader version
    if "Gecko Bootloader" in verBL and not(".gbl" in file):
        print 'Aborted! Gecko bootloader accepts .gbl image only.'
        print 'Please replug the USB NCP board and flash the gbl file again.'
        sys.exit(1)
    elif "EFR32 Serial Btl" in verBL and not(".ebl" in file):
        print 'Aborted! Legacy bootloader accepts .ebl image only.'
        print 'Please replug the USB NCP board and flash the ebl file again.'
        sys.exit(1)
    else:
        ser.readline() # 1. upload gbl or ebl
        ser.readline() # 2. run
        ser.readline() # 3. ebl info
        # Enter '1' to initialize X-MODEM mode
        ser.write('1')
        time.sleep(1)
        # Read responses
        ser.readline() # BL > 1
        ser.readline() # begin upload
        # Wait for char 'C'
        success = False
        start_time = time.time()
        while time.time()-start_time < BOOTLOADER_INIT_TIMEOUT:
            if ser.read() == 'C':
                success = True
                break
        if not success:
            print 'Failed to restart into bootloader mode. Please see users guide.'
            sys.exit(1)

    print 'Successfully restarted into bootloader mode! Starting upload of NCP image... '

    # Start XMODEM transaction
    modem = XMODEM(getc, putc)
    stream = open(file,'r')
    sentcheck = modem.send(stream)

    if sentcheck:
        print 'Finished!'
    else:
        print 'NCP upload failed. Please reload a correct NCP image to recover.'
    print 'Rebooting NCP...'

    # Send Reboot into App-Code command
    ser.write('2')
    ser.close()

def scan():
    outjson = {'ports':[]}
    for port in serial.tools.list_ports.comports():
        portjson = {"port":port[0]}
        try:
            # Parse out VID and PID
            vid = port[2].split('PID=')[1].split(':')[0]
            pid = port[2].split('PID=')[1].split(':')[1][0:4]
            portjson['vid'] = vid
            portjson['pid'] = pid

            # Check which USB NCP device
            if vid == CEL_VID and pid == CEL_PID or vid == WSTK_VID and pid == WSTK_PID or vid == ETRX_VID and pid == ETRX_PID or vid == CP201x_VID and pid == CP201x_PID:
                # Use EM3588 USB stick as default
                BAUD = CEL_BAUD
                XON_XOFF = CEL_XON_XOFF
                RTS_CTS = CEL_RTS_CTS
                # Check if WSTK board
                if vid == WSTK_VID and pid == WSTK_PID:
                    BAUD = WSTK_BAUD
                    XON_XOFF = WSTK_XON_XOFF
                    RTS_CTS = WSTK_RTS_CTS

                sys.stderr.write('Connecting to.. %s %s %s %s \n' % (port[0], BAUD, XON_XOFF, RTS_CTS));

                # Init serial port
                ser = serial.Serial(
                    port=port[0],
                    baudrate=BAUD,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    xonxoff=XON_XOFF,
                    rtscts=RTS_CTS
                )

                # Wait for ncp ready
                time.sleep(1)

                # EZSP protocol initialization...
                if ezspV7Init(ser)==NO_ERROR or ezspV6Init(ser)==NO_ERROR or ezspV5Init(ser)==NO_ERROR or ezspV4Init(ser)==NO_ERROR:
                    #flush input buffer
                    ser.flushInput()

                    # EZSP Configuration Frame: getValue ID: 0xAA
                    # { FRAME CTR + EZSP [0x01 0x00 0xAA 0x11] + CRC + FRAME END }
                    # Note: FRAME CTR is 0x11 which needs to be escaped [ 0x7D 0x31 ]
                    ser.write(b'\x7D\x31\x43\x21\x02\x45\x85\xB2\x7E')

                    # EZSP Response Frame: getValue ID: 0xAA
                    # { FRAME CTR + EZSP (SAMPLE) [0x1 0x80 0xaa 0x0 0x7 0x57 0x0 0x5 0x7 0x0 0x0 0x0] + CRC + FRAME END}
                    # EZSP Format {CTR + FRAME CONTROL + COMMAND USED + EMBER STATUS + RETURNED DATA LENGTH + RETURNED DATA}
                    # Returned Data: Build Number, unused?, Major version, Minor Version, Patch Version, Special Version, Type
                    versioninfo = trans(ser.read(16)[1:])[5:]
                    portjson['deviceType'] = 'zigbee'
                    portjson['stackVersion'] = str(versioninfo[2]) + '.' + str(versioninfo[3]) + '.' + str(versioninfo[4]) + '-' + str(versioninfo[0])
                    # Include a special version if it exists
                    if versioninfo[5] != 0:
                        portjson['stackVersion'] += 's' + str(versioninfo[5])
                else:
                    sys.stderr.write('No ZigBee Ack. %s \n' % port[0]);
                    portjson['deviceType'] = 'unknown'
                ser.close()
            else:
                sys.stderr.write('No Compatable USB devices found. %s %s \n' % port[0]);
                portjson['deviceType'] = 'unknown'
        except:
            sys.stderr.write('Exception: %s %s \n' % (sys.exc_info()[0],  port[0]));
            portjson['deviceType'] = 'unknown'
            pass
        outjson['ports'].append(portjson)
    print json.dumps(outjson)

args = parser.parse_args()
if args.which == 'scan':
    scan()
else:
    flash(args.port,args.file)
