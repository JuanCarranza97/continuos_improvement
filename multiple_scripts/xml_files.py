import os,sys,subprocess
import xml.etree.ElementTree as et
import time
from datetime import datetime

version = "0.8.1"

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

testName = xml_data.attrib["name"] #Getting the concurrency test name from xml

def get_seconds(expression_time):
    #---------------------------------------------------------------------------------------
    #   Function: get_seconds
    #   This function is used to get the time in secods from expression  Hr:Min:Sec
    #   Example:
    #       seconds=get_seconds("01:02:03")
    #   Seconds variable is equals to 3723  
    #---------------------------------------------------------------------------------------
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
    #---------------------------------------------------------------------------------------
    #   Function: get_time_expression
    #   This function is used to get the expression in format Hr:Min:Sec 
    #   introducing the time in seconds
    #   Example:
    #       expression=get_time_expression(3723)
    #   Expression variable is equals to 01:02:03
    #---------------------------------------------------------------------------------------
    seconds_input=int(seconds_input)
    hours=(seconds_input/3600)
    mins=(seconds_input%3600)/60
    seconds=seconds_input-hours*3600-mins*60
    expression="%02d:%02d:%02d" %(hours,mins,seconds)
    return expression

def initializing_concurrency(process,testName):
    print("{}{}{}".format("-"*23,"-"*27,"-"*23))
    print("{} Concurrency Multi Scripts V {} {}".format("-"*20,version,"-"*20))
    print("{}{}{}".format("-"*23,"-"*27,"-"*23))
    time.sleep(1)
    print("\n\nTest Name: {}".format(testName))
    print("Process to Run:")
    for i in process:
        i.print_data()
        time.sleep(1)
    print("{}\n\n".format("-"*70))


class Test():
    def __init__(self,xml_object,test_id):
        self.name               = xml_object.attrib["name"]
        self.testID             = test_id

        self.preTestCommandLine = xml_object.find("pretest_command").text
        if self.preTestCommandLine == "" or self.preTestCommandLine == "NOTHING":
            self.preTestXterm   = "NOTHING"
        else:
            self.preTestXterm   = "xterm -e '{} ; echo $? > returnCode_pre{}.log'".format(self.preTestCommandLine,self.testID)
                          
        self.delayTime          = xml_object.find("delay_time").text
        if not self.delayTime == "ALL_FINISHED":
            self.delayTime      = get_seconds(self.delayTime)  

        self.estimatedTime      = get_seconds(xml_object.find("estimated_time").text)
        self.timeout            = get_seconds(xml_object.find("timeout").text)  

        self.commandLine        = xml_object.find("command_line").text    
        if self.commandLine == "" or self.commandLine == "NOTHING":
            self.xtermLine      = None
        else:
            self.xtermLine          = "xterm -e '{} ; echo $? > returnCode_{}.log'".format(self.commandLine,self.testID)

        self.status             = "Not Run"
        self.endDate            = None
        self.initDate           = None
        self.runningTime        = "Not Run"

    def print_data(self):
        print("    {}{}{}".format("-"*20,self.name,"-"*20))
        print("        Test ID: {}".format(self.testID))
        print("        PreTest line: {}".format(self.preTestCommandLine))
        print("        Command line: {}".format(self.commandLine)) 
        print("        Delay time: {}".format(self.delayTime))
        print("        Estimated time: {}".format(self.estimatedTime))
        print("        TimeOut: {}".format(self.timeout))
        #print("    XtermLine: {}".format(self.xtermLine))

    def run_pre_test(self):
        if self.preTestXterm == "NOTHING":
            print("  --{}-- Pretest was not defined ".format(self.name))
        else:
            os.system("printf '  --{}-- Initializing pretest'".format(self.name))
            
            self.preTestProcess=subprocess.Popen(self.preTestXterm,shell=True)

            loading_counter=0
            while self.preTestProcess.poll() == None: #Wait for process end
                os.system("printf '\r  --{}-- Running pretest ...{}'".format(self.name,loading_symbols[loading_counter]))
                loading_counter+=1
                if loading_counter == 4: 
                    loading_counter=0
                time.sleep(.5)

            self.preTestReturnCode=int(open("returnCode_pre{}.log".format(self.testID),"r").read()[0])
            os.system("rm returnCode_pre{}.log -rf".format(self.testID))
            if self.preTestReturnCode != 0:
                os.system("printf '\n'")
                print("Error: Pretest of {} Failed with Error code {}".format(self.name,self.preTestReturnCode))
                print("Test Failed!! :c")
                exit(1)
            else:
                os.system("printf '\r  --{}-- Pretest end succesfully\n'".format(self.name))

    def run_test(self):  
        if not self.delayTime == "ALL_FINISHED":  
            self.initTime    = time.time()
            self.runningTime = 0
            if self.delayTime == 0:
                self.process=subprocess.Popen(self.xtermLine,shell=True)
                self.initDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print("  --{}-- started at {} with PID {}".format(self.name,self.initDate,self.process.pid))
                self.status="running"
            else:
                print("  --{}-- will wait  {} to init".format(self.name,get_time_expression(self.delayTime)))
                self.status="waiting"
            return True
        else:
            print("  --{}-- will run if all test ends succesfully ".format(self.name))
            return False

    def run_all_finished(self):
        print("Running all finished {}".format(self.name))
        self.process=subprocess.Popen(self.xtermLine,shell=True)
        self.initTime    = time.time()
        self.runningTime = 0
        self.initDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status="running"

        loading_counter=0
        while self.process.poll() == None: #Wait for process end
            os.system("printf '\r  --{}-- Running all finished... {}'".format(self.name,loading_symbols[loading_counter]))
            loading_counter+=1
            if loading_counter == 4: 
                loading_counter=0
            time.sleep(.5)
            self.runningTime=time.time() - self.initTime

        self.endDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.allFinishedReturnCode=int(open("returnCode_{}.log".format(self.testID),"r").read()[0])
        os.system("rm returnCode_{}.log -rf".format(self.testID))
        os.system("printf '\n'")

        if self.allFinishedReturnCode == 0:
            self.status="passed"
            print("  --{}-- end succesfully at {}".format(self.name,self.endDate))
        else:
            self.status="failed"
            print("  --{}-- failed with error code {} at {}".format(self.name,self.allFinishedReturnCode,self.endDate))




    def print_summary(self):
        print("{}{}{}".format("-"*20,self.name,"-"*20))
        print("    Command line: {}".format(self.commandLine)) 

        if not self.delayTime == "ALL_FINISHED":
            print("    Delay time: {}".format(get_time_expression(self.delayTime)))
        else:
            print("    Delay time: {}".format(self.delayTime))

        if self.status != "Not Run":
            print("    Start Date: {}".format(self.initDate))
            print("    End Date: {}".format(self.endDate))
            print("    Time Running: {}".format(get_time_expression(int(self.runningTime))))
        print("    Test status: {}".format(self.status.capitalize()))
        

    def update(self):   
        if not self.delayTime == "ALL_FINISHED":    
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

def run_all_pretest(process):
    print("\n{} Running Pretests {}".format("*"*30,"*"*29))
    for i in process:
        i.run_pre_test()

def run_all(process):
    print("\n{} Initializing Tests {}".format("*"*30,"*"*27))
    initialized=0
    for current_process in process:
        if current_process.run_test():
            initialized+=1
    return initialized


def some_running(process):
    status=False
    for i in process:
        if i.status == "running" or i.status == "waiting":
            status=True
            break
    return status

def all_passed(process,involveAllFinished=False):
    status=True
    for i in process:
        if i.status == "failed" :
            status=False
            break
        elif involveAllFinished == True:
            if i.delayTime == "ALL_FINISHED" and i.status == "Not Run":
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
initializing_concurrency(concurrency_tests,testName)

run_all_pretest(concurrency_tests)

all_process = len(concurrency_tests)
test_process_running = run_all(concurrency_tests)

print(" ----{}/{} Process were initialized ----".format(test_process_running,all_process))

print("\n{} Monitoring {}".format("*"*32,"*"*33))
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


if all_passed(concurrency_tests):
    print("\n{} Running ALL TEST Finished test{} ".format("*"*30,"*"*30))
    for i in concurrency_tests:
        if i.delayTime == "ALL_FINISHED":
            i.run_all_finished()

summary_process(concurrency_tests)
if all_passed(concurrency_tests,True):
    print("\nTest ends succesfully :)")
    exit(0)
else:
    print("\nTest Failed!! :c")
    exit(1)