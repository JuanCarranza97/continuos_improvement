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

def get_seconds(expression_time):
    arguments=expression_time.split(":")
    if len(arguments) == 3:
        time=int(arguments[2]) #Initialize time variable with seconds
        time+=(int(arguments[0])*3600) #Add hours converted to seconds in variable
        time+=(int(arguments[1])*60) #Add Mins converted to seconds in variable
        return time
    else:
        print("Entered expression time {} is not correct".format(expression_time))
        exit(2)

def get_time_expression(seconds_input):
    seconds_input=int(seconds_input)
    hours=(seconds_input/3600)
    mins=(seconds_input%3600)/60
    seconds=seconds_input-hours*3600-mins*60
    expression="%02d:%02d:%02d" %(hours,mins,seconds)
    return expression

class Test():
    def __init__(self,xml_object,test_id):
        self.name=xml_object.attrib["name"]
        self.commandLine=xml_object.find("command_line").text
        self.delayTime=get_seconds(xml_object.find("delay_time").text)    
        self.estimatedTime=xml_object.find("estimated_time").text 
        self.timeout=xml_object.find("timeout").text
        self.testID=test_id
        self.xtermLine="xterm -e '{} ; echo $? > returnCode_{}.log'".format(self.commandLine,self.testID)
        self.status="notRun"
        self.endDate=0
        self.initDate=0

    def print_data(self):
        print("{}{}{}".format("-"*20,self.name,"-"*20))
        print("    Test ID: {}".format(self.testID))
        print("    Command line: {}".format(self.commandLine)) 
        print("    Delay time: {}".format(self.delayTime))
        print("    Estimated time: {}".format(self.estimatedTime))
        print("    TimeOut: {}".format(self.timeout))
        print("    XtermLine: {}".format(self.xtermLine))

    def run_test(self):        
        self.initTime=time.time()
        self.runningTime=0
        if self.delayTime == 0:
            self.process=subprocess.Popen(self.xtermLine,shell=True)
            self.initDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("  --{}-- started at {} with PID {}".format(self.name,self.initDate,self.process.pid))
            self.status="running"
        else:
            print("  --{}-- will wait  {} to init".format(self.name,get_time_expression(self.delayTime)))
            self.status="waiting"

    def print_summary(self):
        print("{}{}{}".format("-"*20,self.name,"-"*20))
        print("    Command line: {}".format(self.commandLine)) 
        print("    Delay time: {}".format(get_time_expression(self.delayTime)))
        if self.status != "not run":
            print("    Start Date: {}".format(self.initDate))
            print("    End Date: {}".format(self.endDate))
            print("    Time Running: {}".format(get_time_expression(int(self.runningTime))))
        print("    Test status: {}".format(self.status.capitalize()))
        

    def update(self):        
        if self.status=="waiting":
            self.runningTime=time.time() - self.initTime
            if self.runningTime >= self.delayTime:
                self.initTime=time.time()
                self.runningTime=0
                self.process=subprocess.Popen(self.xtermLine,shell=True)
                self.initDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("  --{}-- started at {} with PID {}".format(self.name,self.initDate,self.process.pid))
                self.status="running"

        elif self.status == "running":   
            self.runningTime=time.time() - self.initTime
            if self.process.poll() != None: #If process stop running
                self.endDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.returnCode=int(open("returnCode_{}.log".format(self.testID),"r").read()[0])
                os.system("rm returnCode_{}.log -rf".format(self.testID))
                
                if self.returnCode == 0:
                    self.status="passed"
                    print("  --{}-- end succesfully at {}".format(self.name,self.endDate))
                else:
                    self.status="failed"
                    print("  --{}-- failed with error code {} at {}".format(self.name,self.returnCode,self.endDate))

    def kill_process(self):
        self.update()
        if self.status == "running":
            self.process.kill()
            self.endDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.endTime=time.time()
            self.status = "killed"
            print("  --{}-- killed  at {}".format(self.name,self.endDate))

        elif self.status == "waiting":
            self.status = "not run"
            self.runningTime=0
            print("  --{}-- killed  at {}".format(self.name,self.endDate))


def create_process(xml_data):
    concurrency_tests=[]
    script_number=1
    for test in xml_data:
        concurrency_tests.append(Test(test,script_number))
        script_number+=1
    return concurrency_tests

def run_all(process):
    print("\n{} Initializing Tests {}".format("*"*30,"*"*30))
    for current_process in process:
        current_process.run_test()

def some_running(process):
    status=False
    for i in process:
        if i.status == "running" or i.status == "waiting":
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

def kill_remaining_process(process):
    for i in process:
        i.update()
        if i.status == "running" or i.status == "waiting":
            i.kill_process()

def summary_process(process):
    print("\n{} Test Summary {}".format("*"*30,"*"*30))
    for i in process:
        i.print_summary()

concurrency_tests=create_process(xml_data)
run_all(concurrency_tests)

print("\n{} Monitoring {}".format("*"*30,"*"*30))
while(1):
    os.system("printf 'Running...{}\r'".format(loading_symbols[loading_counter]))
    for current_process in concurrency_tests:
        current_process.update()
        if current_process.status == "failed":
            kill_remaining_process(concurrency_tests)

    if  some_running(concurrency_tests):       
        loading_counter+=1
        if loading_counter == 4:
            loading_counter=0
    else:
        break
    time.sleep(.5)

summary_process(concurrency_tests)
if all_passed(concurrency_tests):
    print("\nTest ends succesfully :)")
    exit(0)
else:
    print("\nTest Failed!! :c")
    exit(1)
