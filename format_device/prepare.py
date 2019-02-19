#!/usr/bin/python
import os,re
"""This class is used to specify the storage device and this includes
    -name (Is the way that our device is named by our system)
    -device_type (This attriubute specify if our device is sata,usb,emmc or nvme for our sysmer)
    -partitions (This attribute have the partition por our system listed in an array, each 
     partition has as atribute name,isMounted and mountedPath)"""
class storage_device():
    class partition():
        def __init__(self,name):
            self.name=name
            self.isMounted=False
            self.mountPoint="none"

        def update_status(self):
            lsblk=os.popen("lsblk").read().split("\n")
            #lsblk -o MOUNTPOINT
            for current_line in range(len(lsblk)):
                if lsblk[current_line].find(self.name) > 0:#If the partition name is found in lsblk line
                    self.mountPoint=os.popen("lsblk -o MOUNTPOINT").read().split("\n")[current_line]
                    if self.mountPoint != "":
                        self.isMounted=True
                    else:
                        self.isMounted=False

        def print_summary(self):
            if self.isMounted:
                print("  -{} is mounted at {}".format(self.name,self.mountPoint))
            else:
                print("  -{} is not mounted".format(self.name))

    """This is the init function, when a new storage device is created,
        we need to specify  the device type and the kind of device that 
         we have mounted in our system"""
    def __init__(self,name,deviceType):
        self.name=name
        self.deviceType=deviceType
        self.partitions=[]
    """This function is used to sear partitions of an specific device in our system,
        there is an specific regular expression for every kind of device (except sata and usb)
        When we found that a partition is in our system we create an object of type partition
        and we define here the partiton name, if it is mount and mountedPath"""
    def update_partitions(self):
        lsblk=os.popen("lsblk").read().split("\n")
        
        if self.deviceType == "sata" or self.deviceType == "usb":
            partition_pattern=re.compile(self.name+"\d{1,2}$")
        elif self.deviceType == "nvme":
            partition_pattern=re.compile(self.name+"p\d{1,2}$")        
        elif self.deviceType == "emmc":
            partition_pattern=re.compile(self.name+"p\d{1,2}$")
        
        self.partitions=[]
        for current_line in lsblk:
            device_name=current_line.split(" ")[0]
            try:
                device_name=self.name+device_name.split(self.name)[1]
                if partition_pattern.match(device_name):
                    self.partitions.append(self.partition(device_name))
            except:
                pass
        for current_partition in self.partitions:
            current_partition.update_status()

    def print_summary(self):
        print("{}Storage Device Summary{}".format("-"*20,"-"*20))
        print(" Device Name: {}".format(self.name))
        print(" Device Type: {}".format(self.deviceType))
        print(" Partitions Number: {}".format(len(self.partitions)))
        for i in self.partitions:
            i.print_summary()
    

def get_devices():
    lsblk=os.popen("lsblk").read().split("\n")
    sd_pattern=re.compile("sd[a-z]$")
    nvme_pattern=re.compile("nvme[0-9]n1$")
    emmc_pattern=re.compile("mmcblk[0-9]$")
    devices=[]
    for lsblk_line in lsblk:
        device_name=lsblk_line.split(" ")[0]
        if sd_pattern.match(device_name):
            device_type=os.popen("udevadm info --query=all --name="+device_name+" | grep ID_BUS").read().split("\n")[0].split("=")[1]
            if device_type == "ata":
                devices.append(storage_device(device_name,"sata"))
            if device_type == "usb":
                devices.append(storage_device(device_name,"usb"))
        elif nvme_pattern.match(device_name):
            devices.append(storage_device(device_name,"nvme"))
        elif emmc_pattern.match(device_name):
            devices.append(storage_device(device_name,"emmc"))
        #if len(devices) > 0:
        #    devices[len(devices)-1].update_partitions()
    for i in devices:
        i.update_partitions()
    return devices

devices=get_devices()
for i in devices:
    i.print_summary()
