import os,sys
import xml.etree.ElementTree as et

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
except:
    print("Sorry, There is an error with your xml file :c")
    exit(1)
concurrency_test=tree.getroot()

loop=1
for test in concurrency_test:
    print("  {}.-{}".format(loop,test.attrib["name"]))
    command_line=test.find("command_line").text
    delay_time=test.find("delay_time").text    
    estimated_time=test.find("estimated_time").text 
    timeout=test.find("timeout").text
    print("    Command line: {}".format(command_line)) 
    print("    Delay time: {}".format(delay_time))
    print("    Estimated time: {}".format(estimated_time))
    print("    TimeOut: {}".format(timeout))
    loop+=1