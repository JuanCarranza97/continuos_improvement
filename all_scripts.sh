#!/bin/bash

commands=( "python python1.py"
           "python python2.py" )

loading_symbols=( "|" "/" "-" "\\" )
pids=()
pid_status=()
echo "PID test is $$" | tee concurrency_$$.log
echo "${#commands[@]} scripts will run" | tee -a concurrency_$$.log
for i in ${!commands[@]}; do
    log_name=`echo "${commands[$i]}" | tr " " _ | cut -f1 -d'.'`
    #echo "Log name is $log_name"
    ${commands[$i]} >> "output-$log_name-$$.log" &
    pids+=($!)
    echo "    --${commands[$i]}-- is running with pid ${pids[$i]}, log file name is -output-$log_name-$$.log" | tee -a concurrency_$$.log
    pid_status[$i]="running"
done
echo " " | tee -a concurrency_$$.log
running=1
finished=0
error_codes=()
test_status="Passed"
loading_counter=0
end_time=()
while [ $running -eq 1 ]; do
    printf "\rRunning  ${loading_symbols[$loading_counter]}"
    for i in ${!commands[@]}; do
        if [ -n "${pids[$i]}" -a -e /proc/${pids[$i]} ]; then
            running=1
            #echo "process ${pids[$i]} exists ..."
        elif [ "${pid_status[$i]}" == "running" ]; then 
            wait "${pids[$i]}"
            error_codes[$i]=$?
            end_time[$i]=`date '+%Y-%m-%d %H:%M:%S'`
            finished=$((finished+1))
            pid_status[$i]="finished"
            if [ ${error_codes[$i]} -ne 0 ]; then
                printf "\r"
                echo "The command line --${commands[$i]}-- ends with error code ${error_codes[$i]} at ${end_time[$i]}" | tee -a concurrency_$$.log
                test_status="Failed"
                #If process are running yet, kill them
                if [ $finished -ne ${#pids[@]} ]; then
                    echo "Stoping all pids ..."
                    for j in ${!pids[@]}; do
                        if [ ${pid_status[$j]} == "running" ]; then
                            if [ -n "${pids[$j]}" -a -e /proc/${pids[$j]} ]; then
                                printf "    Killing --${commands[$j]}-- ..." | tee -a concurrency_$$.log
                                kill ${pids[$j]} > /dev/null 2>&1
                                end_time[$j]=`date '+%Y-%m-%d %H:%M:%S'`
                                printf " killed at $DATE\n" | tee -a concurrency_$$.log
                                finished=$((finished+1))
                                pid_status[$j]="killed"
                             else
                                wait "${pids[$j]}"
                                error_codes[$j]=$?
                                end_time[$j]=`date '+%Y-%m-%d %H:%M:%S'`
                                echo "    --${commands[$j]}-- ends before we kill it at ${end_time[$j]}, error code ${error_codes[$j]}" | tee -a concurrency_$$.log
                                finished=$((finished+1))
                                pid_status[$j]="finished"
                            fi
                        fi
                    done
                fi
            else
                printf "\r"
                echo "--${commands[$i]}-- pid(${pids[$i]}) finished correctly at ${end_time[$i]}" | tee -a concurrency_$$.log
                pid_status[$i]="correctly"
            fi
        fi
    done
    #echo "before compare $finished"
    if [ $finished -ge ${#commands[@]} ]; then
        printf "\n-------------------------------------Summary-------------------------------------\n" | tee -a concurrency_$$.log
        for i in ${!commands[@]}; do
            if [ "${pid_status[$i]}" == "killed" ]; then
                echo "--${commands[$i]}--  was killed at ${end_time[$i]}" | tee -a concurrency_$$.log
            elif [ "${pid_status[$i]}" == "correctly" ]; then
                echo "--${commands[$i]}-- finished correctly at ${end_time[$i]}" | tee -a concurrency_$$.log
            else
                echo "--${commands[$i]}-- finished with error code ${error_codes[$i]} at ${end_time[$i]}" | tee -a concurrency_$$.log
            fi 
        done
        echo "---------------------------------------------------------------------------------" | tee -a concurrency_$$.log	
        if [ $test_status == "Passed" ]; then
            printf "\nAll process finished correctly :)\n" | tee -a concurrency_$$.log
            echo "Test PASSED!!" | tee -a concurrency_$$.log 
            running=0
            exit 0
        else
            printf "\nSomething was wrong with some scripts :(\n" | tee -a concurrency_$$.log
            echo "Test FAILED!!" | tee -a concurrency_$$.log
            running=0
            exit 1
        fi
    fi
    loading_counter=$((loading_counter+1))
    if [ $loading_counter -eq 4 ]; then
        loading_counter=0
    fi
    sleep .5
done
