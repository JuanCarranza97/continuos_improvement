import os,sys,subprocess
import xml.etree.ElementTree as et
import time
from datetime import datetime

file_name="my_config.xml"
loading_symbols=["|","/","-","\\"]
loading_counter=0

if __name__ == '__main__':
    input_argv=sys.argv[1:]
    while len(input_argv) > 0:
        current=input_argv.pop(0)
        if current == '-c':
            file_name=input_argv.pop(0)
            print("File name is {}".format(file_name))

base_path=os.path.dirname(os.path.realpath(__file__))
xml_file=os.path.join(base_path,file_name)

try:
    tree=et.parse(xml_file)
    xml_data=tree.getroot()
except:
    print("Sorry, There is an error with your xml file :c")
    exit(1)


class Test():
    def __init__(self,xml_object,test_id):
        self.name=xml_object.attrib["name"]
        self.commandLine=xml_object.find("command_line").text
        self.delayTime=xml_object.find("delay_time").text    
        self.estimatedTime=xml_object.find("estimated_time").text 
        self.timeout=xml_object.find("timeout").text
        self.testID=test_id
        self.xtermLine="xterm -e '{} ; echo $? > returnCode_{}.log'".format(self.commandLine,self.testID)
        self.status="notRun"

    def print_data(self):
        print("{}{}{}".format("-"*20,self.name,"-"*20))
        print("    Test ID: {}".format(self.testID))
        print("    Command line: {}".format(self.commandLine)) 
        print("    Delay time: {}".format(self.delayTime))
        print("    Estimated time: {}".format(self.estimatedTime))
        print("    TimeOut: {}".format(self.timeout))
        print("    XtermLine: {}".format(self.xtermLine))

    def run_test(self):
        self.process=subprocess.Popen(self.xtermLine,shell=True)
        self.initDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.initTime=time.time()
        self.runningTime=0
        print("  --{}-- started at {} with PID {}".format(self.name,self.initDate,self.process.pid))
        self.status="running"

    def update(self):
        if self.status == "running":
            self.runningTime=time.time() - self.initTime

            if self.process.poll() != None: #If process stop running
                self.endDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.endTime=self.runningTime
                self.returnCode=int(open("returnCode_{}.log".format(self.testID),"r").read()[0])
                os.system("rm returnCode_{}.log -rf".format(self.testID))
                
                if self.returnCode == 0:
                    self.status="passed"
                    print("Script --{}-- ends succesfully at {}".format(self.name,self.endDate))
                else:
                    self.status="failed"
                    print("Script --{}-- fails with error code {} at {}".format(self.name,self.returnCode,self.endDate))

def create_process(xml_data):
    concurrency_tests=[]
    script_number=1
    for test in xml_data:
        concurrency_tests.append(Test(test,script_number))
        script_number+=1
    return concurrency_tests

def run_all(process):
    for current_process in process:
        current_process.run_test()

def some_running(process):
    status=False
    for i in process:
        if i.status == "running":
            status=True
            break
    return status

def all_passed(process):
    status=True
    for i in process:
        if i.status == "failed":
            status=False
            break
    return status

concurrency_tests=create_process(xml_data)
run_all(concurrency_tests)

print("All scripts initialized ...\n")
while(1):
    os.system("printf 'Running...{}\r'".format(loading_symbols[loading_counter]))
    #print("\rRuning ... {}".format(loading_symbols[loading_counter]))
    for current_process in concurrency_tests:
        current_process.update()

    if  some_running(concurrency_tests):       
        loading_counter+=1
        if loading_counter == 4:
            loading_counter=0
    else:
        break
    time.sleep(.5)

if all_passed(concurrency_tests):
    print("\nTest ends succesfully :)")
    exit(0)
else:
    print("\nTest Failed!! :c")
    exit(1)
   