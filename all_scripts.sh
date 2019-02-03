#!/bin/bash

commands=( "python python1.py"
           "python python2.py" )
pids=()
pid_status=()
echo "There are ${#commands[@]} scripts" | tee concurrency_$$.log
for i in ${!commands[@]}; do
    log_name=`echo "${commands[$i]}" | tr " " _ | cut -f1 -d'.'`
    echo "Log name is $log_name"
    ${commands[$i]} >> "output-$log_name-$$.log" &
    pids+=($!)
    echo "    --${commands[$i]}-- is running with pid ${pids[$i]}" | tee -a concurrency_$$.log
    pid_status[$i]="running"
done

running=1
finished=0
error_codes=()
while [ $running -eq 1 ]; do
    for i in ${!commands[@]}; do
        if [ -n "${pids[$i]}" -a -e /proc/${pids[$i]} ]; then
            echo "process ${pids[$i]} exists ..."
        elif [ "${pid_status[$i]}" == "running" ]; then 
            wait "${pids[$i]}"
	    error_codes[$i]=$?
	    finished=$((finished+1))
	    pid_status[$i]="finished"
	    DATE=`date '+%Y-%m-%d %H:%M:%S'`

	    if [ ${error_codes[$i]} -ne 0 ]; then
                echo "The command line --${commands[$i]}-- ends with error code ${error_codes[$i]} at $DATE" | tee -a concurrency_$$.log

		#If process are running yet, kill them
		if [ $finished -ne ${#pids[@]} ]; then
		    echo "Stoping all pids ..."
	            for j in ${!pids[@]}; do
                        if [ ${pid_status[$j]} == "running" ]; then
	                     if [ -n "${pids[$j]}" -a -e /proc/${pids[$j]} ]; then
		    	         printf "    Killing --${commands[$j]}-- ..." | tee -a concurrency_$$.log
		    	         kill ${pids[$j]}
	                         DATE=`date '+%Y-%m-%d %H:%M:%S'`
		    	         printf " killed at $DATE\n" | tee -a concurrency_$$.log
		    	         pid_status[$j]="killed"
		             else
		                 wait "${pids[$j]}"
		    	         error_codes[$j]=$?
				 echo "    --${commands[$j]}-- ends before we kill it at $DATE, error code ${error_codes[$j]}" | tee -a concurrency_$$.log
		                 finished=$((finished+1))
		    	         pid_status[$j]="finished"
		             fi
		        fi
		    done
	        fi
		echo "Test FAILED!!" | tee concurrency_$$.log
		exit 1
	    fi
	    echo "--${commands[$i]}-- pid(${pids[$i]}) finished correctly at $DATE" | tee -a concurrency_$$.log
        fi
    done
    sleep .5
    #echo "before compare $finished"
    if [ $finished -ge ${#commands[@]} ]; then
        echo "All process finished correctly :)" | tee -a concurrency_$$.log
	echo "Test PASSED!!" | tee -a concurrency_$$.log 
	running=0
	exit 0
    fi
done
