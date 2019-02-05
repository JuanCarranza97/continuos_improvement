#!/bin/bash

if [ "$#" -eq 0 ]; then
    echo "You must enter at least 1 argument"
    exit 1
else
    process_list=( "$@" )
fi

for i in ${process_list[@]}; do
    echo "Process $i"
done
exit 0
