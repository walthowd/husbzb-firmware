FROM ubuntu:18.04 
MAINTAINER Walt Howd <walthowd@gmail.com>

VOLUME ["/config"]

RUN apt-get update \
  && apt-get install -y wget python-pip unzip

RUN pip install xmodem pyserial

RUN mkdir -p /tmp/silabs

# Get firmware
RUN cd /tmp/silabs && wget http://developer.silabs.com/studio/v4/control/stacks/PrivateGA/updates/binary/com.silabs.stack.znet.v6.4.feature_root_6.4.1.0
RUN cd /tmp/silabs &&  unzip -p com.silabs.stack.znet.v6.4.feature_root_6.4.1.0 developer/sdks/gecko_sdk_suite/v2.4/protocol/zigbee/ncp-images/em3581/ncp-uart-xon-xoff-use-with-serial-uart-btl-6.4.1.ebl > ncp-uart-xon-xoff-use-with-serial-uart-btl-6.4.1.ebl

# Get ncp.py
RUN cd /tmp/silabs && wget http://devtools.silabs.com/solutions/apt/pool/main/s/silabs-zigbee-gateway/silabs-zigbee-gateway_2.5.0-3_armhf.deb
RUN cd /tmp/silabs && ar x /tmp/silabs/silabs-zigbee-gateway_2.5.0-3_armhf.deb
RUN cd /tmp/silabs && tar -xvf data.tar.gz ./opt/siliconlabs/zigbeegateway/tools/ncp-updater/ncp.py --strip-components 6 -C /tmp/silabs/
RUN cd /tmp/silabs && sed -i "s/CEL_PID.=.*/CEL_PID = '8A2A'/" ncp.py

CMD [ "/usr/bin/python2.7", "/tmp/silabs/ncp.py", "scan" ]
