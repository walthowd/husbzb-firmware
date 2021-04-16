#FROM ubuntu:20.04 
FROM python:buster

MAINTAINER Walt Howd <walthowd@gmail.com>

WORKDIR /tmp/silabs

#RUN apt-get update \
#  && apt-get install -y git wget python3-pip unzip jq curl python2.7 python2

RUN apt-get update \
  && apt-get install -y git wget python3-pip unzip jq curl

RUN pip3 install --upgrade git+git://github.com/zigpy/bellows.git

RUN pip3 install pyserial xmodem

#RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output /tmp/get-pip.py

#RUN python2 /tmp/get-pip.py

#RUN pip2 install xmodem pyserial

RUN mkdir -p /tmp/silabs

# Get firmware
#RUN wget http://developer.silabs.com/studio/v4/control/stacks/PrivateGA/updates/binary/com.silabs.stack.znet.v6.4.feature_root_6.4.1.0
#RUN unzip -p com.silabs.stack.znet.v6.4.feature_root_6.4.1.0 developer/sdks/gecko_sdk_suite/v2.4/protocol/zigbee/ncp-images/em3581/ncp-uart-xon-xoff-use-with-serial-uart-btl-6.4.1.ebl > ncp-uart-xon-xoff-use-with-serial-uart-btl-6.4.1.ebl
#RUN rm -f /tmp/silabs/com.silabs.stack.znet.v6.4.feature_root_6.4.1.0

# Get ncp.py
#RUN wget http://devtools.silabs.com/solutions/apt/pool/main/s/silabs-zigbee-gateway/silabs-zigbee-gateway_2.5.0-3_armhf.deb
#RUN ar x /tmp/silabs/silabs-zigbee-gateway_2.5.0-3_armhf.deb
#RUN tar -xvf data.tar.gz ./opt/siliconlabs/zigbeegateway/tools/ncp-updater/ncp.py --strip-components 6 -C /tmp/silabs/
#RUN sed -i "s/CEL_PID.=.*/CEL_PID = '8A2A'/" ncp.py
#RUN rm -f silabs-zigbee-gateway_2.5.0-3_armhf.deb
#RUN rm -f *.gz
#RUN rm -f /tmp/silabs/debian-binary

ADD update-firmware.sh /tmp/silabs
ADD ncp.py /tmp/silabs
ADD *.ebl /tmp/silabs/

CMD /tmp/silabs/update-firmware.sh
