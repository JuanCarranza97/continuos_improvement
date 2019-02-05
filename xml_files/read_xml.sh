#!/bin/bash
#This is an example about how to read xml files
xml_filename=$1
echo "Config File: $xml_filename"

# This function returns the times that a specific char appears in a string
#   example: Search how many times "<" appears in string "<concurrency>"     
#       search_symbol "<concurrency>" "<"
function search_symbol(){
    local input_string=$1
    local symbol=$2
    echo "$input_string" | grep -o "$symbol" | wc -l
}

xml_data=()
while  IFS= read -r var
do
    xml_data+=("$var")
done < "$xml_filename"
#To extract test from label"
###########echo "<name>Juan</name>" | sed -e 's/<name>\(.*\)<\/name>/\1/'
#echo "The xml file was read succesfully!!"
#echo "There are ${#xml_data[@]} lines"
i=1
if [ -n "${xml_data[$i]}" ]; then 
    open_symbol=$(search_symbol "${xml_data[$i]}" "<")
    close_symbol=$(search_symbol "${xml_data[$i]}" ">")
    if [ $open_symbol -eq $close_symbol ]; then
        echo "${xml_data[$i]}"
        echo "In line $i the symbol appears $open_symbol times"
        if [ $open_symbol -eq 1 ]; then
            label=`echo "${xml_data[$i]}" | sed -e 's/^[ \t]*//' | sed -e 's/<\(.*\)>/\1/'`
            echo "The label is $label"
            for j in $(seq $i ${#xml_data[@]});do
                if [ -n "${xml_data[$j]}" ]; then
                    appears=$(search_symbol "${xml_data[$i]}" ">")
                    if [ $appears -eq 1 ];then
                        echo "Something"
                    fi    
                fi 
            done
        elif [ $open_symbol -eq 2 ]; then
            echo "complete line"
        else
            echo "There was an error reading xml file"
        fi
    else
        echo "The number of < and > doesn't match in line $i"
    fi
else
    echo "The line $i is empty"
fi
