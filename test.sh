#/bin/bash

LS0=/mnt/local-ssd0

# Testing storage performance (local SSD, EBS SSD GP2) by fill rates.

# To make an instance store volume with TRIM support available for use on Linux
#   [http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ssd-instance-store.html]
#   - I2, R3's instance store volumes support TRIM
#   - I'm using an i2.xlarge instance.

setup_dirs() {
	sudo mkdir -p $LS0

	# Without nodiscard, it takes like 1 min for a 800GB SSD.
	time sudo mkfs.ext4 -m 0 -E nodiscard -L local-ssd0 /dev/xvdb

	sudo mount -t ext4 -o discard /dev/xvdb $LS0
	sudo chown -R ubuntu $LS0

	mkdir -p /home/ubuntu/ebs-tmp
}

#
# TODO: what's the underlying disk specs of the machine?
#   Not much from lshw
#   $ lshw
#     ubuntu@ip-10-164-205-205:~$ sudo lshw -class disk -class storage
#       *-ide
#            description: IDE interface
#            product: 82371SB PIIX3 IDE [Natoma/Triton II]
#            vendor: Intel Corporation
#            physical id: 1.1
#            bus info: pci@0000:00:01.1
#            version: 00
#            width: 32 bits
#            clock: 33MHz
#            capabilities: ide bus_master
#            configuration: driver=ata_piix latency=64
#            resources: irq:0 ioport:1f0(size=8) ioport:3f6 ioport:170(size=8) ioport:376 ioport:c100(size=16)
#
# hdparm doesn't work
# $ sudo hdparm -I /dev/xvdb
#   /dev/xvdb:
#    HDIO_DRIVE_CMD(identify) failed: Invalid argument
#
# $ sudo smartctl --all /dev/xvda
#    smartctl 6.2 2013-07-26 r3841 [x86_64-linux-3.13.0-85-generic] (local build)
#    Copyright (C) 2002-13, Bruce Allen, Christian Franke, www.smartmontools.org
#
#    /dev/xvda: Unable to detect device type

# TODO: wanna repeat 10 times, each time with a new instance. to avoid any side
# effects or any performance anomality, for example, from a bad VM, PM, or
# networking.

# IO queue size
#   [http://yoshinorimatsunobu.blogspot.com/2009/04/linux-io-scheduler-queue-size-and.html]
#   $ cat /sys/block/xvda/queue/nr_requests
#     128
#   $ cat /sys/block/xvdb/queue/nr_requests
#     128
#   Not sure how ioping goes with the queue size.

DT_BEGIN=`date +"%y%m%d-%H%M%S"`
mkdir -p ioping-output
FN_OUT=ioping-output/$DT_BEGIN
touch $FN_OUT

LS0_DN_RAND_DATA=$LS0/rand-data
rm -rf $LS0_DN_RAND_DATA
mkdir -p $LS0_DN_RAND_DATA

measure() {
	# Local SSD and EBS SSD directories
	ES=/home/ubuntu/ebs-tmp

	date +"%y%m%d-%H%M%S.%N" >> $FN_OUT

	# -p period  : Print raw statistics for every period requests.
	# -c count   : Stop after count requests.
	# -i interval: Set time between requests to interval (1s).
	# -q         : Suppress periodical human-readable output.
	#ioping -p 100 -c 200 -i 0 -q

	ioping -p 100 -c 100 -i 0      -q $LS0 >> $FN_OUT
	ioping -p 100 -c 100 -i 0 -WWW -q $LS0 >> $FN_OUT
	ioping -p 100 -c 100 -i 0      -q $ES  >> $FN_OUT
	ioping -p 100 -c 100 -i 0 -WWW -q $ES  >> $FN_OUT

	# Report free spaces
	df /dev/xvda1 /dev/xvdb >> $FN_OUT
}

while [ 1 ]; do
	measure
	dd if=/dev/urandom of=$LS0_DN_RAND_DATA/`date +"%y%m%d-%H%M%S.%N"` bs=1M count=20 > /dev/null 2>&1
	echo -n "."
done
