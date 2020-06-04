# husbzb-firmware


Nortek GoControl HUSBZB-1 Firmware updater image. 

This docker image will update the firmware from the shipped 5.4.1-194 (or other) to the latest publicly available image from SiLabs (6.4.1)

## To use:
`docker run --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware`

Replace */dev/ttyUSB1* with the path to the zigbee side of your USB stick. Make sure that nothing else is currently using the port (i.e. Shutdown and stop Home Assistant)

### *BETA STATUS - Currently the image only does a scan and does not yet update the firmware*

Example output, currently just a scan reporting current FW version: 
```
walthowd@home:/opt/husbzb-firmware$ docker run --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware
{"ports": [{"stackVersion": "5.4.1-194", "deviceType": "zigbee", "pid": "8A2A", "port": "/dev/ttyUSB1", "vid": "10C4"}]}
Found zigbee port at /dev/ttyUSB1 running 5.4.1-194
```

If you want to use this image to manually update your firmware run:

```
docker run --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware bash
cd /tmp/silabs
python2.7 ncp.py -p /dev/ttyUSB1 -f ncp-uart-sw.ebl 
```
