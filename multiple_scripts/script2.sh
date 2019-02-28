#!/bin/bash
echo "Initializing script .."
sleep 1
for i in `eval echo {1..$1}`; do
    echo "Running script ... $i"
    sleep .5
done
echo "Done script :c"
exit 4
