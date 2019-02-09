#!/usr/bin/python
import os,re
"""This class is used to specify the storage device and this includes
    -name (Is the way that our device is named by our system)
    -device_type (This attriubute specify if our device is sata,usb,emmc or nvme for our sysmer)
    -partitions (This attribute have the partition por our system listed in an array, each 
     partition has as atribute name,isMounted and mountedPath)"""
class storage_device():
    """This is the init function, when a new storage device is created,
        we need to specify  the device type and the kind of device that 
         we have mounted in our system"""
    class partition():
        def __init__(self,name
    def __init__(self,name,device_type):
        self.name=name
        self.device_type=device_type
        self.partitions=[]
    
    def update_partitions():
        print("Search partition function")
        if self.device_type == "sata" or "usb":
            partition_pattern=re.compile(self.name+"\d{1,2}")
            if 
def get_devices():
    lsblk=os.popen("lsblk").read().split("\n")
    sd_pattern=re.compile("sd[a-z]$")
    nvme_pattern=re.compile("nvme[0-9]n1$")
    emmc_pattern=re.compile("mmcblk[0-9]$")
    devices=[]
    for lsblk_line in lsblk:
        device_name=lsblk_line.split(" ")[0]
        if sd_pattern.match(device_name):
            devices.append(storage_device(device_name,"sata"))
        elif nvme_pattern.match(device_name):
            devices.append(storage_device(device_name,"nvme"))
        elif emmc_pattern.match(device_name):
            devices.append(storage_device(device_name,"emmc"))
    return devices

devices=get_devices()
for i in devices:
    print("Device Name: {} - Device Type: {}".format(i.name,i.device_type))
