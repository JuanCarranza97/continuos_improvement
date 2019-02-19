import os,subprocess

print("Preparing to run scripts")

proc=subprocess.Popen("xterm -e 'bash script1.sh ; echo $? > error.log' &", shell=True)
print("I catch {}".format(proc.pid))

