# husbzb-firmware
Nortek GoControl HUSBZB-1 Firmware updater image. 

This docker image will update the firmware from the shipped 5.4.1-194 (or other) to the latest publicly available image from SiLabs (6.4.1)

## To use:
docker run --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware 

Replace */dev/ttyUSB1* with the path to the zigbee side of your USB stick. Make sure that nothing else is currently using the port (i.e. Shutdown and stop Home Assistant)

*Currently the image only does a scan and does not yet update the firmware*
