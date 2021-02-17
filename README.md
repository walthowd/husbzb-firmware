# husbzb-firmware

Zigbee coordinator firmware updater image for Nortek GoControl QuickStick Combo Model HUSBZB-1 (Z-Wave & Zigbee USB Adapter) and Telegesis ETRX357USB adapter. 

This docker image provides an environment to update the EmberZNet NCP application firmware from the base version 5.4.1-194 (or any other version) that is shipped with the adapter to the latest publicly available EmberZNet NCP application firmware from Silicon Labs (6.7.8) or any other included version. 

Please submit a pull request to this GitHub repository with any other known working versions (older and newer).

**Note!** Please understand that as of September 2020, the 6.x.x releases and higher of SiLabs EmberZNet will require Home Assistant 0.115 or higher. 

## To use:
`docker run --rm --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware`

Replace */dev/ttyUSB1* with the path to the zigbee side of your USB stick. Make sure that nothing else is currently using the port (i.e. Shutdown and stop Home Assistant)

Example output, currently just a scan reporting current FW version: 
```
docker run --rm --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware
{"ports": [{"stackVersion": "5.4.1-194", "deviceType": "zigbee", "pid": "8A2A", "port": "/dev/ttyUSB1", "vid": "10C4"}]}
Found zigbee port at /dev/ttyUSB1 running 5.4.1-194
```

### Selecting the correct firmware file

For Nortek GoControl QuickStick Combo Model HUSBZB-1 and integration with bellows/zigpy you will want the `ncp-uart-sw-6.7.8.ebl` image. This provides EZSP v8 support. Please note that the EM3581 has been deprecated by SiLabs and support has been dropped in future releases of EmberZNet. 

For Telegesis ETRX357USB adapter and integration with bellows/zigpy you will want the `em357-v665-ncp-uart-sw.ebl` image.

As of September 2020, hardware flow control is not supported by bellows/zigpy. Don't flash any of the images in the `hw-flow-control` folder unless you know what you are doing. 

### Manual firmware update procedure
If you want to use this image to manually update your firmware first shut down Home Assistant, or any other program accessing the port.

Then start a shell from the docker image:

```
docker run --rm --device=/dev/ttyUSB1:/dev/ttyUSB1 -it walthowd/husbzb-firmware bash
```
Make sure you are in */tmp/silabs* by changing directory and then flash:
```
cd /tmp/silabs
./ncp.py flash -p /dev/ttyUSB1 -f ncp-uart-sw-6.7.8.ebl
Restarting NCP into Bootloader mode...
CEL stick
EM3581 Serial Bootloader v5.4.1.0 b962

Successfully restarted into bootloader mode! Starting upload of NCP image... 
Finished!
Rebooting NCP...
```
Wait for the stick to reboot, then run *ncp.py* again to verify upgrade
```
./ncp.py scan
Connecting to.. /dev/ttyUSB1 57600 True False 
{"ports": [{"stackVersion": "6.7.8-204", "deviceType": "zigbee", "pid": "8A2A", "port": "/dev/ttyUSB1", "vid": "10C4"}]}
```

### Coordinator migration
Latest versions of bellows support migrating from one coordinator to another. This allows you to move between sticks without resetting and rejoining all devices in your zigpy network. 

For seamless migration, you need to overwrite the EUI64 on your target adapter. This is a one time operation and can not be undone or changed in future (without a SWD flasher) so this should only be done if you are sure of the change. If you do not overwrite the EUI64 the binding tables on your devices will be incorrect and they will need to be reset and rejoined. 

For Elelabs adapters with hardcodes baud rates, you need to always add `-b 115200` as a paramter to bellows.  

NOTE: This is currently in testing mode.

To backup your existing configration:
```
docker run --rm --device=/dev/ttyUSB1:/dev/ttyUSB1 -v .:/data -e EZSP_DEVICE='/dev/ttyUSB1' -e LANG='C.UTF-8' -it walthowd/husbzb-firmware bash
bellows info
bellows backup > /data/bellows-backup.txt
exit
```

Remove old stick, insert new stick (find correct ttyUSB port in `dmesg`) and restart container:
```
docker run --rm --device=/dev/ttyUSB1:/dev/ttyUSB1 -v .:/data -e EZSP_DEVICE='/dev/ttyUSB1' -e LANG='C.UTF-8' -it walthowd/husbzb-firmware bash
bellows info
bellows restore --i-understand-i-can-update-eui64-only-once-and-i-still-want-to-do-it -B /data/bellows-backup.txt
bellows info
```
On subsequent `bellows info` runs check that the EUI64 matches your backup, that the PANID matches and that the trustCenterLongAddress addresses matches. If they do not match, re-run the `bellows restore` as `bellows restore -f -B /data/bellows-backup.txt` (Omitting the `--i-understand-i-can-update-eui64-only-once-and-i-still-want-to-do-it`)

### HUSBZB-1 Firmware Recovery

In the event of a bad flash or unexpected event, the bootloader for the EM3581 on the HUSBZB-1 can be accessed by resetting the stick and shorting TP17 to GND with a serial connection (115200, 8/N/1, no hw or sw flow control).

On device startup, unshort TP17 and send a carriage return over the serial connection. You should be returned to the bootloader menu where a image can be uploaded via XMODEM.

![HUSBZB-1](husbzb-1.jpg)

An example of the process using minicom:

* Connect the HUSBZB-1 to the USB port
* Configure minicom with the right settings:

   ```
   $ minicom -s
      -> Select "Serial port setup"
      -> Type A and set the path of the device, ex: /dev/ttyUSB1
      -> Type E and set 115200 8N1 as the value
      -> Type F and G and choose: No
      -> Hit enter, save the settings, and exit minicom
   ```
* Now you can open `minicom` again and keep it open
   ```
   $ minicom
   ```
* Disconnect your HUSBZB-1 and open the case to be able to access the board (like in the previous image)
* Short TP17 to GND with something like a paperclip (touch both connectors with the paperclip)
* Connect the HUSBZB-1 to the USB port again, making sure the short is still on
* Wait few seconds and unshort TP17 (release the paperclip)
* Go back to minicom and hit enter few times. You should see a menu with the following elements. If you don't see it, the shorting probably didn't work well. Try to do it again:
   ```
   EM3581 Serial Bootloader v5.4.1.0 b962
   1. upload ebl
   2. run
   3. ebl info
   BL > 
   ```
* Choose 1. and the stick will start waiting for you to send the firmware (you will see multiple `Cs` written in the screen)
* Now type `Ctrl+A Z` to open the menu and select S (for sending the file). Write down the full path of the ebs file (ex: `/tmp/silabs/ncp-uart-sw-6.6.5.ebl` and hit enter. 
* Once the file has been completely sent (it can take a while), the process is done
