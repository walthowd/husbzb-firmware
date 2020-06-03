#!/bin/bash

SCAN=$(/usr/bin/python2.7 /tmp/silabs/ncp.py scan 2>/dev/null)

if echo $SCAN | grep zigbee; then
	PORT=$(echo $SCAN | jq '.ports' | jq '.[0]' | jq -r '.port')
	VERSION=$(echo $SCAN | jq '.ports' | jq '.[0]' | jq -r '.stackVersion')
	echo "Found zigbee port at $PORT running $VERSION"
else
	echo "Did not find compatible zigbee port. Please make sure you passed the correct device through to the docker image"
	exit 1
fi
