from time import sleep
import sys
print("Welcome to script 1...")

for i in range(5):
    print("Value is {}".format(i))
    sleep(1)
    sys.stdout.flush()
print("Scripts end")
exit(0)
