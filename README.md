# husbzb-firmware


Nortek GoControl HUSBZB-1 Firmware updater image. 

This docker image will update the firmware from the shipped 5.4.1-194 (or other) to the latest publicly available image from SiLabs (6.6.3)

## To use:
`docker run --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware`

Replace */dev/ttyUSB1* with the path to the zigbee side of your USB stick. Make sure that nothing else is currently using the port (i.e. Shutdown and stop Home Assistant)

### *BETA STATUS - Currently the image only does a scan and does not yet automatically update the firmware*

Example output, currently just a scan reporting current FW version: 
```
docker run --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware
{"ports": [{"stackVersion": "5.4.1-194", "deviceType": "zigbee", "pid": "8A2A", "port": "/dev/ttyUSB1", "vid": "10C4"}]}
Found zigbee port at /dev/ttyUSB1 running 5.4.1-194
```

### Manual firmware update procedure
If you want to use this image to manually update your firmware first shut down Home Assistant, or any other program accessing the port.

Then start a shell from the docker image:

```
docker run --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware bash
```
Make sure you are in */tmp/silabs* by changing directory and then flash:
```
cd /tmp/silabs
./ncp.py flash -p /dev/ttyUSB1 -f ncp-uart-sw.ebl 
```
Wait for the stick to reboot, then run *ncp.py* again to verify upgrade
```
./ncp.py scan
Connecting to.. /dev/ttyUSB1 57600 True False 
{"ports": [{"stackVersion": "6.6.3-151", "deviceType": "zigbee", "pid": "8A2A", "port": "/dev/ttyUSB1", "vid": "10C4"}]}
```
