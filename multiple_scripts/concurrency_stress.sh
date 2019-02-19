#!/bin/bash
#all_command = "xterm -e '{} ; echo $? > error.log' &".format(script
xterm -e 'bash script1.sh ; echo $? > error.log' &
pid=$!
echo "Script was initializaded.. "
wait $!
echo "The error code was $?"
echo "Script finished succesfully :)"
